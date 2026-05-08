NETWORK = "project3-net" # also must be modified in docker-compose.yml
COMPOSE_PROJECT_NAME = "project3-compose" # also must be modified in docker-compose.yml
N_REPLICAS = 5
READ_QUORUM_SIZE = 3
WRITE_QUORUM_SIZE = 3

STORAGE_REQUEST_TIMEOUT = 5

assert WRITE_QUORUM_SIZE * 2 > N_REPLICAS, "Write quorum too small"
assert READ_QUORUM_SIZE + WRITE_QUORUM_SIZE > N_REPLICAS, "Read or write quorum too small" 