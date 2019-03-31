dist:
	python3 setup.py sdist bdist_wheel

twine:
	twine dist/*

dist-clean:
	rm -rf dist/

.PHONY: dist dist-clean twine
