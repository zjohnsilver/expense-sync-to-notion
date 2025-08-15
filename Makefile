.PHONY: run run-streamlit run-cli setup install

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi
	uv sync

run:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first"; \
		exit 1; \
	fi
	python main.py

run-streamlit:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first"; \
		exit 1; \
	fi
	python main.py --streamlit

run-cli:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first"; \
		exit 1; \
	fi
	python main.py --cli
