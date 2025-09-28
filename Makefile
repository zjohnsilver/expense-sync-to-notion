.PHONY: run streamlit cli setup install

ENV_FILE = .env
PYTHON   = python

$(ENV_FILE):
	@if [ ! -f $(ENV_FILE) ]; then \
		cp .env.example $(ENV_FILE); \
		echo "Created $(ENV_FILE) from .env.example"; \
		echo "Please edit $(ENV_FILE) with your configuration"; \
	else \
		echo "$(ENV_FILE) already exists"; \
	fi

setup: $(ENV_FILE)
	uv sync

run: $(ENV_FILE)
	$(PYTHON) -m src.main

streamlit: $(ENV_FILE)
	$(PYTHON) -m src.main streamlit

sync_expenses: $(ENV_FILE)
	$(PYTHON) -m src.main sync
