import hashlib
import os
from concurrent import futures

import grpc

import kv_pb2
import kv_pb2_grpc

POD_NAME = os.environ.get("POD_NAME", "frontend")
PORT = os.environ.get("PORT", "50051")
STORAGE_PORT = os.environ.get("STORAGE_PORT", "50052")
STORAGE_TARGETS = [
    f"storage-0.storage:{STORAGE_PORT}",
    f"storage-1.storage:{STORAGE_PORT}",
]


def storage_target(key: str) -> str:
    n = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return STORAGE_TARGETS[n % len(STORAGE_TARGETS)]


class Frontend(kv_pb2_grpc.FrontendServiceServicer):
    def Put(self, request, context):
        target = storage_target(request.key)
        with grpc.insecure_channel(target) as channel:
            stub = kv_pb2_grpc.StorageServiceStub(channel)
            response = stub.Put(kv_pb2.PutRequest(key=request.key, value=request.value))
        print(f"{POD_NAME} PUT {request.key} -> {target}", flush=True)
        return kv_pb2.PutResponse(ok=response.ok, pod=POD_NAME)

    def Get(self, request, context):
        target = storage_target(request.key)
        with grpc.insecure_channel(target) as channel:
            stub = kv_pb2_grpc.StorageServiceStub(channel)
            response = stub.Get(kv_pb2.GetRequest(key=request.key))
        print(f"{POD_NAME} GET {request.key} -> {target}", flush=True)
        return kv_pb2.GetResponse(found=response.found, value=response.value, pod=POD_NAME)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv_pb2_grpc.add_FrontendServiceServicer_to_server(Frontend(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"frontend {POD_NAME} listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
