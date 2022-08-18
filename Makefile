PYFLAKES_0 := $(shell command -v pyflakes-3 2>/dev/null)
PYFLAKES_1 := $(shell command -v pyflakes3 2>/dev/null)
PYFLAKES_2 := $(shell command -v pyflakes 2>/dev/null)
ifdef PYFLAKES_0
PYFLAKES := pyflakes-3
else ifdef PYFLAKES_1
PYFLAKES := pyflakes3
else ifdef PYFLAKES_2
PYFLAKES := pyflakes
endif


clean:
	rm -rf build dist nodeclass.egg-info

flakes:
	${PYFLAKES} nodeclass

rpm:
	python3 setup.py bdist_rpm

tests:
	py.test-3 -v

types:
	mypy nodeclass

checks: tests types flakes

.PHONY: checks clean flakes tests types
