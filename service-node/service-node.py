import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
import utils.config as config
import utils.network_conventions as net_con


class ServiceNode(p3_grpc.ServiceNodeServiceServicer):
    def S_CreateItem(self, request: p3.CreateItemRequest, context: grpc.ServicerContext) -> p3.CreateItemResponse:
        return p3.CreateItemResponse(
            success=False,
            item=None,
        )

    def S_GetItem(self, request: p3.GetItemRequest, context: grpc.ServicerContext) -> p3.GetItemResponse:
        return p3.GetItemResponse(
            success=False,
            item=None,
        )

    def S_CreateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Put(request.item)
        print(f"'{CONTAINER_NAME}' CreateItem {response.item_id}", flush=True)
        return response

    def S_GetItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Get(request)
        print(f"'{CONTAINER_NAME}' GetItem {request.item_id}", flush=True)
        return response

    def S_SearchItems(self, request, context):
        # For bare bones, just return all items, filter by keyword/category
        # But storage doesn't have search, so get all? Wait, storage only has Get by id.
        # For bare bones, assume we have a list or something. But to keep simple, return empty for now.
        print(f"'{CONTAINER_NAME}' SearchItems {request.keyword}", flush=True)
        return p3.SearchItemsResponse(items=[], pod=CONTAINER_NAME)

    def S_UpdateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Update(request)
        print(f"'{CONTAINER_NAME}' UpdateItem {request.item_id}", flush=True)
        return response

    def S_PlaceBid(self, request, context):
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

    def S_JoinAuction(self, request, context):
        # For streaming, yield updates
        # Bare bones: just yield initial, and wait for bids
        # But to keep simple, yield nothing for now.
        print(f"'{CONTAINER_NAME}' JoinAuction {request.item_id}", flush=True)
        # For bare bones, just return empty stream
        return

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global PORT
    global DATA

    HOSTNAME = os.environ.get("HOSTNAME", "service-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-service-node")
    PORT = os.environ.get("PORT", "50150")
    DATA = {}

    print("dummy service node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ServiceNodeServiceServicer_to_server(ServiceNode(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"Service node '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

def ack_then_serve():
    # for when spawned by controller, should send an "yes, i am alive" message to controller before beginning to serve

    my_id = int(os.environ.get("SERVICE_NODE_ID", "-1"))
    my_container_name = net_con.service_node_name(my_id)
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
