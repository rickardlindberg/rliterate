# This file is automatically extracted from rliterate.rliterate.

.PHONY: test
test:
	py.test

.PHONY: watch-test
watch-test:
	inotifywait -m -e close_write *rliterate.py 2>&1 | while read x; do tput reset && make test; done
