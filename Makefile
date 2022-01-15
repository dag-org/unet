SHELL :/bin/bash

.PHONY: venv install data clean run-local image-exp run-exp

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
	docker build -f exp/Dockerfile -t unet-exp:latest exp

run-exp: image-exp
	docker run unet-exp:latest /bin/bash init.sh what \
		--env WANDB_API_KEY=${WANDB_API_KEY}