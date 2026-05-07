import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
import utils.config as config
import utils.network_conventions as net_con

class ReplicaNode(p3_grpc.ReplicaNodeServiceServicer):
    # def Put(self, request, context):
    #     DATA[request.key] = request.value
    #     print(f"{CONTAINER_NAME} PUT {request.key}={request.value}", flush=True)
    #     return project3_pb2.PutResponse(ok=True, pod=CONTAINER_NAME)

    # def Get(self, request, context):
    #     value = DATA.get(request.key, "")
    #     found = request.key in DATA
    #     print(f"{CONTAINER_NAME} GET {request.key} found={found}", flush=True)
    #     return project3_pb2.GetResponse(found=found, value=value, pod=CONTAINER_NAME)
    ...

class Storage(p3_grpc.StorageServiceServicer):
    ...

def serve():
    global HOSTNAME
    global CONTAINER_NAME
    global PORT
    global DATA

    HOSTNAME = os.environ.get("HOSTNAME", "replica-node")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "p3-replica-node")
    PORT = os.environ.get("PORT", "50250")
    DATA = {}

    print("dummy replica node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ReplicaNodeServiceServicer_to_server(ReplicaNode(), server)
    p3_grpc.add_StorageServiceServicer_to_server(Storage(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    log.info(f"storage '{CONTAINER_NAME}' listening on {PORT}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
