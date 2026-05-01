import sys
import os
import grpc

import kv_pb2
import kv_pb2_grpc

TARGET = os.environ.get("TARGET", "localhost:50051")


def main():
    if len(sys.argv) < 2:
        print("put <key> <value>")
        print("get <key>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    with grpc.insecure_channel(TARGET) as channel:
        stub = kv_pb2_grpc.FrontendServiceStub(channel)
        if cmd == "put":
            if len(sys.argv) < 4:
                print("put <key> <value>")
                sys.exit(1)
            key, value = sys.argv[2], sys.argv[3]
            r = stub.Put(kv_pb2.PutRequest(key=key, value=value))
            print({"key": key, "ok": r.ok, "frontend_pod": r.pod})
        elif cmd == "get":
            if len(sys.argv) < 3:
                print("get <key>")
                sys.exit(1)
            key = sys.argv[2]
            r = stub.Get(kv_pb2.GetRequest(key=key))
            print(
                {
                    "key": key,
                    "found": r.found,
                    "value": r.value,
                    "frontend_pod": r.pod,
                }
            )
        else:
            print("use put or get")
            sys.exit(1)


if __name__ == "__main__":
    main()
