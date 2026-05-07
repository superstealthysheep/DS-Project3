## Project setup

1. Vscode devcontainer extension should auto-build devcontainer for you

2. Make protofiles
```bash
you@devcontainer $ make proto
```
NOTE: you will need to run this in the devcontainer whenever you make updates to the protofile

3. Optional: start logs in a new terminal on host machine
```bash
you@host_machine: $ make follow
```
The logs produced by `make follow` have the benefit of including messages from containers spun up during the running of the system (e.g. service containers)

4. Start system
```bash
# (if necessary, `docker rm` old containers:)
you@host_machine $ make purge-containers

# (`docker compose up`)
you@host_machine $ make up
```

## High-level architecture

### Docker compose
Controller node runs two services:
- `FrontendService` (external API accessed by clients)
- `ControllerService` (internal API, for e.g. receiving heartbeats)
Service nodes run `ServiceNodeService`
Storage nodes run two services:
- `StorageNodeService` (external API, abstracted for ease of use)
- `ReplicaNodeService` (internal API for inter-replica communication)

## Containers and their configs:
- Host machine
- Devcontainer
    - `.devcontainer/devcontainer.json`
- Nodes (controller, service)
    - `docker/docker-compose.yml`
    - `docker/Dockerfile`
    - `controller/controller.py` (has config for when controller spins up service node)
- Replica (aka storage) nodes:
    - `docker/docker-compose.yml`
    - `replica_node/Dockerfile`
    - `controller/controller.py` (has config for when controller spins up replica node)

## Port conventions
- Controller at `50050`
- Service nodes at range starting at `50150`
- Storage nodes at range starting at `50250`
- Client nodes at range starting at `50350`(?)
Specified both in `/util/network_conventions.py` and relevant Docker configs

## Naming conventions:
- Docker images: `project3-{...}-image:latest`
- Docker containers: `p3-{...}-{id}`
- Networks: `project3-net`
Specified both in `/util/network_conventions.py` and relevant Docker configs

### Areas of minor interest:
- `.uv_cache` is used project-wide to cache libraries (for devcontainer, for nodes)
