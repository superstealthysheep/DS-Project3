import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
import utils.config as config
import utils.network_conventions as net_con

class ReplicaNodeServicer(p3_grpc.ReplicaNodeServiceServicer):
    # def Put(self, request, context):
    #     DATA[request.key] = request.value
    #     print(f"{CONTAINER_NAME} PUT {request.key}={request.value}", flush=True)
    #     return project3_pb2.PutResponse(ok=True, pod=CONTAINER_NAME)

    # def Get(self, request, context):
    #     value = DATA.get(request.key, "")
    #     found = request.key in DATA
    #     print(f"{CONTAINER_NAME} GET {request.key} found={found}", flush=True)
    #     return project3_pb2.GetResponse(found=found, value=value, pod=CONTAINER_NAME)
    ...

class StorageServicer(p3_grpc.StorageServiceServicer):
    ...

class Storage:
    def __init__(self):
        self.replica_node_servicer = ReplicaNodeServicer()
        self.storage_servicer = StorageServicer()

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global PORT
    global DATA

    HOSTNAME = os.environ.get("HOSTNAME", "replica-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-replica-node")
    PORT = os.environ.get("PORT", "50250")
    DATA = {}
    storage = Storage()

    print("dummy replica node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ReplicaNodeServiceServicer_to_server(storage.replica_node_servicer, server)
    p3_grpc.add_StorageServiceServicer_to_server(storage.storage_servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"storage '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

def ack_then_serve():
    # for when spawned by controller, should send an "yes, i am alive" message to controller before beginning to serve

    my_id = int(os.environ.get("REPLICA_NODE_ID"))
    assert my_id is not None and my_id in range(50), "Invalid REPLICA_NODE_ID"
    my_container_name = net_con.replica_node_name(my_id)
    controller_address = os.environ.get("CONTROLLER_ADDRESS", "p3-controller")
    controller_port = os.environ.get("CONTROLLER_PORT", "50050")
    controller_full_address = f"{controller_address}:{controller_port}"
    print(f"{controller_full_address=}")
    with grpc.insecure_channel(controller_full_address) as channel:
        stub = p3_grpc.ControllerServiceStub(channel)
        heartbeat_msg = p3.Heartbeat(node_id=my_container_name)
        stub.C_SendHeartbeat(heartbeat_msg)
    serve()

if __name__ == "__main__":
    serve()
