FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# copy over uv cache from host machine and install python deps when building (p sure)
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/root/.cache/uv
RUN --mount=type=cache,target=/root/.cache/uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# COPY proto ./app/proto
# COPY replica-node ./app/replica-node
# COPY storage ./app/storage
COPY proto /app/proto
COPY replica-node /app/replica-node
COPY service-node /app/service-node
COPY utils /app/utils
ENV PYTHONPATH=$PYTHONPATH:/app:/app/proto/src

# for replicas not spawned by container
CMD ["python", "-u", "replica-node/replica-node.py"]
# # for replicas spawned by container (override applied in spawner function)
# CMD ["python", "-u", "replica-node/ack_then_serve.py"]

