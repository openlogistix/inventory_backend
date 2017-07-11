help:
	@echo 'The OpenLogistix Inventory Backend'
	@echo
	@echo 'Targets:'
	@echo
	@echo '  virtualenv:	create virtualenv (./env), then pip install from requirements.txt'
	@echo '  server:	run a development server'
	@echo

virtualenv:
	test -d env || virtualenv env
	env/bin/pip install -Ur requirements.txt

server: virtualenv
	env/bin/python manage.py runserver
