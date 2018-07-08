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
        ],
    })
    doc = Document.from_file(tmpfile)
    doc.edit_page("106af6f8665c45e8ab751993a6abc876", {})
    assert load_json_from_file(tmpfile) == {
        "title": "Root",
        "children": [],
        "id": "106af6f8665c45e8ab751993a6abc876",
        "paragraphs": [
            {"id": "abc1", "type": "text", "fragments": fragments},
            {"id": "abc2", "type": "quote", "fragments": fragments},
            {"id": "abc3", "type": "image", "fragments": fragments, "image_base64": "data"},
        ],
    }
