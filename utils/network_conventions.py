# ports
CONTROLLER_NODE_BASE_PORT = 50050
SERVICE_NODE_BASE_PORT = 50150
REPLICA_NODE_BASE_PORT = 50250
CLIENT_NODE_BASE_PORT = 50350

# container names
CONTROLLER_NODE_NAME = "p3-controller"
SERVICE_NODE_PREFIX = "p3-service-node-"
REPLICA_NODE_PREFIX = "p3-replica-node-"
CLIENT_NODE_PREFIX = "p3-client-node-"

def service_node_name(id: int):
    return f"{SERVICE_NODE_PREFIX}{id}"
def service_node_port(id: int):
    return SERVICE_NODE_BASE_PORT + id

def replica_node_name(id: int):
    return f"{REPLICA_NODE_PREFIX}{id}"
def replica_node_port(id: int):
    return REPLICA_NODE_BASE_PORT + id

def client_node_name(id: int):
    return f"{CLIENT_NODE_PREFIX}{id}"
def client_node_port(id: int):
    return CLIENT_NODE_BASE_PORT + id

# image names
CONTROLLER_NODE_IMAGE_NAME = "project3-controller-image:latest"
SERVICE_NODE_IMAGE_NAME = "project3-service-node-image:latest"
REPLICA_NODE_IMAGE_NAME = "project3-replica-node-image:latest"
CLIENT_NODE_IMAGE_NAME = "project3-client-image:latest"