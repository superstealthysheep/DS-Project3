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

## Containers and their configs:
- Host machine
- Devcontainer
    - `.devcontainer/devcontainer.json`
- Nodes (controller, service)
    - `docker/docker-compose.yml`
    - `docker/Dockerfile`
- Replica/storage nodes:
    - `docker/docker-compose.yml`
    - `replica-node/Dockerfile`

### Areas of minor interest:
- `.uv_cache` is used project-wide to cache libraries (for devcontainer, for nodes)
