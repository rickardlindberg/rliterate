# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!

rliterate.py: rliterate_.py widgets.py
	python splice.py rliterate_.py widgets.py > rliterate.py

widgets.py: rlgui.py widgets.gui
	python rlgui.py < widgets.gui > widgets.py
.PHONY: test
test:
	py.test -vv
	python rliterate.py rliterate.rliterate --diff > /dev/null
	python rliterate.py rliterate.rliterate --html > /dev/null
.PHONY: watch-test
watch-test:
	inotifywait -m -e close_write *rliterate.py 2>&1 | while read x; do tput reset && make test; done
