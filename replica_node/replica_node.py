from __future__ import annotations

import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
import utils.config as config
import utils.network_conventions as net_con

import threading

STORE_LOCK = threading.RLock()

def clone_item(src: p3.Item) -> p3.Item:
    dst = p3.Item()
    dst.CopyFrom(src)
    return dst

class ReplicaNodeServicer(p3_grpc.ReplicaNodeServiceServicer):
    def __init__(self, replica_node: ReplicaNode):
        assert replica_node is not None
        self.replica_node : ReplicaNode = replica_node

    def R_Put(self, request: p3.CreateItemRequest, context):
        return self.replica_node.put_item(request.item, pod=CONTAINER_NAME)

    def R_Get(self, request: p3.GetItemRequest, context):
        return self.replica_node.get_item(request.item_id, pod=CONTAINER_NAME)

    def R_Update(self, request: p3.UpdateItemRequest, context):
        return self.replica_node.update_item(request, pod=CONTAINER_NAME)

class StorageServicer(p3_grpc.StorageServiceServicer):
    def __init__(self, replica_node: ReplicaNode):
        assert replica_node is not None
        self.replica_node : ReplicaNode = replica_node

    def Put(self, request, context):
        return self.replica_node.put_item(request, pod=CONTAINER_NAME)

    def Get(self, request, context):
        return self.replica_node.get_item(request.item_id, pod=CONTAINER_NAME)

    def Update(self, request, context):
        return self.replica_node.update_item(request, pod=CONTAINER_NAME)

    # def HeartbeatRequest(self, request, context):
    #     ...
    #     # value = DATA.get(request.key, "")
    #     # found = request.key in DATA
    #     # print(f"{CONTAINER_NAME} GET {request.key} found={found}", flush=True)
    #     # return p3.GetResponse(found=found, value=value, pod=CONTAINER_NAME)
    

class ReplicaNode:
    """ holds all the core data/logic. the two other classes are just thing layers for handling RPCs """
    def __init__(self):
        self.replica_node_servicer = ReplicaNodeServicer(replica_node=self)
        self.storage_servicer = StorageServicer(replica_node=self)
        # item_id -> {"item": Item, "version": int}
        self.data = {}

    def put_item(self, item: p3.Item, pod: str) -> p3.CreateItemResponse:
        with STORE_LOCK:
            if item.item_id in self.data:
                return p3.CreateItemResponse(ok=False, item_id=item.item_id, pod=pod)

            stored = clone_item(item)
            stored.version = "0"
            self.data[item.item_id] = {"item": stored, "version": 0}
            return p3.CreateItemResponse(ok=True, item_id=item.item_id, new_version="0", pod=pod)

    def get_item(self, item_id: str, pod: str) -> p3.GetItemResponse:
        with STORE_LOCK:
            entry = self.data.get(item_id)
            if entry is None:
                return p3.GetItemResponse(ok=True, found=False, pod=pod)

            item = clone_item(entry["item"])
            item.version = str(entry["version"])
            return p3.GetItemResponse(ok=True, found=True, item=item, pod=pod)

    def update_item(self, req: p3.UpdateItemRequest, pod: str) -> p3.UpdateItemResponse:
        with STORE_LOCK:
            entry = self.data.get(req.item_id)
            if entry is None:
                return p3.UpdateItemResponse(ok=False, pod=pod)

            cur_v = entry["version"]
            if req.prev_version != str(cur_v):
                return p3.UpdateItemResponse(ok=False, pod=pod)

            new_v = cur_v + 1
            new_item = clone_item(req.new_value)
            new_item.version = str(new_v)
            self.data[req.item_id] = {"item": new_item, "version": new_v}
            return p3.UpdateItemResponse(ok=True, new_version=str(new_v), pod=pod)

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global PORT
    global DATA

    HOSTNAME = os.environ.get("HOSTNAME", "replica-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-replica-node")
    PORT = os.environ.get("PORT", str(net_con.REPLICA_NODE_BASE_PORT))
    replica = ReplicaNode()

    print("dummy replica node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ReplicaNodeServiceServicer_to_server(replica.replica_node_servicer, server)
    p3_grpc.add_StorageServiceServicer_to_server(replica.storage_servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"storage '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

def ack_then_serve():
    # for when spawned by controller, should send an "yes, i am alive" message to controller before beginning to serve

    my_id = int(os.environ.get("REPLICA_NODE_ID"))
    assert my_id is not None and my_id in range(50), "Invalid REPLICA_NODE_ID"
    my_container_name = net_con.replica_node_name(my_id)

    controller_address = os.environ.get("CONTROLLER_ADDRESS", net_con.CONTROLLER_NODE_NAME)
    controller_port = os.environ.get("CONTROLLER_PORT", str(net_con.CONTROLLER_NODE_BASE_PORT))
    controller_full_address = f"{controller_address}:{controller_port}"
    print(f"{controller_full_address=}")

    with grpc.insecure_channel(controller_full_address) as channel:
        stub = p3_grpc.ControllerServiceStub(channel)
        heartbeat_msg = p3.Heartbeat(node_id=my_container_name)
        stub.C_SendHeartbeat(heartbeat_msg)
    serve()

if __name__ == "__main__":
    serve()
