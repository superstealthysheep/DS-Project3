from __future__ import annotations
import typing
import time

import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
import utils.config as config
import utils.network_conventions as net_con


def clone_item(src: p3.Item) -> p3.Item:
    dst = p3.Item()
    dst.CopyFrom(src)
    return dst


class ServiceNodeServicer(p3_grpc.ServiceNodeServiceServicer):
    def __init__(self, service_node: ServiceNode):
        assert service_node is not None
        self.service_node = service_node

    def CreateItem(self, request: p3.CreateItemRequest, context) -> p3.CreateItemResponse:
        return self.service_node.quorum_put(request.item, pod=CONTAINER_NAME)

    def GetItem(self, request, context):
        return self.service_node.quorum_get(request.item_id, pod=CONTAINER_NAME)

    def SearchItems(self, request, context):
        return p3.SearchItemsResponse(items=[], pod=CONTAINER_NAME)

    def UpdateItem(self, request, context):
        return self.service_node.quorum_update(request, pod=CONTAINER_NAME)

    def PlaceBid(self, request, context):
        get_resp = self.service_node.quorum_get(request.item_id, pod=CONTAINER_NAME)
        if not get_resp.found:
            return p3.PlaceBidResponse(ok=False, new_price=0, pod=CONTAINER_NAME)

        item = get_resp.item
        if request.bid_amount <= item.current_price:
            return p3.PlaceBidResponse(ok=False, new_price=item.current_price, pod=CONTAINER_NAME)

        item.current_price = int(request.bid_amount)
        upd = p3.UpdateItemRequest(item_id=request.item_id, prev_version=item.version, new_value=item)
        upd_resp = self.service_node.quorum_update(upd, pod=CONTAINER_NAME)
        if not upd_resp.ok:
            return p3.PlaceBidResponse(ok=False, new_price=item.current_price, pod=CONTAINER_NAME)

        return p3.PlaceBidResponse(ok=True, new_price=item.current_price, pod=CONTAINER_NAME)

    def JoinAuction(self, request, context):
        print(f"'{CONTAINER_NAME}' JoinAuction {request.item_id}", flush=True)
        return

class ServiceNode:
    def __init__(self):
        self.servicer = ServiceNodeServicer(self)
        self.auction_listeners = {}

    def all_replica_targets(self) -> list[str]:
        return [
            f"{net_con.replica_node_name(i)}:{net_con.replica_node_port(i)}"
            for i in range(config.N_REPLICAS)
        ]

    def quorum_put(self, item: p3.Item, pod: str) -> p3.CreateItemResponse:
        it = clone_item(item)
        it.version = "0"

        deadline = time.time() + 10.0
        acks = 0
        while time.time() < deadline:
            acks = 0
            for target in self.all_replica_targets():
                try:
                    with grpc.insecure_channel(target) as channel:
                        stub = p3_grpc.StorageServiceStub(channel)
                        resp = stub.Put(it, timeout=config.STORAGE_REQUEST_TIMEOUT)
                    if resp.ok:
                        acks += 1
                except grpc.RpcError:
                    pass

            if acks >= config.WRITE_QUORUM_SIZE:
                break
            time.sleep(0.5)

        ok = acks >= config.WRITE_QUORUM_SIZE
        return p3.CreateItemResponse(ok=ok, item_id=it.item_id, new_version="0" if ok else "", pod=pod)

    def quorum_get(self, item_id: str, pod: str) -> p3.GetItemResponse:
        deadline = time.time() + 10.0
        responses = 0
        found_items: list[p3.Item] = []
        while time.time() < deadline:
            responses = 0
            found_items = []
            for target in self.all_replica_targets():
                try:
                    with grpc.insecure_channel(target) as channel:
                        stub = p3_grpc.StorageServiceStub(channel)
                        resp = stub.Get(p3.GetItemRequest(item_id=item_id), timeout=config.STORAGE_REQUEST_TIMEOUT)
                    responses += 1
                    if resp.found:
                        found_items.append(resp.item)
                except grpc.RpcError:
                    pass

            if responses >= config.READ_QUORUM_SIZE:
                break
            time.sleep(0.5)

        if responses < config.READ_QUORUM_SIZE:
            return p3.GetItemResponse(found=False, pod=pod)

        if len(found_items) == 0:
            return p3.GetItemResponse(found=False, pod=pod)

        best = max(found_items, key=lambda x: int(x.version) if x.version.isdigit() else -1)
        return p3.GetItemResponse(found=True, item=best, pod=pod)

    def quorum_update(self, req: p3.UpdateItemRequest, pod: str) -> p3.UpdateItemResponse:
        get_resp = self.quorum_get(req.item_id, pod=pod)
        if not get_resp.found:
            return p3.UpdateItemResponse(ok=False, pod=pod)

        latest = get_resp.item
        if req.prev_version != latest.version:
            return p3.UpdateItemResponse(ok=False, pod=pod)

        latest_v = int(latest.version) if latest.version.isdigit() else -1
        if latest_v < 0:
            return p3.UpdateItemResponse(ok=False, pod=pod)

        new_v = latest_v + 1
        new_item = clone_item(req.new_value)
        new_item.version = str(new_v)
        cas_req = p3.UpdateItemRequest(item_id=req.item_id, prev_version=str(latest_v), new_value=new_item)

        deadline = time.time() + 10.0
        acks = 0
        while time.time() < deadline:
            acks = 0
            for target in self.all_replica_targets():
                try:
                    with grpc.insecure_channel(target) as channel:
                        stub = p3_grpc.StorageServiceStub(channel)
                        resp = stub.Update(cas_req, timeout=config.STORAGE_REQUEST_TIMEOUT)
                    if resp.ok:
                        acks += 1
                except grpc.RpcError:
                    pass

            if acks >= config.WRITE_QUORUM_SIZE:
                break
            time.sleep(0.5)

        ok = acks >= config.WRITE_QUORUM_SIZE
        return p3.UpdateItemResponse(ok=ok, new_version=str(new_v) if ok else "", pod=pod)

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global PORT

    HOSTNAME = os.environ.get("HOSTNAME", "service-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-service-node")
    PORT = os.environ.get("PORT", "50150")

    service_node = ServiceNode()
    print("dummy service node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ServiceNodeServiceServicer_to_server(service_node.servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"Service node '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

def ack_then_serve():
    my_id = int(os.environ.get("SERVICE_NODE_ID"))
    assert my_id is not None and my_id in range(50)
    my_container_name = net_con.service_node_name(my_id)
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