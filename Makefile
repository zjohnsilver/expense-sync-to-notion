.PHONY: run setup

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

run:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first"; \
		exit 1; \
	fi
	python main.py
