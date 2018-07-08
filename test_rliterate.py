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
