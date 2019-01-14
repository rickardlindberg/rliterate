#!/bin/bash

set -e

cd "$(dirname "$0")"

support_py=$(python rlmeta/rlmeta.py --support)
parser_py=$(python rlmeta/rlmeta.py < guiparser.rlmeta)
wxcodegenerator_py=$(python rlmeta/rlmeta.py < wxguicodegenerator.rlmeta)

cat <<EOF
import sys

$support_py

$parser_py

$wxcodegenerator_py

join = "".join

if __name__ == "__main__":
    parser = GuiParser()
    wxcodegenerator = WxGuiCodeGenerator()
    try:
        ast = parser.run("file", sys.stdin.read())
        code = wxcodegenerator.run("file", ast)
        sys.stdout.write(code)
    except _MatchError as e:
        sys.stderr.write(e.describe())
        sys.exit(1)
EOF
