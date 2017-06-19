help:
	@echo hi

virtualenv:
	test -d env || virtualenv env
	env/bin/pip install -Ur requirements.txt

server:
	env/bin/python src/inventory_app.py
