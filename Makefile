.PHONY: install lint test eval golden image kind-up deploy-kind validate bench

IMAGE ?= drawing-review:dev

install:
	pip install -r requirements.lock -r requirements-dev.txt && pip install --no-deps -e .

lint:
	ruff check . && ruff format --check .

test:
	pytest

eval:
	drawing-review eval --data golden --report reports/eval.md

golden:
	python scripts/update_golden.py

image:
	docker build --build-arg GIT_SHA=$$(git rev-parse --short=12 HEAD) -t $(IMAGE) .

kind-up:
	kind create cluster --name drw

deploy-kind: image
	kind load docker-image $(IMAGE) --name drw
	kubectl apply -k deploy/k8s/overlays/kind
	kubectl -n drawing-review rollout status deploy/drawing-review --timeout=120s

validate:
	kubectl kustomize deploy/k8s/overlays/kind | kubeconform -strict -summary -
	kubectl kustomize deploy/k8s/overlays/gpu | kubeconform -strict -summary -
	kubeconform -strict -summary deploy/k8s/vllm/

bench:
	python bench/load_test.py service --url http://localhost:8080 -n 200 -c 8
