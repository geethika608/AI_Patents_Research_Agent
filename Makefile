.PHONY: help install test run clean setup

help: ## Show this help message
	@echo "Patent Research AI Agent - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup the development environment
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e .

install: ## Install dependencies
	pip install -e .

test: ## Run tests
	python -m pytest tests/ -v --cov=src/patent_researcher_agent --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	python -m pytest tests/integration/ -v

health-check: ## Run health check
	python scripts/health_check.py

backup: ## Create data backup
	python scripts/backup_data.py

monitoring: ## Run monitoring check
	python scripts/monitoring.py --check

monitoring-continuous: ## Start continuous monitoring
	python scripts/monitoring.py --continuous

monitoring-export: ## Export metrics
	python scripts/monitoring.py --export json

monitoring-setup: ## Setup local monitoring (no Docker required)
	./scripts/setup_local_monitoring.sh

monitoring-setup-full: ## Setup full monitoring with Prometheus & Grafana (requires Docker)
	./scripts/setup_monitoring.sh

monitoring-logs: ## View application logs
	python scripts/view_logs.py

monitoring-metrics: ## Start simple metrics server
	python monitoring/simple_metrics_server.py

dashboard: ## Start monitoring dashboard
	python -c "from patent_researcher_agent.utils.dashboard import dashboard; dashboard.create_dashboard().launch(server_name='0.0.0.0', server_port=7861)"

run: ## Run the application
	python src/patent_researcher_agent/main.py

chat: ## Launch the chat interface
	python src/patent_researcher_agent/launch_chat.py

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

lint: ## Run linting
	flake8 src/patent_researcher_agent/
	black src/patent_researcher_agent/ --check
	isort src/patent_researcher_agent/ --check-only

format: ## Format code
	black src/patent_researcher_agent/
	isort src/patent_researcher_agent/

docker-build: ## Build Docker image
	docker build -t patent-researcher-agent .

docker-run: ## Run Docker container
	docker run -p 7860:7860 patent-researcher-agent

test-metrics: ## Test metrics generation
	@echo "🧪 Testing metrics generation..."
	@python scripts/generate_test_metrics.py

test-advanced-metrics: ## Test advanced metrics (API, memory, rate limiting)
	@echo "🧪 Testing advanced metrics..."
	@python scripts/test_advanced_metrics.py 