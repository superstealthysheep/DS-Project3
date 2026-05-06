## Project setup

1. Vscode devcontainer extension should auto-build devcontainer

2. 
```bash
# (if necessary, `docker rm` old containers:)
make purge-containers

cd docker
docker compose up --build
```

## Containers and their configs:
- Host machine
- Devcontainer
    - `.devcontainer/devcontainer.json`
- Nodes (controller, service, storage)
    - `docker/docker-compose.yml`
    - `docker/Dockerfile`

### Areas of minor interest:
- `.uv_cache` is used project-wide to cache libraries (for devcontainer, for nodes)
