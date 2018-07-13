# This file is automatically extracted from rliterate.rliterate.


import pytest

from rliterate import *


@pytest.fixture
def tmpfile(tmpdir):
    return str(tmpdir.join("test.rliterate"))


def test_can_read_legacy_file_format_paragraph_had_text(tmpfile):
    text = "This **is** very *cool*. [[106af6f8665c45e8ab751993a6abc876:page]] is it. Some `code`. [link](http://example.com)."
    fragments = [
        {"type": "text",      "text": "This "},
        {"type": "strong",    "text": "is"},
        {"type": "text",      "text": " very "},
        {"type": "emphasis",  "text": "cool"},
        {"type": "text",      "text": ". "},
        {"type": "reference", "text": "page", "page_id": "106af6f8665c45e8ab751993a6abc876"},
        {"type": "text",      "text": " is it. Some "},
        {"type": "code",      "text": "code"},
        {"type": "text",      "text": ". "},
        {"type": "link",      "text": "link", "url": "http://example.com"},
        {"type": "text",      "text": "."},
    ]
    write_json_to_file(tmpfile, {
        "title": "Root",
        "children": [],
        "id": "106af6f8665c45e8ab751993a6abc876",
        "paragraphs": [
            {"id": "abc1", "type": "text", "text": text},
            {"id": "abc2", "type": "quote", "text": text},
            {"id": "abc3", "type": "image", "text": text, "image_base64": "data"},
            {"id": "abc4", "type": "list", "text": "\n".join([
                "* **a**{}".format(text),
                "* **b**{}".format(text),
                "    1. **c**{}".format(text),
                "    1. **d**{}".format(text),
            ])},
        ],
    })
    doc = Document.from_file(tmpfile)
    with doc.notify():
        pass
    assert load_json_from_file(tmpfile) == {
        "title": "Root",
        "children": [],
        "id": "106af6f8665c45e8ab751993a6abc876",
        "paragraphs": [
            {"id": "abc1", "type": "text", "fragments": fragments},
            {"id": "abc2", "type": "quote", "fragments": fragments},
            {"id": "abc3", "type": "image", "fragments": fragments, "image_base64": "data"},
            {"id": "abc4", "type": "list", "child_type": "unordered", "children": [
                {"child_type": None, "children": [], "fragments": [{"type": "strong", "text": "a"}]+fragments},
                {"child_type": "ordered", "children": [
                    {"child_type": None, "children": [], "fragments": [{"type": "strong", "text": "c"}]+fragments},
                    {"child_type": None, "children": [], "fragments": [{"type": "strong", "text": "d"}]+fragments},
                ], "fragments": [{"type": "strong", "text": "b"}]+fragments},
            ]},
        ],
    }
def test_reads_legacy_code_paragraph(tmpfile):
    write_json_to_file(tmpfile, {
        "title": "Root",
        "children": [],
        "id": "106af6f8665c45e8ab751993a6abc876",
        "paragraphs": [
            {
                "id": "abc1",
                "type": "code",
                "path": ["foo.py", "<<functions>>"],
                "text": "one\n<<chunk>>\ntwo\n",
            }
        ],
    })
    document = Document(tmpfile)
    with document.notify():
        pass
    assert load_json_from_file(tmpfile)["paragraphs"] == [
        {
            "id": "abc1",
            "type": "code",
            "filepath": ["foo.py"],
            "chunkpath": ["functions"],
            "fragments": [
                {"type": "code", "text": "one\n"},
                {"type": "chunk", "prefix": "", "path": ["chunk"]},
                {"type": "code", "text": "two\n"},
            ],
        }
    ]
@pytest.mark.parametrize("path,expected_split", [
    (
        ["foo.py", "<<functions>>"],
        (["foo.py"], ["functions"])
    ),
    (
        ["foo.py", "<<Foo/__init__>>"],
        (["foo.py"], ["Foo", "__init__"])
    ),
    (
        ["foo.py", "<<functions>>", "<<with", "missing>>", "stuff/or"],
        (["foo.py"], ["functions", "with", "missing", "stuff", "or"])
    ),
    (
        ["foo.py", "<<with", "missing>>", "stuff/or"],
        (["foo.py", "<<with", "missing>>", "stuff", "or"], [])
    ),
    (
        ["bar/foo.py"],
        (["bar", "foo.py"], [])
    ),
    (
        [],
        ([], [])
    ),
])
def test_split_legacy_path(path, expected_split):
    assert split_legacy_path(path) == expected_split
@pytest.mark.parametrize("text,expected_fragments", [
    (
        "def foo()\n",
        [
            {"type": "code", "text": "def foo()\n"},
        ]
    ),
    (
        "def foo()\n    <<foo/pre>>\n    return False",
        [
            {"type": "code", "text": "def foo()\n"},
            {"type": "chunk", "prefix": "    ", "path": ["foo", "pre"]},
            {"type": "code", "text": "    return False\n"},
        ]
    ),
])
def test_legacy_code_text_to_fragments(text, expected_fragments):
    assert legacy_code_text_to_fragments(text) == expected_fragments
def test_reads_legacy_scratch_pages(tmpfile):
    write_json_to_file(tmpfile, {
        "workspace": {
            "scratch": ["abc"],
        }
    })
    layout = Layout(tmpfile)
    layout.set_hoisted_page(None)
    assert load_json_from_file(tmpfile)["workspace"] == {
        "columns": [
            ["abc"],
        ]
    }
