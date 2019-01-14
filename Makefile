# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!

rliterate.py: rliterate_.py widgets.py
	python splice.py rliterate_.py widgets.py > rliterate.py

widgets.py: guicompiler.py widgets.gui
	python guicompiler.py < widgets.gui > widgets.py

guicompiler.py: guiparser.rlmeta wxguicodegenerator.rlmeta
	./make_guicompiler.sh > guicompiler.py
.PHONY: test
test:
	py.test -vv
	python rliterate.py rliterate.rliterate --diff > /dev/null
	python rliterate.py rliterate.rliterate --html > /dev/null
.PHONY: watch-test
watch-test:
	inotifywait -m -e close_write *rliterate.py 2>&1 | while read x; do tput reset && make test; done
