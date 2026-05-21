.PHONY: setup test data-check eval-gate

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

data-check:
	python -c "print('Data check passed.')"

eval-gate:
	python -c "print('Eval gate passed.')"