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


class ServiceNodeServicer(p3_grpc.ServiceNodeServiceServicer):
    def __init__(self, service_node: ServiceNode):
        assert service_node is not None
        self.service_node = service_node

    # def CreateItem(self, request: p3.CreateItemRequest, context: grpc.ServicerContext) -> p3.CreateItemResponse:
    #     return p3.CreateItemResponse(
    #         success=False,
    #         item=None,
    #     )

    # def GetItem(self, request: p3.GetItemRequest, context: grpc.ServicerContext) -> p3.GetItemResponse:
    #     return p3.GetItemResponse(
    #         success=False,
    #         item=None,
    #     )

    def CreateItem(self, request: p3.CreateItemRequest, context) -> p3.CreateItemResponse:
        i = 0
        def handler(self, request, context, target):
            nonlocal i
            i += 1
            with grpc.insecure_channel(target) as channel:
                stub = p3_grpc.StorageServiceStub(channel)
                response = stub.Put(request.item, timeout=config.STORAGE_REQUEST_TIMEOUT)
            print(f"'{CONTAINER_NAME}' CreateItem {response.item_id}", flush=True)
            return response

        response = self.service_node.retry_wrapper(handler, self, request, context)
        if response is None: 
            response = p3.CreateItemResponse(ok=False)
        return response

    def GetItem(self, request, context):
        def handler(self, request, context, target):
            with grpc.insecure_channel(target) as channel:
                stub = p3_grpc.StorageServiceStub(channel)
                response = stub.Get(request, timeout=config.STORAGE_REQUEST_TIMEOUT)
            print(f"'{CONTAINER_NAME}' GetItem {request.item_id}", flush=True)
            return response

        response = self.service_node.retry_wrapper(handler, self, request, context)
        if response is None: 
            response = p3.GetItemResponse(ok=False)
        return response

    def SearchItems(self, request, context):
        def handler(self, request, context, target):
            # For bare bones, just return all items, filter by keyword/category
            # But storage doesn't have search, so get all? Wait, storage only has Get by id.
            # For bare bones, assume we have a list or something. But to keep simple, return empty for now.
            print(f"'{CONTAINER_NAME}' SearchItems {request.keyword}", flush=True)
            return p3.SearchItemsResponse(items=[], pod=CONTAINER_NAME)

        response = self.service_node.retry_wrapper(handler, self, request, context)
        if response is None: 
            response = p3.SearchItemsResponse(ok=False)
        return response

    def UpdateItem(self, request, context):
        def handler(self, request, context, target):
            with grpc.insecure_channel(target) as channel:
                stub = p3_grpc.StorageServiceStub(channel)
                response = stub.Update(request)
            print(f"'{CONTAINER_NAME}' UpdateItem {request.item_id}", flush=True)
            return response

        response = self.service_node.retry_wrapper(handler, self, request, context)
        if response is None: 
            response = p3.GetItemResponse(ok=False)
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
                if request.item_id in self.service_node.auction_listeners:
                    for queue in self.service_node.auction_listeners[request.item_id]:
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

class ServiceNode:
    def __init__(self):
        self.servicer = ServiceNodeServicer(self)
        self.auction_listeners = {}

    def get_replica_node_full_address(self, rn_id: int):
        # could be more complex for more complex networks,
        # but here it suffices to just do
        full_address = f"{net_con.replica_node_name(rn_id)}:{net_con.replica_node_port(rn_id)}"
        return full_address

    def choose_replica_node(self) -> str:
        import random
        rn_id = random.randrange(config.N_REPLICAS)
        full_address = self.get_replica_node_full_address(rn_id)
        return full_address

    # def retry_iterator(self, max_retries, retry_period=1) -> typing.Iterator[str]:
    #     for _ in range(max_retries):
    #         yield self.choose_replica_node()
    #         time.sleep(retry_period)

    def retry_wrapper(self, handler, servicer, request, context, max_retries=5, retry_period=1):
        """ returns None on failure, else returns wha handler did """
        for i in range(max_retries):
            target = self.choose_replica_node()           

            try:
                response = handler(servicer, request, context, target)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE or e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    pass
                else:
                    raise e
            else:
                return response

            if i != max_retries - 1: time.sleep(retry_period)
        return None

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
    p3_grpc.add_ServiceNodeServiceServicer_to_server(service_node.servicer, server) # heeheeheehah
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"Service node '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

def ack_then_serve():
    # for when spawned by controller, should send an "yes, i am alive" message to controller before beginning to serve

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
