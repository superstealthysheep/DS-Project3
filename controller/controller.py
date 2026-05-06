import argparse
import subprocess
import time

import grpc


def run_cmd(cmd, check=True, verbose=True):
    if verbose: print(" ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if verbose:
        print(res.stderr)
        print(res.stdout)
    return res


def replica_name(i):
    return f"storage-{i}"


def network_exists(network):
    result = run_cmd(
        ["docker", "network", "ls", "--format", "{{.Name}}"],
        check=False,
    )
    return network in result.stdout.splitlines()


def ensure_network(network):
    if not network_exists(network):
        run_cmd(["docker", "network", "create", network])
        print(f"created network: {network}", flush=True)


def container_running(name):
    result = run_cmd(
        [
            "docker",
            "ps",
            "--filter",
            f"name=^{name}$",
            "--filter",
            "status=running",
            "--format",
            "{{.Names}}",
        ],
        check=False,
    )
    return name in result.stdout.splitlines()


def remove_container(name):
    run_cmd(["docker", "rm", "-f", name], check=False)


def start_replica(name, image, network, container_port, host_port):
    remove_container(name)
    run_cmd(
        [
            "docker",
            "run",
            "-d",
            "--name",
            name,
            "--network",
            network,
            "-p",
            f"{host_port}:{container_port}",
            "-e",
            f"POD_NAME={name}",
            "-e",
            f"PORT={container_port}",
            image,
        ]
    )
    print(f"started {name} on localhost:{host_port}", flush=True)


def grpc_healthy(host_port, timeout_sec):
    target = f"localhost:{host_port}"
    channel = grpc.insecure_channel(target)
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout_sec)
        return True
    except Exception:
        return False
    finally:
        channel.close()


def running_storage_replicas():
    result = run_cmd(
        ["docker", "ps", "--filter", "name=^storage-", "--format", "{{.Names}}"],
        check=False,
    )
    names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(names)


def main():
    # print("dummy controller")
    parser = argparse.ArgumentParser(description="Simple storage replica controller")
    parser.add_argument("--image", default="storage:latest")
    parser.add_argument("--network", default="project3-net")
    parser.add_argument("--port", type=int, default=50052)
    parser.add_argument("--replicas", type=int, default=2)
    parser.add_argument(
        "--host-port-base",
        type=int,
        default=60052,
        help="Host port for storage-0 (storage-i uses base+i)",
    )
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=2)
    args = parser.parse_args()

    import docker
    docker_client = docker.from_env()
    print(docker_client)
    print(docker_client.containers.list())
    print(docker_client.containers.get("controller"))

    # ensure_network(args.network)

    # for i in range(args.replicas):
    #     name = replica_name(i)
    #     host_port = args.host_port_base + i
    #     if not container_running(name):
    #         start_replica(name, args.image, args.network, args.port, host_port)

    # print("controller is running", flush=True)

    # while True:
    #     for i in range(args.replicas):
    #         name = replica_name(i)
    #         host_port = args.host_port_base + i

    #         if not container_running(name):
    #             print(f"{name} is down (container not running), restarting", flush=True)
    #             start_replica(name, args.image, args.network, args.port, host_port)
    #             continue

    #         if not grpc_healthy(host_port, args.timeout):
    #             print(f"{name} is down (grpc timeout), replacing", flush=True)
    #             start_replica(name, args.image, args.network, args.port, host_port)

    #     print(f"active replicas: {running_storage_replicas()}", flush=True)
    #     time.sleep(args.interval)


if __name__ == "__main__":
    main()
