
test:
	docker run --rm -it -v "$(PWD):/opt/src" python:3.7 bash -c " \
		READTHEDOCS=True pip install /opt/src -q; \
		python -m mkdocs build --version \
	"
