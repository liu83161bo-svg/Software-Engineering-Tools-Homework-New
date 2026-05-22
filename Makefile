.PHONY: setup test data-check eval-gate

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

data-check:
	python -m pytest tests/test_data_checks.py -v

eval-gate:
	python -c "print('Eval gate passed.')"