SHELL :/bin/bash

.PHONY: venv install data clean run-local image-exp run-exp deploy

env=staging


venv:
	python3 -m venv venv

install: venv data
	source venv/bin/activate; \
	pip install -r requirements.txt; \
	deactivate

data:
	mkdir -p data/res

clean:
	rm -rf venv && rm -rf data

run-local: install
	source venv/bin/activate; \
	echo "Error: Not implemented"; \
	deactivate

image-exp:
	DOCKER_BUILDKIT=0 docker build -f exp/Dockerfile -t unet-exp:latest .

run-exp: image-exp
	docker run --env WANDB_API_KEY=${WANDB_API_KEY} \
		unet-exp:latest /bin/bash exp/init.sh $(SWEEP_ID)

deploy:
	cdk deploy --context env=$(env)
