FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# copy over uv cache from host machine and install python deps when building (p sure)
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/root/.cache/uv
RUN --mount=type=cache,target=/root/.cache/uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY ./proto /app/proto
COPY ./controller ./app/controller
COPY ./service-node ./app/service-node
COPY ./docker ./app/docker
ENV PYTHONPATH=$PYTHONPATH:/app/proto/src

WORKDIR /app