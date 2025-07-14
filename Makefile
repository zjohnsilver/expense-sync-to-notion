.PHONY: help run clean info setup
.DEFAULT_GOAL := help

help: ## Show available commands
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup (copy .env.example to .env)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

run: ## Run the expense sync application
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup' first"; \
		exit 1; \
	fi
	python main.py

clean: ## Clean up cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

info: ## Show project information
	@echo "Project: Expense Sync to Notion"
	@echo "Python version: $(shell python --version)"
	@echo "UV version: $(shell uv --version)"
