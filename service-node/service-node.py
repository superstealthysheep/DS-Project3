import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

HOSTNAME = os.environ.get("HOSTNAME", "service-node")
PORT = os.environ.get("PORT", "50051")
DATA = {}


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

def serve():
    print("dummy service node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ServiceNodeServiceServicer_to_server(ServiceNode(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"Service node '{HOSTNAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
