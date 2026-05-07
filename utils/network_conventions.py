SERVICE_NODE_PREFIX = "p3-service-node-"
REPLICA_NODE_PREFIX = "p3-replica-node-"

def service_node_name(id: int):
    return f"{SERVICE_NODE_PREFIX}{id}"
def service_node_port(id: int):
    return 50150 + id

def replica_node_name(id: int):
    return f"{REPLICA_NODE_PREFIX}{id}"
def replica_node_port(id: int):
    return 50250 + id