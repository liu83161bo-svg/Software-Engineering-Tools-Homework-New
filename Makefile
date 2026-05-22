.PHONY: setup test data-check eval-gate slo-gate rollback

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/test_dummy.py -v

data-check:
	python -m pytest tests/test_data_checks.py -v

eval-gate:
	python pipelines/eval_gate.py

slo-gate:
	python pipelines/slo_gate.py

rollback:
	@echo "Rolling back to previous model version..."
	@if [ -f models/previous_model.pkl ]; then \
		cp models/previous_model.pkl models/eval_model.pkl; \
		echo "Rollback completed."; \
	else \
		echo "No previous model found. Creating placeholder (ensure actual rollback is practiced)."; \
		# In production, this would fetch from registry; for homework we just echo. \
	fi