run-server:
	poetry run python manage.py runserver

.PHONY: superuser
superuser:
	poetry run python -m cooking_core.manage createsuperuser
