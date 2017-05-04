default: serve

test:
	python3 -m unittest discover

serve:
	cd web/ && npm run dev

build:
	cd web/ && npm run build

celery:
	celery --autoscale=100,10 worker

flask:
	FLASK_APP=app.py FLASK_DEBUG=1 flask run
