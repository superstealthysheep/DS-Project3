import os
from concurrent import futures
import uuid

import grpc

import kv_pb2
import kv_pb2_grpc

POD_NAME = os.environ.get("POD_NAME", "storage")
PORT = os.environ.get("PORT", "50052")
DATA = {}


class Storage(kv_pb2_grpc.StorageServiceServicer):
    def Put(self, request, context):
        item_id = str(uuid.uuid4())
        request.item_id = item_id
        DATA[item_id] = request
        print(f"{POD_NAME} PUT item {item_id}", flush=True)
        return kv_pb2.CreateItemResponse(ok=True, item_id=item_id, pod=POD_NAME)

    def Get(self, request, context):
        item = DATA.get(request.item_id)
        found = item is not None
        print(f"{POD_NAME} GET {request.item_id} found={found}", flush=True)
        return kv_pb2.GetItemResponse(found=found, item=item, pod=POD_NAME)

    def Update(self, request, context):
        if request.item_id in DATA:
            DATA[request.item_id] = request.item
            print(f"{POD_NAME} UPDATE {request.item_id}", flush=True)
            return kv_pb2.UpdateItemResponse(ok=True, new_version=request.item.version, pod=POD_NAME)
        else:
            return kv_pb2.UpdateItemResponse(ok=False, new_version=0, pod=POD_NAME)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv_pb2_grpc.add_StorageServiceServicer_to_server(Storage(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"storage {POD_NAME} listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
