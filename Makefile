.PHONY: setup test data-check eval-gate

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/test_dummy.py -v

data-check:
	python -m pytest tests/test_data_checks.py -v

eval-gate:
	python pipelines/eval_gate.py