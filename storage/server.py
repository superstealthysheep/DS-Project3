import os
from concurrent import futures

import grpc

import kv_pb2
import kv_pb2_grpc

POD_NAME = os.environ.get("POD_NAME", "storage")
PORT = os.environ.get("PORT", "50052")
DATA = {}


class Storage(kv_pb2_grpc.StorageServiceServicer):
    def Put(self, request, context):
        DATA[request.key] = request.value
        print(f"{POD_NAME} PUT {request.key}={request.value}", flush=True)
        return kv_pb2.PutResponse(ok=True, pod=POD_NAME)

    def Get(self, request, context):
        value = DATA.get(request.key, "")
        found = request.key in DATA
        print(f"{POD_NAME} GET {request.key} found={found}", flush=True)
        return kv_pb2.GetResponse(found=found, value=value, pod=POD_NAME)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv_pb2_grpc.add_StorageServiceServicer_to_server(Storage(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"storage {POD_NAME} listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
