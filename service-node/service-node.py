import os
from concurrent import futures

import grpc

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc
import utils.log_util as log
# import log_util as log
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

def serve():
    global HOSTNAME
    global PORT
    global DATA

    HOSTNAME = os.environ.get("HOSTNAME", "service-node")
    PORT = os.environ.get("PORT", "50051")
    DATA = {}

    print("dummy service node")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p3_grpc.add_ServiceNodeServiceServicer_to_server(ServiceNode(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    # print(f"Service node '{HOSTNAME}' listening on {PORT}", flush=True)
    log.info(f"Service node '{HOSTNAME}' listening on {PORT}", flush=True)
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
