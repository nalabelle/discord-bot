build:
	docker build -t discord-bot:latest .

run:
	docker run \
		-v data:/app/data:rw \
		-v ~/git/discord-bot-extensions:/app/data/extensions \
		-v /run/secrets/discord_api_token:/run/secrets/discord_api_token:ro \
		--rm -it discord-bot \
		--config /app/data/local_config.yml
