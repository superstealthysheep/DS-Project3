import os
from concurrent import futures
import time

import grpc

import kv_pb2
import kv_pb2_grpc

POD_NAME = os.environ.get("POD_NAME", "frontend")
PORT = os.environ.get("PORT", "50051")
STORAGE_PORT = os.environ.get("STORAGE_PORT", "50052")
STORAGE_TARGET = f"localhost:{STORAGE_PORT}"

auction_listeners = {}  # item_id -> list of queues or something, but for bare bones, simple


class Frontend(kv_pb2_grpc.FrontendServiceServicer):
    def CreateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = kv_pb2_grpc.StorageServiceStub(channel)
            response = stub.Put(request.item)
        print(f"{POD_NAME} CreateItem {response.item_id}", flush=True)
        return response

    def GetItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = kv_pb2_grpc.StorageServiceStub(channel)
            response = stub.Get(request)
        print(f"{POD_NAME} GetItem {request.item_id}", flush=True)
        return response

    def SearchItems(self, request, context):
        # For bare bones, just return all items, filter by keyword/category
        # But storage doesn't have search, so get all? Wait, storage only has Get by id.
        # For bare bones, assume we have a list or something. But to keep simple, return empty for now.
        print(f"{POD_NAME} SearchItems {request.keyword}", flush=True)
        return kv_pb2.SearchItemsResponse(items=[], pod=POD_NAME)

    def UpdateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = kv_pb2_grpc.StorageServiceStub(channel)
            response = stub.Update(request)
        print(f"{POD_NAME} UpdateItem {request.item_id}", flush=True)
        return response

    def PlaceBid(self, request, context):
        # Get current item
        get_resp = self.GetItem(kv_pb2.GetItemRequest(item_id=request.item_id), context)
        if not get_resp.found:
            return kv_pb2.PlaceBidResponse(ok=False, new_price=0, pod=POD_NAME)
        item = get_resp.item
        if request.bid_amount > item.current_price:
            item.current_price = request.bid_amount
            item.version += 1
            update_req = kv_pb2.UpdateItemRequest(item_id=request.item_id, item=item)
            update_resp = self.UpdateItem(update_req, context)
            if update_resp.ok:
                # Notify listeners
                if request.item_id in auction_listeners:
                    for queue in auction_listeners[request.item_id]:
                        queue.put(kv_pb2.AuctionUpdate(
                            item_id=request.item_id,
                            current_price=item.current_price,
                            bidder_id=request.bidder_id,
                            status="active",
                            timestamp=int(time.time())
                        ))
                return kv_pb2.PlaceBidResponse(ok=True, new_price=item.current_price, pod=POD_NAME)
        return kv_pb2.PlaceBidResponse(ok=False, new_price=item.current_price, pod=POD_NAME)

    def JoinAuction(self, request, context):
        # For streaming, yield updates
        # Bare bones: just yield initial, and wait for bids
        # But to keep simple, yield nothing for now.
        print(f"{POD_NAME} JoinAuction {request.item_id}", flush=True)
        # For bare bones, just return empty stream
        return


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv_pb2_grpc.add_FrontendServiceServicer_to_server(Frontend(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"frontend {POD_NAME} listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()


if __name__ == "__main__":
    serve()
