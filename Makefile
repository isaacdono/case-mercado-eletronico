.PHONY: up down build logs test 

up:
	docker compose up --build -d

down:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f

test:
	docker compose exec mcp_server pytest -v
	docker compose exec backend pytest -v
