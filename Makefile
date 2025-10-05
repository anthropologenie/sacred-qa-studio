.PHONY: ritual health sankalpa qa frontend migrate migrate-create db-shell db-reset db-status

# Main ritual - runs all health checks
ritual: health sankalpa qa frontend test-lineage

# Health checks for all services
health:
	@echo "=== Health Checks ==="
	@echo -n "Backend: " && curl -s http://localhost:8000/health | jq -r '.status'
	@echo -n "AI Inference: " && curl -s http://localhost:8001/health | jq -r '.status'
	@echo -n "Frontend: " && curl -s http://localhost:3000 | jq -r '.status'

# Test sankalpa endpoint and verify in DB
sankalpa:
	@echo "=== Sankalpa Create → DB ==="
	@curl -s -X POST http://localhost:8000/sankalpa \
		-H "Content-Type: application/json" \
		-d '{"text":"Makefile ritual","context":"automated check"}' \
		| jq -r '.id' 2>/dev/null | xargs -I {} echo "Created Sankalpa ID: {}"
	@docker compose exec -T postgres psql -U admin -d ai_qa_platform -t \
		-c "SELECT 'Latest: ' || text || ' (' || created_at || ')' FROM app.sankalpa ORDER BY created_at DESC LIMIT 1;"

# Test QA endpoint and verify logging
qa:
	@echo "=== QA Proxy → Logs ==="
	@curl -s -X POST http://localhost:8000/qa \
		-H "Content-Type: application/json" \
		-d '{"prompt":"Makefile check"}' \
		| jq -r '.data.echo.prompt' 2>/dev/null | xargs -I {} echo "Echoed Prompt: {}"
	@docker compose exec -T postgres psql -U admin -d ai_qa_platform -t \
		-c "SELECT 'Logged QA at: ' || created_at FROM app.qa_logs ORDER BY created_at DESC LIMIT 1;"

# Frontend check
frontend:
	@echo "=== Frontend ==="
	@echo "Open http://localhost:3000 and check browser console for errors"


# Add after the existing targets
crud-test:
	@echo "=== Testing CRUD Operations ==="
	@echo "Creating sankalpa..."
	@SID=$$(curl -s -X POST http://localhost:8000/sankalpa \
		-H "Content-Type: application/json" \
		-d '{"text":"CRUD automation","context":"makefile"}' | jq -r '.id'); \
	echo "Created ID: $$SID"; \
	echo "Reading..."; \
	curl -s "http://localhost:8000/sankalpa/$$SID" | jq '.text, .status'; \
	echo "Updating..."; \
	curl -s -X PATCH "http://localhost:8000/sankalpa/$$SID" \
		-H "Content-Type: application/json" \
		-d '{"status":"completed"}' | jq '.status'; \
	echo "Deleting..."; \
	curl -s -X DELETE "http://localhost:8000/sankalpa/$$SID" | jq

smoke:
	@echo "=== Quick Smoke Test ==="
	@curl -s http://localhost:8000/health | jq -r '.status'
	@curl -s -X POST http://localhost:8000/sankalpa \
		-H 'Content-Type: application/json' \
		-d '{"text":"smoke","context":"test"}' | jq -r '.id'
	@echo "✓ Basic operations working"

seed:
	@docker compose exec postgres psql -U admin -d ai_qa_platform -c \
	  "INSERT INTO app.test_cases (name, description) VALUES \
	  ('Echo test', 'Verify echo response'), \
	  ('Idempotency test', 'Verify consistent responses');"

# Test lineage tracking end-to-end
test-lineage:
	@echo "=== Testing Lineage Tracking ==="
	@echo "1. Creating valid sankalpa..."
	@RESP=$$(curl -s -X POST http://localhost:8000/sankalpa \
		-H "Content-Type: application/json" \
		-d '{"text":"Lineage test from Makefile","context":"Automated verification"}'); \
	echo "   Response: $$RESP"; \
	LINEAGE_ID=$$(docker compose exec -T postgres psql -U admin -d ai_qa_platform -t \
		-c "SELECT response_payload->>'lineage_id' FROM app.sacred_contacts ORDER BY timestamp DESC LIMIT 1" | tr -d ' \n'); \
	echo "2. Lineage ID: $$LINEAGE_ID"; \
	echo "3. Fetching lineage tree..."; \
	curl -s http://localhost:8000/lineage/$$LINEAGE_ID | jq -r '.tree[] | "   \(.agent_name) -> \(.operation_type) (success: \(.success), duration: \(.duration_ms)ms)"'

# Show recent lineage activity
lineage-recent:
	@echo "=== Recent Lineage Activity ==="
	@docker compose exec -T postgres psql -U admin -d ai_qa_platform \
		-c "SELECT agent_name, operation_type, success, duration_ms, timestamp FROM app.request_lineage ORDER BY timestamp DESC LIMIT 10;"






# Database Management
# Apply pending migrations
migrate:
	@echo "=== Applying Migrations ==="
	docker compose exec backend sh -c "cd /app && alembic upgrade head"

# Create new migration with autogenerate
migrate-create:
	@echo "=== Creating Migration ==="
	@read -p "Migration message: " msg; \
	docker compose exec backend sh -c "cd /app && alembic revision --autogenerate -m \"$$msg\""

# Open PostgreSQL shell
db-shell:
	@echo "=== Opening Database Shell ==="
	docker compose exec postgres psql -U admin -d ai_qa_platform




# Show current migration status and table count
db-status:
	@echo "=== Database Status ==="
	@echo -n "Current migration: "
	@docker compose exec -T postgres psql -U admin -d ai_qa_platform -t \
		-c "SELECT version_num FROM app.alembic_version;"
	@echo "Tables in app schema:"
	@docker compose exec -T postgres psql -U admin -d ai_qa_platform \
		-c "\dt app.*"

# Reset database (WARNING: destroys all data)
db-reset:
	@echo "=== Resetting Database (DANGEROUS) ==="
	@read -p "Are you sure? This will DELETE ALL DATA. Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down -v; \
		docker compose up -d postgres; \
		sleep 3; \
		docker compose exec postgres psql -U admin -d ai_qa_platform -c "CREATE SCHEMA IF NOT EXISTS app;"; \
		$(MAKE) migrate; \
		echo "Database reset complete"; \
	else \
		echo "Reset cancelled"; \
	fi


