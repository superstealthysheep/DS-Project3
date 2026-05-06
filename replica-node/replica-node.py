import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

HOSTNAME = os.environ.get("HOSTNAME", "replica-node")
PORT = os.environ.get("PORT", "50052")
DATA = {}


class ReplicaNode(p3_grpc.ReplicaNodeServiceServicer):
    # def Put(self, request, context):
    #     DATA[request.key] = request.value
    #     print(f"{HOSTNAME} PUT {request.key}={request.value}", flush=True)
    #     return project3_pb2.PutResponse(ok=True, pod=HOSTNAME)

    # def Get(self, request, context):
    #     value = DATA.get(request.key, "")
    #     found = request.key in DATA
    #     print(f"{HOSTNAME} GET {request.key} found={found}", flush=True)
    #     return project3_pb2.GetResponse(found=found, value=value, pod=HOSTNAME)
    ...


def serve():
    print("dummy replica node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ReplicaNodeServiceServicer_to_server(ReplicaNode(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"storage {HOSTNAME} listening on {PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
