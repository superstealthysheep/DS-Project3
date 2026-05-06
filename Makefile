.PHONY: purge-containers
purge-containers:
	// a little scuffed
	docker rm $$(docker ps --all --filter name=p3-controller --quiet)
	docker rm $$(docker ps --all --filter name=p3-service-node --quiet)

.PHONY: up
up:
	(cd docker ; docker compose up --build ; cd ..)