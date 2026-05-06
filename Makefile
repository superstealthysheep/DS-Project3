# Host machine
.PHONY: purge-containers
purge-containers:
	// a little scuffed
	docker rm $$(docker ps --all --filter name=p3-controller --quiet)
	docker rm $$(docker ps --all --filter name=p3-service-node --quiet)

.PHONY: up
up:
	(cd docker ; docker compose up --build ; cd ..)

# Devcontainer
## protofile
protofile_target_alias = proto/src/project3_pb2_grpc.py proto/src/project3_pb2.py proto/src/project3_pb2.pyi
.PHONY: proto
proto: $(protofile_target_alias)
$(protofile_target_alias): proto/project3.proto
	(cd proto ; sh gen_proto.sh ; cd ..)