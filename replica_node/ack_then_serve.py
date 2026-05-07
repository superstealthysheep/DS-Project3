import importlib
replica_node = importlib.import_module("replica_node") # heehee
if __name__ == "__main__":
    replica_node.ack_then_serve()