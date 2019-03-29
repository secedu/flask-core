dist:
	python3 setup.py sdist bdist_wheel

dist-clean:
	rm -rf dist/

.PHONY: dist dist-clean
