import sys
import os
import time
import threading
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto', 'src'))

import grpc
import project3_pb2 as p3
import project3_pb2_grpc as p3_grpc

CONTROLLER = "p3-controller:50050"


def get_target():
    with grpc.insecure_channel(CONTROLLER) as ch:
        stub = p3_grpc.FrontendServiceStub(ch)
        r = stub.FindServiceNode(p3.FindServiceNodeRequest())
        return f"{r.address}:{r.port}"


def new_item(sid, price):
    iid = f"{sid}-{int(time.time()*1000)}-{threading.get_ident()}"
    return p3.Item(
        item_id=iid, seller_id=sid, title=f"item-{sid}",
        category="electronics", description="test item",
        starting_price=price, current_price=price, quantity=10,
        status=p3.ITEM_STATUS_AVAILABLE, version="0",
    )


def do_create(stub, sid, price=100):
    item = new_item(sid, price)
    t0 = time.time()
    r = stub.CreateItem(p3.CreateItemRequest(item=item))
    return r.ok, time.time() - t0, item.item_id


def do_get(stub, iid):
    t0 = time.time()
    r = stub.GetItem(p3.GetItemRequest(item_id=iid))
    return r.found, time.time() - t0


def do_bid(stub, iid, bidder, amt):
    t0 = time.time()
    r = stub.PlaceBid(p3.PlaceBidRequest(item_id=iid, bidder_id=bidder, bid_amount=amt))
    return r.ok, time.time() - t0


def show_stats(label, lats):
    if not lats:
        print(f"  {label}: no data")
        return
    lats = sorted(lats)
    avg = statistics.mean(lats) * 1000
    med = lats[len(lats)//2] * 1000
    mx = lats[-1] * 1000
    print(f"  {label}: mean={avg:.0f}ms median={med:.0f}ms max={mx:.0f}ms (n={len(lats)})")


def test1():
    print("\ntest 1 - sequential latency")
    target = get_target()
    cl, gl, bl, ids = [], [], [], []

    with grpc.insecure_channel(target) as ch:
        stub = p3_grpc.ServiceNodeServiceStub(ch)
        for i in range(10):
            ok, lat, iid = do_create(stub, f"s{i}")
            if ok:
                cl.append(lat)
                ids.append(iid)
        for iid in ids:
            found, lat = do_get(stub, iid)
            if found:
                gl.append(lat)
        for i, iid in enumerate(ids):
            _, lat = do_bid(stub, iid, f"b{i}", 150)
            bl.append(lat)

    show_stats("create", cl)
    show_stats("get", gl)
    show_stats("bid", bl)


def test2(n=10):
    print(f"\ntest 2 - {n} concurrent threads, 5 creates each")
    target = get_target()
    lats, errs, lock = [], [0], threading.Lock()

    def worker(tid):
        try:
            with grpc.insecure_channel(target) as ch:
                stub = p3_grpc.ServiceNodeServiceStub(ch)
                for j in range(5):
                    ok, lat, _ = do_create(stub, f"t{tid}_{j}")
                    with lock:
                        if ok: lats.append(lat)
                        else: errs[0] += 1
        except:
            with lock:
                errs[0] += 1

    t0 = time.time()
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = time.time() - t0

    print(f"  {len(lats)} ops in {elapsed:.2f}s = {len(lats)/elapsed:.0f} ops/sec, {errs[0]} errors")
    show_stats("create", lats)


def test3():
    # kill p3-replica-node-0 manually before running this
    print("\ntest 3 - fault tolerance (1 replica down)")
    target = get_target()

    with grpc.insecure_channel(target) as ch:
        stub = p3_grpc.ServiceNodeServiceStub(ch)
        ok, _, iid = do_create(stub, "fseller", price=200)
        assert ok, "create failed"
        print(f"  item: {iid}")

    print("  assuming replica-node-0 is already killed")
    time.sleep(1)

    with grpc.insecure_channel(target) as ch:
        stub = p3_grpc.ServiceNodeServiceStub(ch)
        found, lat = do_get(stub, iid)
        print(f"  get: found={found} ({lat*1000:.0f}ms)")
        ok, lat = do_bid(stub, iid, "fbidder", 250)
        print(f"  bid: ok={ok} ({lat*1000:.0f}ms)")


def test4():
    print("\ntest 4 - 10 concurrent bids, same item")
    target = get_target()

    with grpc.insecure_channel(target) as ch:
        stub = p3_grpc.ServiceNodeServiceStub(ch)
        ok, _, iid = do_create(stub, "cseller", price=100)
        assert ok
        time.sleep(0.5)

    results = []
    lock = threading.Lock()

    def bidder(i, amt):
        with grpc.insecure_channel(target) as ch:
            stub = p3_grpc.ServiceNodeServiceStub(ch)
            ok, _ = do_bid(stub, iid, f"b{i}", amt)
            with lock:
                results.append(ok)

    threads = [threading.Thread(target=bidder, args=(i, 110 + i*10)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    wins = sum(results)
    print(f"  {wins} accepted, {len(results)-wins} rejected")

    with grpc.insecure_channel(target) as ch:
        stub = p3_grpc.ServiceNodeServiceStub(ch)
        r = stub.GetItem(p3.GetItemRequest(item_id=iid))
        print(f"  final price: {r.item.current_price}")


if __name__ == "__main__":
    print("p3 benchmark")
    test1()
    test2()
    test3()
    test4()