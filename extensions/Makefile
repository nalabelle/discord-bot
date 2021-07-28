update: poetry-update requirements.txt

test:
	poetry run pytest

poetry-update:
	@poetry update

requirements.txt: poetry.lock
	@poetry export --without-hashes > $@
