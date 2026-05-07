## Project setup

1. Vscode devcontainer extension should auto-build devcontainer for you

2. 
```bash
you@devcontainer $ make proto
```
NOTE: you will need to run this in the devcontainer whenever you make updates to the protofile

3. 
```bash
# (if necessary, `docker rm` old containers:)
you@host_machine $ make purge-containers

# (`docker compose up`)
you@host_machine $ make up
```

## High-level architecture

We should merge these two code paths together

### Docker compose version
Controller node runs two services:
- `FrontendService` (external API accessed by clients)
- `ControllerService` (internal API, for e.g. receiving heartbeats)
Service nodes run `ServiceNodeService`
Storage nodes run two services:
- `StorageNodeService` (external API, abstracted for ease of use)
- `ReplicaNodeService` (internal API for inter-replica communication)

### Non-Docker-compose version
Run each of the following in their own terminal in the devcontainer:
- `frontend/server.py`
- `client/client.py`
(this is not working for me rn. getting when client tries to connect to server to make rpc call? -William)

## Containers and their configs:
- Host machine
- Devcontainer
    - `.devcontainer/devcontainer.json`
- Nodes (controller, service)
    - `docker/docker-compose.yml`
    - `docker/Dockerfile`
    - `controller/controller.py` (has config for service node)
- Replica (aka storage) nodes:
    - `docker/docker-compose.yml`
    - `replica-node/Dockerfile`

## Port conventions
- Controller at `50050`
- Service nodes at range starting at `50150`
- Storage nodes at range starting at `50250`
- Client nodes at range starting at `50350`(?)

### Areas of minor interest:
- `.uv_cache` is used project-wide to cache libraries (for devcontainer, for nodes)
