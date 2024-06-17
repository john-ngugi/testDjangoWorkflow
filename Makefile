run-server:
	poetry run python -m manage runserver

superuser:
	poetry run python -m manage createsuperuser

collectstatic:
	poetry run  python -m manage collectstatic
