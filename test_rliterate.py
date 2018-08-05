# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!

import pytest

from rliterate import *
@pytest.fixture
def tmpfile(tmpdir):
    return str(tmpdir.join("test.rliterate"))
INLINE_TEXT = "This **is** very *cool*. [[106af6f8665c45e8ab751993a6abc876:page]] is it. Some `code`. [link](http://example.com)."
FRAGMENTS = [
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
TEXT_OLD = {"id": "abc1", "type": "text", "text": INLINE_TEXT}
TEXT_NEW = {"id": "abc1", "type": "text", "fragments": FRAGMENTS}
QUOTE_OLD = {"id": "abc2", "type": "quote", "text": INLINE_TEXT}
QUOTE_NEW = {"id": "abc2", "type": "quote", "fragments": FRAGMENTS}
IMAGE_OLD = {"id": "abc3", "type": "image", "image_base64": "data",
             "text": INLINE_TEXT}
IMAGE_NEW = {"id": "abc3", "type": "image", "image_base64": "data",
             "fragments": FRAGMENTS}
LIST_OLD = {
    "id": "abc4",
    "type": "list",
    "text": "\n".join([
        "* **a**{}".format(INLINE_TEXT),
        "* **b**{}".format(INLINE_TEXT),
        "    1. **c**{}".format(INLINE_TEXT),
        "    1. **d**{}".format(INLINE_TEXT),
    ]),
}
LIST_NEW = {
    "id": "abc4",
    "type": "list",
    "child_type": "unordered",
    "children": [
        {
            "fragments": [{"type": "strong", "text": "a"}]+FRAGMENTS,
            "child_type": None,
            "children": [],
        },
        {
            "fragments": [{"type": "strong", "text": "b"}]+FRAGMENTS,
            "child_type": "ordered",
            "children": [
                {
                    "fragments": [{"type": "strong", "text": "c"}]+FRAGMENTS,
                    "child_type": None,
                    "children": [],
                },
                {
                    "fragments": [{"type": "strong", "text": "d"}]+FRAGMENTS,
                    "child_type": None,
                    "children": [],
                },
            ],
        },
    ]
}
def test_converts_inline_text_to_fragments(tmpfile):
    old_paragraphs = [TEXT_OLD, QUOTE_OLD, IMAGE_OLD, LIST_OLD]
    new_paragraphs = [TEXT_NEW, QUOTE_NEW, IMAGE_NEW, LIST_NEW]
    document = write_read_document(tmpfile, {
        "title": "Root",
        "id": "abc1",
        "paragraphs": old_paragraphs,
        "children": [
            {
                "title": "Child",
                "children": [],
                "id": "abc2",
                "paragraphs": old_paragraphs,
            }
        ],
    })
    assert document["root_page"]["paragraphs"] == new_paragraphs
    assert document["root_page"]["children"][0]["paragraphs"] == new_paragraphs
CODE_OLD = {
    "id": "abc1",
    "type": "code",
    "path": ["foo.py", "<<functions>>"],
    "text": "one\n<<chunk>>\ntwo\n",
}
CODE_NEW = {
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
def test_converts_legacy_code_paragraphs(tmpfile):
    document = write_read_document(tmpfile, {
        "title": "Root",
        "children": [
            {
                "title": "Child",
                "children": [],
                "id": "abc2",
                "paragraphs": [CODE_OLD],
            },
        ],
        "id": "abc1",
        "paragraphs": [CODE_OLD],
    })
    assert document["root_page"]["paragraphs"] == [CODE_NEW]
    assert document["root_page"]["children"][0]["paragraphs"] == [CODE_NEW]
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
def test_converts_legacy_root_document(tmpfile):
    root_page = {
        "title": "Root",
        "children": [],
        "id": "abc1",
        "paragraphs": [],
    }
    assert write_read_document(tmpfile, root_page) == {
        "root_page": root_page,
        "variables": {},
    }
def write_read_document(path, document):
    write_json_to_file(path, document)
    doc = Document.from_file(path)
    with doc.notify():
        pass
    return load_json_from_file(path)
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
