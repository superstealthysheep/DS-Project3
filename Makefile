# Host machine
.PHONY: purge-containers
purge-containers:
	# a little scuffed
	# (leading dash to not quit on error)
	-docker rm $$(docker ps --all --filter name="^p3-controller" --quiet)
	-docker rm $$(docker ps --all --filter name="^p3-service-node-" --quiet)
# 	-docker rm $$(docker ps --all --filter name="^project3-service-node-" --quiet)

# server up
.PHONY: sup
sup:
	(cd docker ; docker compose --profile server up --build; cd ..)

# client up
.PHONY: cup
cup:
	(cd docker ; docker compose --profile client up --build; cd ..)

.PHONY: up
up: purge-containers # purging each time a bit scuffed but ehh

	(cd docker ; docker compose --profile template up --build --no-start; )
	(cd docker ; docker compose --profile server --profile client up --build; cd ..)
# 	(cd docker ; docker compose --profile server --profile client up --build --force-recreate; cd ..)
# 

.PHONY: down
down:
	(cd docker; docker compose down --remove-orphans)

# Devcontainer
## protofile
protofile_target_alias = proto/src/project3_pb2_grpc.py proto/src/project3_pb2.py proto/src/project3_pb2.pyi
.PHONY: proto
proto: $(protofile_target_alias)
$(protofile_target_alias): proto/project3.proto
	(cd proto ; sh gen_proto.sh ; cd ..)