import argparse
import subprocess
import time
import google.protobuf

import grpc
import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

import os
from concurrent import futures

import docker
import utils.config as config
import utils.network_conventions as net_con

def run_cmd(cmd, check=True, verbose=True):
    if verbose: print(" ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if verbose:
        print(res.stderr)
        print(res.stdout)
    return res


def network_exists(network):
    result = run_cmd(
        ["docker", "network", "ls", "--format", "{{.Name}}"],
        check=False,
    )
    return network in result.stdout.splitlines()


def ensure_network(network):
    if not network_exists(network):
        run_cmd(["docker", "network", "create", network])
        print(f"created network: {network}", flush=True)


def container_running(name):
    result = run_cmd(
        [
            "docker",
            "ps",
            "--filter",
            f"name=^{name}$",
            "--filter",
            "status=running",
            "--format",
            "{{.Names}}",
        ],
        check=False,
    )
    return name in result.stdout.splitlines()


def remove_container(name):
    run_cmd(["docker", "rm", "-f", name], check=False)


def start_replica(name, image, network, container_port, host_port):
    remove_container(name)
    run_cmd(
        [
            "docker",
            "run",
            "-d",
            "--name",
            name,
            "--network",
            network,
            "-p",
            f"{host_port}:{container_port}",
            "-e",
            f"POD_NAME={name}",
            "-e",
            f"PORT={container_port}",
            image,
        ]
    )
    print(f"started {name} on localhost:{host_port}", flush=True)


def grpc_healthy(host_port, timeout_sec):
    target = f"localhost:{host_port}"
    channel = grpc.insecure_channel(target)
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout_sec)
        return True
    except Exception:
        return False
    finally:
        channel.close()

def running_service_nodes():
    dc: docker.DockerClient = docker.from_env()
    names = []
    for container in dc.containers.list(filters={
        'name': "^p3-service-node-",
    }):
        names.append(container.name)
    return sorted(names)

def running_replica_nodes():
    dc: docker.DockerClient = docker.from_env()
    names = []
    for container in dc.containers.list(filters={
        'name': "^p3-replica-node-",
    }):
        names.append(container.name)
    return sorted(names)

class ControllerServicer(p3_grpc.ControllerServiceServicer):
    def C_CreateItem(self, request: p3.CreateItemRequest, context: grpc.ServicerContext) -> p3.CreateItemResponse:
        return p3.CreateItemResponse(
            success=False,
            item=None,
        )

    def C_GetItem(self, request: p3.GetItemRequest, context: grpc.ServicerContext) -> p3.GetItemResponse:
        return p3.GetItemResponse(
            success=False,
            item=None,
        )

    def C_SendHeartbeat(self, request: p3.Heartbeat, context: grpc.ServicerContext):
        container_name = request.node_id
        self.controller.heartbeat_callback(container_name)
        return google.protobuf.empty_pb2.Empty()

class FrontendServicer(p3_grpc.FrontendServiceServicer):
    global HOSTNAME
    global CONTAINER_NAME
    global STORAGE_TARGET
    global auction_listeners

    def CreateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Put(request.item)
        print(f"'{CONTAINER_NAME}' CreateItem {response.item_id}", flush=True)
        return response

    def GetItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Get(request)
        print(f"'{CONTAINER_NAME}' GetItem {request.item_id}", flush=True)
        return response

    def SearchItems(self, request, context):
        # For bare bones, just return all items, filter by keyword/category
        # But storage doesn't have search, so get all? Wait, storage only has Get by id.
        # For bare bones, assume we have a list or something. But to keep simple, return empty for now.
        print(f"'{CONTAINER_NAME}' SearchItems {request.keyword}", flush=True)
        return p3.SearchItemsResponse(items=[], pod=CONTAINER_NAME)

    def UpdateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Update(request)
        print(f"'{CONTAINER_NAME}' UpdateItem {request.item_id}", flush=True)
        return response

    def PlaceBid(self, request, context):
        # Get current item
        get_resp = self.GetItem(p3.GetItemRequest(item_id=request.item_id), context)
        if not get_resp.found:
            return p3.PlaceBidResponse(ok=False, new_price=0, pod=CONTAINER_NAME)
        item = get_resp.item
        if request.bid_amount > item.current_price:
            item.current_price = request.bid_amount
            item.version += 1
            update_req = p3.UpdateItemRequest(item_id=request.item_id, item=item)
            update_resp = self.UpdateItem(update_req, context)
            if update_resp.ok:
                # Notify listeners
                if request.item_id in auction_listeners:
                    for queue in auction_listeners[request.item_id]:
                        queue.put(p3.AuctionUpdate(
                            item_id=request.item_id,
                            current_price=item.current_price,
                            bidder_id=request.bidder_id,
                            status="active",
                            timestamp=int(time.time())
                        ))
                return p3.PlaceBidResponse(ok=True, new_price=item.current_price, pod=CONTAINER_NAME)
        return p3.PlaceBidResponse(ok=False, new_price=item.current_price, pod=CONTAINER_NAME)

    def JoinAuction(self, request, context):
        # For streaming, yield updates
        # Bare bones: just yield initial, and wait for bids
        # But to keep simple, yield nothing for now.
        print(f"'{CONTAINER_NAME}' JoinAuction {request.item_id}", flush=True)
        # For bare bones, just return empty stream
        return

class Controller:
    def __init__(self):
        self.service_nodes = {} # dict mapping 'id' -> dict with keys {'address', 'port', 'busy'}
        self.replica_nodes = {} # dict mapping 'id' -> dict with keys {'address', 'port', 'busy'}
        self.docker_client: docker.DockerClient = docker.from_env()
        self.service_node_image = "project3_service_node:latest"
        self.replica_node_image = "project3_replica_node:latest"
        self.container_name = "p3-controller"
        self.n_replicas = 5

        self.controller_servicer = ControllerServicer()
        self.controller_servicer.controller = self
        self.frontend_servicer = FrontendServicer()
        self.frontend_servicer.controller = self

    def spawn_service_node(self, id: int):
        assert id not in self.service_nodes
        assert id in range(50)
        container_name = net_con.service_node_name(id)
        port = net_con.service_node_port(id)
        self.docker_client.containers.run(
            image=self.service_node_image,
            detach=True,
            name=container_name,
            ports={"80": port},
            network=config.NETWORK,
            environment={
                "SERVICE_NODE_ID": str(id),
                "CONTROLLER_ADDRESSS": self.container_name,
                "CONTROLLER_PORT": 50050,
                # "CONTROLLER_PORT": str(80),
            },
            labels={
                "com.docker.compose.project": config.COMPOSE_PROJECT_NAME,
                "com.docker.compose.service": container_name
            },
            command=["python", "-u", "service-node/ack_then_serve.py"],
        )
        self.service_nodes[id] = {
            'address': container_name,
            # 'port': 80,
            'port': port, # or is it 80?
            'status': "spawning"
        }
        print(f"{self.service_nodes[id]=}")

    def stop_service_node(self, id: int):
        assert id in self.service_nodes
        if self.service_nodes[id]['status'] == "busy":
            raise NotImplementedError("Must handle trying to stop busy container. Maybe just return fail?")
        container_info = self.service_nodes.pop(id)
        
        container = self.docker_client.containers.get(
            net_con.service_node_name(id)
        )
        container.stop()

    def spawn_replica_node(self, id: int):
        assert id not in self.replica_nodes
        assert id in range(50)
        container_name = net_con.replica_node_name(id)
        print(f"{container_name=}")
        port = net_con.replica_node_port(id)
        self.docker_client.containers.run(
            image=self.replica_node_image,
            detach=True,
            name=container_name,
            ports={"80": port},
            network=config.NETWORK,
            environment={
                "REPLICA_NODE_ID": str(id),
                "CONTROLLER_ADDRESSS": self.container_name,
                "CONTROLLER_PORT": 50050,
            },
            labels={
                "com.docker.compose.project": config.COMPOSE_PROJECT_NAME,
                "com.docker.compose.service": container_name
            },
            command=["python", "-u", "replica-node/ack_then_serve.py"],
        )
        self.replica_nodes[id] = {
            'address': container_name,
            'port': port,
            'status': "spawning"
        }
        print(f"{self.replica_nodes[id]=}")

    def stop_replica_node(self, id: int):
        assert id in self.replica_nodes
        if self.replica_nodes[id]['status'] == "busy":
            raise NotImplementedError("Must handle trying to stop busy container. Maybe just return fail?")
        container_info = self.replica_nodes.pop(id)
        
        container = self.docker_client.containers.get(
            net_con.replica_node_name(id)
        )
        container.stop()

    def heartbeat_callback(self, sender_container_id):
        """ only purpose is to receive heartbeats from service/replica nodes when they have fully spawned """
        if sender_container_id.startswith(net_con.SERVICE_NODE_PREFIX):
            collection = self.service_nodes
            sender_id = sender_container_id[len(net_con.SERVICE_NODE_PREFIX):]
        elif sender_container_id.startswith(net_con.REPLICA_NODE_PREFIX):
            collection = self.replica_nodes
            sender_id = sender_container_id[len(net_con.REPLICA_NODE_PREFIX):]
        else:
            collection = None

        if collection is not None:
            sender_id = int(sender_id)
            if collection[sender_id]['status'] == "spawning":
                collection[sender_id]['status'] = "ready"

    def autoscaling_policy(self, desired_n_ready=1):
        """ tries to ensure that there is one ready (or spawning) container at all times """
        n_ready = sum(sn['status'] in {'ready', 'spawning'} for sn in self.service_nodes)
        disparity = n_ready - desired_n_ready

        # scale up
        id = 0
        while disparity < 0 and id in range(50):
            if disparity < 0 and id not in self.service_nodes:
                self.spawn_service_node(id)
                disparity += 1
            id += 1

        # scale down
        for id,service_node in self.service_nodes.items():
            if not disparity > 0: break
            if service_node['status'] == 'ready':
                self.stop_service_node(id)
                disparity -= 1

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global STORAGE_PORT
    global STORAGE_TARGET
    global PORT
    global DATA
    global auction_listeners

    HOSTNAME = os.environ.get("HOSTNAME", "controller-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-controller-node")
    PORT = os.environ.get("PORT", "50050")
    DATA = {}
    SERVICE_PORT = os.environ.get("SERVICE_PORT", "50150")
    STORAGE_PORT = os.environ.get("STORAGE_PORT", "50250")
    STORAGE_TARGET = f"{net_con.replica_node_name(id=0)}:{STORAGE_PORT}"
    auction_listeners = {}

    print("dummy controller")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    controller = Controller()
    p3_grpc.add_ControllerServiceServicer_to_server(controller.controller_servicer, server)
    p3_grpc.add_FrontendServiceServicer_to_server(controller.frontend_servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"Controller '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    print(f"Frontend '{CONTAINER_NAME}' listening on {PORT}", flush=True)

    for i in range(controller.n_replicas):
        print(f"Attempting to spawn replica node {i}")
        controller.spawn_replica_node(i)

    controller.autoscaling_policy() # TODO: call this intermittently?
    
    import time
    time.sleep(15)
    print(running_service_nodes())
    for i in range(5):
        controller.stop_service_node(i)
    time.sleep(5)

    server.wait_for_termination()

    # ensure_network(args.network)

    # for i in range(args.replicas):
    #     name = replica_name(i)
    #     host_port = args.host_port_base + i
    #     if not container_running(name):
    #         start_replica(name, args.image, args.network, args.port, host_port)

    # print("controller is running", flush=True)

    # while True:
    #     for i in range(args.replicas):
    #         name = replica_name(i)
    #         host_port = args.host_port_base + i

    #         if not container_running(name):
    #             print(f"{name} is down (container not running), restarting", flush=True)
    #             start_replica(name, args.image, args.network, args.port, host_port)
    #             continue

    #         if not grpc_healthy(host_port, args.timeout):
    #             print(f"{name} is down (grpc timeout), replacing", flush=True)
    #             start_replica(name, args.image, args.network, args.port, host_port)

    #     print(f"active replicas: {running_storage_replicas()}", flush=True)
    #     time.sleep(args.interval)


if __name__ == "__main__":
    serve()
