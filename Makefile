run-server:
	poetry run python manage.py runserver

superuser:
	poetry run python -m manage createsuperuser
