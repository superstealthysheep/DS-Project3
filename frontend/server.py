import os
from concurrent import futures
import time

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

HOSTNAME = os.environ.get("HOSTNAME", "frontend")
PORT = os.environ.get("PORT", "50051")
STORAGE_PORT = os.environ.get("STORAGE_PORT", "50052")
STORAGE_TARGET = f"localhost:{STORAGE_PORT}"

auction_listeners = {}  # item_id -> list of queues or something, but for bare bones, simple


class Frontend(p3_grpc.FrontendServiceServicer):
    def CreateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Put(request.item)
        print(f"'{HOSTNAME}' CreateItem {response.item_id}", flush=True)
        return response

    def GetItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Get(request)
        print(f"'{HOSTNAME}' GetItem {request.item_id}", flush=True)
        return response

    def SearchItems(self, request, context):
        # For bare bones, just return all items, filter by keyword/category
        # But storage doesn't have search, so get all? Wait, storage only has Get by id.
        # For bare bones, assume we have a list or something. But to keep simple, return empty for now.
        print(f"'{HOSTNAME}' SearchItems {request.keyword}", flush=True)
        return p3.SearchItemsResponse(items=[], pod=HOSTNAME)

    def UpdateItem(self, request, context):
        with grpc.insecure_channel(STORAGE_TARGET) as channel:
            stub = p3_grpc.StorageServiceStub(channel)
            response = stub.Update(request)
        print(f"'{HOSTNAME}' UpdateItem {request.item_id}", flush=True)
        return response

    def PlaceBid(self, request, context):
        # Get current item
        get_resp = self.GetItem(p3.GetItemRequest(item_id=request.item_id), context)
        if not get_resp.found:
            return p3.PlaceBidResponse(ok=False, new_price=0, pod=HOSTNAME)
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
                return p3.PlaceBidResponse(ok=True, new_price=item.current_price, pod=HOSTNAME)
        return p3.PlaceBidResponse(ok=False, new_price=item.current_price, pod=HOSTNAME)

    def JoinAuction(self, request, context):
        # For streaming, yield updates
        # Bare bones: just yield initial, and wait for bids
        # But to keep simple, yield nothing for now.
        print(f"'{HOSTNAME}' JoinAuction {request.item_id}", flush=True)
        # For bare bones, just return empty stream
        return


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_FrontendServiceServicer_to_server(Frontend(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    # server.add_insecure_port(f"localhost:{PORT}")
    server.start()
    print(f"frontend '{HOSTNAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()


if __name__ == "__main__":
    serve()
