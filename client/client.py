import sys
import os
import grpc
import json
import time

# Add proto/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto', 'src'))

import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

import utils.config as config
import utils.log_util as log
import utils.network_conventions as net_con

# TARGET = os.environ.get("TARGET", "localhost:50050")
# TARGET = os.environ.get("TARGET", "host.docker.internal:50050")
TARGET = os.environ.get("TARGET", f"{net_con.CONTROLLER_NODE_NAME}:{net_con.CONTROLLER_NODE_BASE_PORT}")

def execute_command(argv):
    log.info("attempting command:", *argv)

    FAIL = "FAIL"
    if len(argv) < 2:
        print("Commands:")
        print("create-item <seller_id> <title> <category> <description> <starting_price> <quantity>")
        print("get-item <item_id>")
        print("search-items <keyword> [category]")
        print("update-item <item_id> <field> <value>")
        print("place-bid <item_id> <bidder_id> <bid_amount>")
        print("join-auction <item_id> <bidder_id>")
        print("interactive")
        return FAIL

    with grpc.insecure_channel(TARGET) as channel:
        stub = p3_grpc.FrontendServiceStub(channel)
        addr_resp = stub.FindServiceNode(p3.FindServiceNodeRequest())
        if not addr_resp.ok:
            return FAIL
        service_node_target = f"{addr_resp.address}:{addr_resp.port}"

    cmd = argv[1].lower()
    with grpc.insecure_channel(service_node_target) as channel:
        stub = p3_grpc.ServiceNodeServiceStub(channel)
        print(f"{stub.__dict__=}")
        if cmd == "create-item":
            if len(argv) < 8:
                print("create-item <seller_id> <title> <category> <description> <starting_price> <quantity>")
                return FAIL
            _, _, seller_id, title, category, description, starting_price, quantity = argv
            starting_price = int(starting_price)
            quantity = int(quantity)
            item_id = f"{seller_id}-{int(time.time()*1000)}"
            item = p3.Item(
                item_id=item_id,
                seller_id=seller_id,
                title=title,
                category=category,
                description=description,
                starting_price=starting_price,
                current_price=starting_price,
                quantity=quantity,
                status=p3.ITEM_STATUS_AVAILABLE,
                version="0",
            )
            log.info(f"{item}", flush=True)
            req = p3.CreateItemRequest(item=item)
            log.info(req, flush=True)
            r = stub.CreateItem(req)
            log.info(r, flush=True)
            print({"ok": r.ok, "item_id": r.item_id, "pod": r.pod})
        elif cmd == "get-item":
            if len(argv) < 3:
                print("get-item <item_id>")
                return FAIL
            item_id = argv[2]
            r = stub.GetItem(p3.GetItemRequest(item_id=item_id))
            if r.found:
                item_dict = {
                    "item_id": r.item.item_id,
                    "seller_id": r.item.seller_id,
                    "title": r.item.title,
                    "category": r.item.category,
                    "description": r.item.description,
                    "starting_price": r.item.starting_price,
                    "current_price": r.item.current_price,
                    "quantity": r.item.quantity,
                    "status": r.item.status,
                    "version": r.item.version
                }
                print({"found": True, "item": item_dict, "pod": r.pod})
            else:
                print({"found": False, "pod": r.pod})
        elif cmd == "search-items":
            if len(argv) < 3:
                print("search-items <keyword> [category]")
                return FAIL
            keyword = argv[2]
            category = argv[3] if len(argv) > 3 else ""
            r = stub.SearchItems(p3.SearchItemsRequest(keyword=keyword, category=category))
            items = []
            for item in r.items:
                items.append({
                    "item_id": item.item_id,
                    "title": item.title,
                    "category": item.category,
                    "current_price": item.current_price,
                    "status": item.status
                })
            print({"items": items, "pod": r.pod})
        elif cmd == "update-item":
            if len(argv) < 5:
                print("update-item <item_id> <field> <value>")
                return FAIL
            item_id, field, value = argv[2], argv[3], argv[4]
            # First get current item
            r = stub.GetItem(p3.GetItemRequest(item_id=item_id))
            if not r.found:
                print({"error": "item not found"})
                return FAIL
            item = r.item
            # Update the specified field
            if field == "title":
                item.title = value
            elif field == "description":
                item.description = value
            elif field == "quantity":
                item.quantity = int(value)
            elif field == "status":
                item.status = value
            r = stub.UpdateItem(
                p3.UpdateItemRequest(item_id=item_id, prev_version=item.version, new_value=item)
            )
            print({"ok": r.ok, "new_version": r.new_version, "pod": r.pod})
        elif cmd == "place-bid":
            if len(argv) < 5:
                print("place-bid <item_id> <bidder_id> <bid_amount>")
                return FAIL
            item_id, bidder_id, bid_amount = argv[2], argv[3], float(argv[4])
            r = stub.PlaceBid(p3.PlaceBidRequest(item_id=item_id, bidder_id=bidder_id, bid_amount=bid_amount))
            print({"ok": r.ok, "new_price": r.new_price, "pod": r.pod})
        elif cmd == "join-auction":
            if len(argv) < 4:
                print("join-auction <item_id> <bidder_id>")
                return FAIL
            item_id, bidder_id = argv[2], argv[3]
            try:
                for update in stub.JoinAuction(p3.JoinAuctionRequest(item_id=item_id, bidder_id=bidder_id)):
                    print({
                        "item_id": update.item_id,
                        "current_price": update.current_price,
                        "bidder_id": update.bidder_id,
                        "status": update.status,
                        "timestamp": update.timestamp
                    })
            except KeyboardInterrupt:
                print("Left auction")
        else:
            print("Unknown command")
            # sys.exit(1)
            return FAIL

def repl():
    while True:
        execute_command(input("> ").split())

def main():
    # execute command from args, then just accept more commands from stdin
    import time
    time.sleep(5)
    execute_command(sys.argv)
    # repl()

if __name__ == "__main__":
    main()
