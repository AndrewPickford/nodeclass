clean:
	rm -rf build dist nodeclass.egg-info

flakes:
	pyflakes3 nodeclass

rpm:
	python3 setup.py bdist_rpm

tests:
	py.test-3 -v

.PHONY: flakes tests
