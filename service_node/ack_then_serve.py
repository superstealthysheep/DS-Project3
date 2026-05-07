import importlib
service_node = importlib.import_module("service_node") # heehee
if __name__ == "__main__":
    service_node.ack_then_serve()