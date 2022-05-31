flakes:
	pyflakes3 reclass

tests:
	py.test-3 -v --ignore tests

.PHONY: flakes tests
