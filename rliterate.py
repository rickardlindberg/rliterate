# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!

from collections import defaultdict
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
import webbrowser
import xml.sax.saxutils
import StringIO
import base64
import copy

import pygments.lexers
import pygments.token
from pygments.token import Token as TokenType
import wx
import wx.richtext
import wx.lib.newevent
UNDO_BUFFER_SIZE = 10
TokenClick, EVT_TOKEN_CLICK = wx.lib.newevent.NewCommandEvent()
HoveredTokenChanged, EVT_HOVERED_TOKEN_CHANGED = wx.lib.newevent.NewCommandEvent()
CONTINUE_PROCESSING = object()
EditStart, EVT_EDIT_START = wx.lib.newevent.NewCommandEvent()
class Editable(wx.Panel):

    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.view = self.CreateView()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.view, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)
        self.view.Bind(EVT_EDIT_START, self.OnEditStart)

    def OnEditStart(self, event):
        if self.project.active_editor is not None:
            show_edit_in_progress_error(self)
            return
        with flicker_free_drawing(self):
            self.edit = self.CreateEdit(event.extra)
            self.edit.SetFocus()
            self.sizer.Add(self.edit, flag=wx.EXPAND, proportion=1)
            self.sizer.Hide(self.view)
            self.GetTopLevelParent().ChildReRendered()
            self.project.active_editor = self

    def Cancel(self):
        with flicker_free_drawing(self):
            self.edit.Destroy()
            self.sizer.Show(self.view)
            self.GetTopLevelParent().ChildReRendered()
            self.project.active_editor = None

    def Save(self):
        project = self.project
        self.edit.Save()
        project.active_editor = None
class Style(object):

    def __init__(self, color, bold=None, underlined=None, italic=False, monospace=False):
        self.color = color
        self.color_rgb = tuple([
            int(x, 16)
            for x
            in (color[1:3], color[3:5], color[5:7])
        ])
        self.bold = bold
        self.underlined = underlined
        self.italic = italic
        self.monospace = monospace

    def apply_to_wx_dc(self, dc, base_font, highlight=False):
        font = base_font
        if self.bold:
            font = font.Bold()
        if self.underlined:
            font = font.Underlined()
        if self.italic:
            font = font.Italic()
        if self.monospace:
            font = wx.Font(
                pointSize=font.GetPointSize(),
                family=wx.FONTFAMILY_TELETYPE,
                style=font.GetStyle(),
                weight=font.GetWeight(),
                underline=font.GetUnderlined(),
            )
        if highlight:
            dc.SetTextForeground("#fcf4df")
            dc.SetTextBackground("#b58900")
            dc.SetBackgroundMode(wx.SOLID)
        else:
            dc.SetTextForeground(self.color_rgb)
            dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(font)
class ParagraphBase(Editable):

    def __init__(self, parent, project, page_id, paragraph):
        self.page_id = page_id
        self.paragraph = paragraph
        Editable.__init__(self, parent, project)

    def BindMouse(self, widget, controls, **overrides):
        def create_handler(name, fn):
            def handler(*args, **kwargs):
                if name in overrides:
                    if overrides[name](*args, **kwargs) is not CONTINUE_PROCESSING:
                        return
                fn(*args, **kwargs)
            return handler
        handlers = {
            "double_click": lambda event: post_edit_start(widget),
            "drag": self.DoDragDrop,
            "right_click": lambda event: self.ShowContextMenu(),
        }
        for key in overrides.keys():
            if key in handlers:
                handlers[key] = create_handler(key, handlers[key])
            else:
                handlers[key] = overrides[key]
        MouseEventHelper.bind(controls, **handlers)

    def DoDragDrop(self):
        data = RliterateDataObject("paragraph", {
            "page_id": self.page_id,
            "paragraph_id": self.paragraph.id,
        })
        drag_source = wx.DropSource(self)
        drag_source.SetData(data)
        result = drag_source.DoDragDrop(wx.Drag_DefaultMove)

    def ShowContextMenu(self):
        menu = ParagraphContextMenu()
        menu.AppendItem(
            "New paragraph before",
            lambda: self.project.add_paragraph(
                self.page_id,
                before_id=self.paragraph.id
            )
        )
        menu.AppendItem(
            "New paragraph after",
            lambda: self.project.add_paragraph(
                self.page_id,
                before_id=self.paragraph.next_id
            )
        )
        menu.AppendItem(
            "Duplicate",
            lambda: self.paragraph.duplicate()
        )
        if hasattr(self.paragraph, "text_version"):
            menu.AppendItem(
                "Edit in gvim",
                lambda: setattr(
                    self.paragraph,
                    "text_version",
                    edit_in_gvim(
                        self.paragraph.text_version,
                        self.paragraph.filename
                    )
                )
            )
        menu.AppendSeparator()
        self.AddContextMenuItems(menu)
        menu.AppendSeparator()
        menu.AppendItem(
            "Delete",
            lambda: self.paragraph.delete()
        )
        self.PopupMenu(menu)
        menu.Destroy()

    def AddContextMenuItems(self, menu):
        pass
class DropPointDropTarget(wx.DropTarget):

    def __init__(self, window, kind):
        wx.DropTarget.__init__(self)
        self.window = window
        self.last_drop_point = None
        self.rliterate_data = RliterateDataObject(kind)
        self.DataObject = self.rliterate_data

    def OnDragOver(self, x, y, defResult):
        self._hide_last_drop_point()
        drop_point = self._find_closest_drop_point(x, y)
        if drop_point is not None and defResult == wx.DragMove:
            drop_point.Show()
            self.last_drop_point = drop_point
            return wx.DragMove
        return wx.DragNone

    def OnData(self, x, y, defResult):
        self._hide_last_drop_point()
        drop_point = self._find_closest_drop_point(x, y)
        if drop_point is not None and self.GetData():
            self.OnDataDropped(self.rliterate_data.get_json(), drop_point)
        return defResult

    def OnLeave(self):
        self._hide_last_drop_point()

    def _find_closest_drop_point(self, x, y):
        return self.window.FindClosestDropPoint(
            self.window.ClientToScreen((x, y))
        )

    def _hide_last_drop_point(self):
        if self.last_drop_point is not None:
            self.last_drop_point.Hide()
            self.last_drop_point = None
class TokenView(wx.Panel):

    def __init__(self, parent, project, tokens, **kwargs):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.tokens = tokens
        self.line_height = kwargs.get("line_height", 1)
        self.max_width = kwargs.get("max_width", 100)
        self.skip_extra_space = kwargs.get("skip_extra_space", False)
        self._calculate_token_positions()
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self._default_cursor = self.GetCursor()

    def _calculate_token_positions(self):
        dc = wx.MemoryDC()
        dc.SetFont(self.GetFont())
        dc.SelectObject(wx.EmptyBitmap(1, 1))
        self.token_positions = []
        x = 0
        y = 0
        max_x, max_y = dc.GetTextExtent("M")
        line_height_pixels = int(round(dc.GetTextExtent("M")[1]*self.line_height))
        for token in self.tokens:
            for subtoken in token.split():
                if subtoken.is_newline():
                    x = 0
                    y += line_height_pixels
                    max_y = max(max_y, y)
                    continue
                style = self.project.get_style(subtoken.token_type)
                style.apply_to_wx_dc(dc, self.GetFont())
                w, h = dc.GetTextExtent(subtoken.text)
                if x > 0 and x+w > self.max_width:
                    x = 0
                    y += line_height_pixels
                if x == 0 and self.skip_extra_space:
                    if self.token_positions and self.token_positions[-1][0].is_space():
                        self.token_positions.pop(-1)
                    if subtoken.is_space():
                        continue
                self.token_positions.append((subtoken, style, wx.Rect(x, y, w, h)))
                max_x = max(max_x, x+w)
                max_y = max(max_y, y+line_height_pixels)
                x += w
        self.SetMinSize((max_x, max_y))
    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        for token, style, box in self.token_positions:
            style.apply_to_wx_dc(dc, self.GetFont(), highlight=token.extra.get("highlight", False))
            dc.DrawText(token.text, box.X, box.Y)
    def GetToken(self, position):
        for token, style, box in self.token_positions:
            if box.Contains(position):
                return token
    def GetClosestToken(self, position):
        if len(self.token_positions) == 0:
            return None
        tokens_by_y_distance = defaultdict(list)
        for token, style, box in self.token_positions:
            if box.Contains(position):
                tokens_by_y_distance[0] = [(token, box)]
                break
            tokens_by_y_distance[
                abs(box.Y + int(box.Height / 2) - position.y)
            ].append((token, box))
        closest_token, closest_box = min(
            tokens_by_y_distance[min(tokens_by_y_distance.keys())],
            key=lambda (token, box): abs(box.X + int(box.Width / 2) - position.x)
        )
        center = closest_box.X + box.Width / 2.0
        left_margin = center - box.Width / 4.0
        right_margin = center + box.Width / 4.0
        if position.x < left_margin:
            edge = -1
        elif position.x > right_margin:
            edge = 1
        else:
            edge = 0
        return (edge, closest_token)
    def SetDefaultCursor(self):
        self.SetCursor(self._default_cursor)
class CompactScrolledWindow(wx.ScrolledWindow):

    MIN_WIDTH = 200
    MIN_HEIGHT = 200

    def __init__(self, parent, style=0, size=wx.DefaultSize, step=100):
        w, h = size
        size = (max(w, self.MIN_WIDTH), max(h, self.MIN_HEIGHT))
        wx.ScrolledWindow.__init__(self, parent, style=style, size=size)
        self.Size = size
        if style == wx.HSCROLL:
            self.SetScrollRate(1, 0)
            self._calc_scroll_pos = self._calc_scroll_pos_hscroll
        elif style == wx.VSCROLL:
            self.SetScrollRate(0, 1)
            self._calc_scroll_pos = self._calc_scroll_pos_vscroll
        else:
            self.SetScrollRate(1, 1)
            self._calc_scroll_pos = self._calc_scroll_pos_vscroll
        self.step = step
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel)

    def _on_mousewheel(self, event):
        x, y = self.GetViewStart()
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        self.Scroll(*self._calc_scroll_pos(x, y, delta))

    def _calc_scroll_pos_hscroll(self, x, y, delta):
        return (x+delta*self.step, y)

    def _calc_scroll_pos_vscroll(self, x, y, delta):
        return (x, y-delta*self.step)

    def ScrollToBeginning(self):
        self.Scroll(0, 0)

    def ScrollToEnd(self):
        self.Scroll(*(self.GetSizer().Size - self.Size))
class MultilineTextCtrl(wx.richtext.RichTextCtrl):

    MIN_HEIGHT = 50

    def __init__(self, parent, value, size=wx.DefaultSize):
        w, h = size
        size = (w, max(h, self.MIN_HEIGHT))
        wx.richtext.RichTextCtrl.__init__(
            self,
            parent,
            style=wx.richtext.RE_MULTILINE|wx.BORDER_SIMPLE,
            value=value,
            size=size
        )
class Observable(object):

    def __init__(self):
        self._notify_count = 0
        self._listeners = []

    def listen(self, fn, *events):
        self._listeners.append((fn, events))

    def unlisten(self, fn, *events):
        self._listeners.remove((fn, events))

    @contextlib.contextmanager
    def notify(self, event=""):
        self._notify_count += 1
        try:
            yield
        finally:
            self._notify_count -= 1
            self._notify(event)

    def notify_forwarder(self, prefix):
        def forwarder(event):
            self._notify("{}.{}".format(prefix, event))
        return forwarder

    def _notify(self, event):
        if self._notify_count == 0:
            for fn, fn_events in self._listeners:
                if self._is_match(fn_events, event):
                    fn(event)

    def _is_match(self, fn_events, event):
        if len(fn_events) == 0:
            return True
        for fn_event in fn_events:
            if is_prefix(fn_event.split("."), event.split(".")):
                return True
        return False
class Document(Observable):

    def __init__(self, document_dict=None):
        Observable.__init__(self)
        self._load(document_dict)

    @classmethod
    def from_file(cls, path):
        if os.path.exists(path):
            document = cls(load_json_from_file(path))
        else:
            document = cls()
        document.listen(lambda event:
            write_json_to_file(
                path,
                document.read_only_document_dict
            )
        )
        return document
    def _load(self, document_dict):
        self._history = History(
            DocumentDictWrapper(
                self._convert_to_latest(
                    self._empty_page()
                    if document_dict is None else
                    document_dict
                )
            ),
            size=UNDO_BUFFER_SIZE
        )
    @property
    def read_only_document_dict(self):
        return self._history.value
    @contextlib.contextmanager
    def modify(self, name):
        with self.notify():
            with self._history.new_value(name) as value:
                yield value

    def get_undo_operation(self):
        def undo():
            with self.notify():
                self._history.back()
        if self._history.can_back():
            return (self._history.back_name(), undo)

    def get_redo_operation(self):
        def redo():
            with self.notify():
                self._history.forward()
        if self._history.can_forward():
            return (self._history.forward_name(), redo)
    def add_page(self, title="New page", parent_id=None):
        with self.modify("Add page") as document_dict:
            document_dict.add_page_dict(self._empty_page(), parent_id=parent_id)

    def _empty_page(self):
        return {
            "id": genid(),
            "title": "New page...",
            "children": [],
            "paragraphs": [],
        }
    def get_page(self, page_id=None):
        page_dict = self.read_only_document_dict.get_page_dict(page_id)
        if page_dict is None:
            return None
        return Page(self, page_dict)
    def add_paragraph(self, page_id, before_id=None):
        with self.modify("Add paragraph") as document_dict:
            paragraph = {
                "id": genid(),
                "type": "factory",
            }
            document_dict.add_paragraph_dict(paragraph, page_id, before_id=before_id)

    def get_paragraph(self, page_id, paragraph_id):
        for paragraph in self.get_page(page_id).paragraphs:
            if paragraph.id == paragraph_id:
                return paragraph
    def rename_path(self, path, name):
        with self.modify("Rename path") as document_dict:
            for p in document_dict.paragraph_dict_iterator():
                if p["type"] == "code":
                    filelen = len(p["filepath"])
                    chunklen = len(p["chunkpath"])
                    if path.is_prefix(Path(p["filepath"], p["chunkpath"])):
                        if path.length > filelen:
                            p["chunkpath"][path.length-1-filelen] = name
                        else:
                            p["filepath"][path.length-1] = name
                    else:
                        for f in p["fragments"]:
                            if f["type"] == "chunk":
                                if path.is_prefix(Path(p["filepath"], p["chunkpath"]+f["path"])):
                                    f["path"][path.length-1-filelen-chunklen] = name
    def new_variable(self, name):
        with self.modify("New variable") as document_dict:
            variable_id = genid()
            document_dict["variables"][variable_id] = name
            return variable_id

    def rename_variable(self, variable_id, name):
        with self.modify("Rename variable") as document_dict:
            document_dict["variables"][variable_id] = name

    def lookup_variable(self, variable_id):
        return self.read_only_document_dict["variables"].get(variable_id)
    def _convert_to_latest(self, document_dict):
        for fn in [
            self._legacy_inline_text,
            self._legacy_inline_code,
            self._legacy_root_page,
        ]:
            document_dict = fn(document_dict)
        return document_dict
    def _legacy_inline_text(self, document_dict):
        for paragraph in document_dict.get("paragraphs", []):
            if paragraph["type"] in ["text", "quote", "image"] and "text" in paragraph:
                paragraph["fragments"] = LegacyInlineTextParser().parse(paragraph["text"])
                del paragraph["text"]
            elif paragraph["type"] in ["list"] and "text" in paragraph:
                paragraph["child_type"], paragraph["children"] = LegacyListParser(paragraph["text"]).parse_items()
                del paragraph["text"]
        for child in document_dict.get("children", []):
            self._legacy_inline_text(child)
        return document_dict
    def _legacy_inline_code(self, document_dict):
        for p in document_dict.get("paragraphs", []):
            if p["type"] == "code" and "path" in p:
                p["filepath"], p["chunkpath"] = split_legacy_path(p["path"])
                del p["path"]
            if p["type"] == "code" and "text" in p:
                p["fragments"] = legacy_code_text_to_fragments(p["text"])
                del p["text"]
        for child in document_dict.get("children", []):
            self._legacy_inline_code(child)
        return document_dict
    def _legacy_root_page(self, document_dict):
        if "root_page" not in document_dict:
            return {
                "root_page": document_dict,
                "variables": {},
            }
        else:
            return document_dict
class DocumentDictWrapper(dict):

    def __init__(self, document_dict):
        dict.__init__(self, document_dict)
        self._pages = {}
        self._parent_pages = {}
        self._paragraphs = {}
        self._cache_page(self["root_page"])

    def _cache_page(self, page, parent_page=None):
        self._pages[page["id"]] = page
        self._parent_pages[page["id"]] = parent_page
        for paragraph in page["paragraphs"]:
            self._paragraphs[paragraph["id"]] = paragraph
        for child in page["children"]:
            self._cache_page(child, page)

    def add_page_dict(self, page_dict, parent_id=None):
        page_dict = copy.deepcopy(page_dict)
        parent_page = self._pages[parent_id]
        parent_page["children"].append(page_dict)
        self._pages[page_dict["id"]] = page_dict
        self._parent_pages[page_dict["id"]] = parent_page

    def get_page_dict(self, page_id=None):
        if page_id is None:
            page_id = self["root_page"]["id"]
        return self._pages.get(page_id, None)

    def delete_page_dict(self, page_id):
        if page_id == self["root_page"]["id"]:
            return
        page = self._pages[page_id]
        parent_page = self._parent_pages[page_id]
        index = index_with_id(parent_page["children"], page_id)
        parent_page["children"].pop(index)
        self._pages.pop(page_id)
        self._parent_pages.pop(page_id)
        for child in reversed(page["children"]):
            parent_page["children"].insert(index, child)
            self._parent_pages[child["id"]] = parent_page

    def update_page_dict(self, page_id, data):
        self._pages[page_id].update(copy.deepcopy(data))

    def move_page_dict(self, page_id, parent_page_id, before_page_id):
        if page_id == before_page_id:
            return
        parent = self._pages[parent_page_id]
        while parent is not None:
            if parent["id"] == page_id:
                return
            parent = self._parent_pages[parent["id"]]
        parent = self._parent_pages[page_id]
        page = parent["children"].pop(index_with_id(parent["children"], page_id))
        new_parent = self._pages[parent_page_id]
        self._parent_pages[page_id] = new_parent
        if before_page_id is None:
            new_parent["children"].append(page)
        else:
            new_parent["children"].insert(
                index_with_id(new_parent["children"], before_page_id),
                page
            )

    def paragraph_dict_iterator(self):
        return self._paragraphs.values()

    def add_paragraph_dict(self, paragraph_dict, page_id, before_id):
        paragraph_dict = copy.deepcopy(paragraph_dict)
        paragraphs = self._pages[page_id]["paragraphs"]
        if before_id is None:
            paragraphs.append(paragraph_dict)
        else:
            paragraphs.insert(index_with_id(paragraphs, before_id), paragraph_dict)
        self._paragraphs[paragraph_dict["id"]] = paragraph_dict

    def delete_paragraph_dict(self, page_id, paragraph_id):
        paragraphs = self._pages[page_id]["paragraphs"]
        paragraphs.pop(index_with_id(paragraphs, paragraph_id))
        return self._paragraphs.pop(paragraph_id)

    def move_paragraph_dict(self, page_id, paragraph_id, target_page, before_paragraph):
        if (page_id == target_page and
            paragraph_id == before_paragraph):
            return
        self.add_paragraph_dict(
            self.delete_paragraph_dict(page_id, paragraph_id),
            target_page,
            before_paragraph
        )

    def update_paragraph_dict(self, paragraph_id, data):
        self._paragraphs[paragraph_id].update(copy.deepcopy(data))
class Page(object):

    def __init__(self, document, page_dict):
        self._document = document
        self._page_dict = page_dict

    @property
    def id(self):
        return self._page_dict["id"]

    @property
    def title(self):
        return self._page_dict["title"]

    def set_title(self, title):
        with self._document.modify("Change title") as document_dict:
            document_dict.update_page_dict(self.id, {"title": title})

    @property
    def paragraphs(self):
        return [
            Paragraph.create(
                self._document,
                self,
                paragraph_dict,
                next_paragraph_dict["id"] if next_paragraph_dict is not None else None
            )
            for paragraph_dict, next_paragraph_dict
            in zip(
                self._page_dict["paragraphs"],
                self._page_dict["paragraphs"][1:]+[None]
            )
        ]

    @property
    def children(self):
        return [
            Page(self._document, child_dict)
            for child_dict
            in self._page_dict["children"]
        ]

    def delete(self):
        with self._document.modify("Delete page") as document_dict:
            document_dict.delete_page_dict(self.id)

    def move(self, parent_page_id, before_page_id):
        with self._document.modify("Move page") as document_dict:
            document_dict.move_page_dict(self.id, parent_page_id, before_page_id)
class Paragraph(object):

    @staticmethod
    def create(document, page, paragraph_dict, next_id):
        return {
            "text": TextParagraph,
            "quote": QuoteParagraph,
            "list": ListParagraph,
            "code": CodeParagraph,
            "image": ImageParagraph,
        }.get(paragraph_dict["type"], Paragraph)(document, page, paragraph_dict, next_id)

    def __init__(self, document, page, paragraph_dict, next_id):
        self._document = document
        self._page = page
        self._paragraph_dict = paragraph_dict
        self._next_id = next_id

    @property
    def id(self):
        return self._paragraph_dict["id"]

    @property
    def next_id(self):
        return self._next_id

    @property
    def type(self):
        return self._paragraph_dict["type"]

    @contextlib.contextmanager
    def multi_update(self):
        with self._document.modify("Edit paragraph"):
            yield

    def update(self, data):
        with self._document.modify("Edit paragraph") as document_dict:
            document_dict.update_paragraph_dict(self.id, data)

    def delete(self):
        with self._document.modify("Delete paragraph") as document_dict:
            document_dict.delete_paragraph_dict(self._page.id, self.id)

    def move(self, target_page, before_paragraph):
        with self._document.modify("Move paragraph") as document_dict:
            document_dict.move_paragraph_dict(self._page.id, self.id, target_page, before_paragraph)

    def duplicate(self):
        with self._document.modify("Duplicate paragraph") as document_dict:
            document_dict.add_paragraph_dict(
                dict(self._paragraph_dict, id=genid()),
                page_id=self._page.id,
                before_id=self.next_id
            )

    @property
    def filename(self):
        return "paragraph.txt"
class TextParagraph(Paragraph):

    @property
    def fragments(self):
        return TextFragment.create_list(self._document, self._paragraph_dict["fragments"])

    @property
    def tokens(self):
        return [x.token for x in self.fragments]

    def get_text_index(self, index):
        return self._text_version.get_selection(index)[0]

    @property
    def text_version(self):
        return self._text_version.text

    @property
    def _text_version(self):
        text_version = TextVersion()
        for fragment in self.fragments:
            fragment.fill_text_version(text_version)
        return text_version

    @text_version.setter
    def text_version(self, value):
        self.update({"fragments": text_to_fragments(value)})
class QuoteParagraph(TextParagraph):
    pass
class ListParagraph(Paragraph):

    @property
    def child_type(self):
        return self._paragraph_dict["child_type"]

    @property
    def children(self):
        return [ListItem(self._document, x) for x in self._paragraph_dict["children"]]

    def get_text_index(self, list_and_fragment_index):
        return self._text_version.get_selection(list_and_fragment_index)[0]

    @property
    def text_version(self):
        return self._text_version.text

    @property
    def _text_version(self):
        def list_item_to_text(text_version, child_type, item, indent=0, index=0):
            text_version.add("    "*indent)
            if child_type == "ordered":
                text_version.add("{}. ".format(index+1))
            else:
                text_version.add("* ")
            for fragment in item.fragments:
                fragment.fill_text_version(text_version)
            text_version.add("\n")
            for index, child in enumerate(item.children):
                with text_version.index(index):
                    list_item_to_text(text_version, item.child_type, child, index=index, indent=indent+1)
        text_version = TextVersion()
        for index, child in enumerate(self.children):
            with text_version.index(index):
                list_item_to_text(text_version, self.child_type, child, index=index)
        return text_version

    @text_version.setter
    def text_version(self, value):
        child_type, children = LegacyListParser(value).parse_items()
        self.update({
            "child_type": child_type,
            "children": children
        })
class ListItem(object):

    def __init__(self, document, item_dict):
        self._document = document
        self._item_dict = item_dict

    @property
    def fragments(self):
        return TextFragment.create_list(self._document, self._item_dict["fragments"])

    @property
    def child_type(self):
        return self._item_dict["child_type"]

    @property
    def children(self):
        return [ListItem(self._document, x) for x in self._item_dict["children"]]

    @property
    def tokens(self):
        return [x.token for x in self.fragments]
class CodeParagraph(Paragraph):

    @property
    def path(self):
        return Path(
            [x for x in self._paragraph_dict["filepath"] if x],
            [x for x in self._paragraph_dict["chunkpath"] if x]
        )

    @path.setter
    def path(self, path):
        self.update({
            "filepath": copy.deepcopy(path.filepath),
            "chunkpath": copy.deepcopy(path.chunkpath),
        })
    @property
    def filename(self):
        return self.path.filename
    @property
    def fragments(self):
        return CodeFragment.create_list(
            self._document,
            self,
            self._paragraph_dict["fragments"]
        )
    @property
    def text_version(self):
        text_version = TextVersion()
        for fragment in self.fragments:
            fragment.fill_text_version(text_version)
        return text_version.text
    @text_version.setter
    def text_version(self, value):
        with self.multi_update():
            self.update({
                "fragments": self._parse(value)
            })

    def _parse(self, value):
        self._parsed_fragments = []
        self._parse_buffer = ""
        for line in value.splitlines():
            match = re.match(self._chunk_fragment_re(), line)
            if match:
                self._parse_clear()
                self._parsed_fragments.append({
                    "type": "chunk",
                    "path": match.group(2).split("/"),
                    "prefix": match.group(1)
                })
            else:
                while line:
                    match = re.match(self._variable_fragment_re(), line)
                    if match:
                        self._parse_clear()
                        self._parsed_fragments.append({
                            "type": "variable",
                            "id": self._get_variable_id(match.group(1))
                        })
                        line = line[len(match.group(0)):]
                    else:
                        self._parse_buffer += line[0]
                        line = line[1:]
                self._parse_buffer += "\n"
        self._parse_clear()
        return self._parsed_fragments

    def _get_variable_id(self, identifier):
        if self._document.lookup_variable(identifier) is None:
            return self._document.new_variable(identifier)
        else:
            return identifier

    def _parse_clear(self):
        if self._parse_buffer:
            self._parsed_fragments.append({"type": "code", "text": self._parse_buffer})
        self._parse_buffer = ""

    def _chunk_fragment_re(self):
        start, end = self.chunk_delimiters
        return r"^(\s*){}(.*){}\s*$".format(re.escape(start), re.escape(end))

    def _variable_fragment_re(self):
        start, end = self.variable_delimiters
        return r"{}(.*?){}".format(re.escape(start), re.escape(end))
    @property
    def tokens(self):
        pygments_text, inserts, extras = self._pygments_text()
        return self._pygments_tokens_to_tokens(
            self.pygments_lexer.get_tokens(pygments_text),
            inserts,
            extras
        )

    def _pygments_text(self):
        pygments_text = ""
        inserts = defaultdict(list)
        extras = defaultdict(dict)
        for fragment in self.fragments:
            if fragment.type == "chunk":
                text_version = TextVersion()
                fragment.fill_text_version(text_version)
                inserts[len(pygments_text)].append(Token(
                    text_version.text,
                    token_type=TokenType.RLiterate.Chunk,
                    subpath=self.path.extend_chunk(fragment.path)
                ))
            elif fragment.type == "variable":
                text = fragment.name
                for i in range(len(text)):
                    extras[len(pygments_text)+i] = {"variable": fragment.id}
                pygments_text += text
            else:
                pygments_text += fragment.text
        return pygments_text, inserts, extras

    def _pygments_tokens_to_tokens(self, pygments_tokens, inserts, extras):
        pos = 0
        tokens = []
        for pygments_token, text in pygments_tokens:
            for ch in text:
                tokens.extend(inserts.get(pos, []))
                tokens.append(Token(ch, token_type=pygments_token, **extras.get(pos, {})))
                pos += 1
        tokens.extend(inserts.get(pos, []))
        return tokens
    @property
    def language(self):
        return "".join(self.pygments_lexer.aliases[:1])

    @property
    def pygments_lexer(self):
        try:
            return pygments.lexers.get_lexer_for_filename(
                self.filename,
                stripnl=False
            )
        except:
            return pygments.lexers.TextLexer(stripnl=False)
    @property
    def chunk_delimiters(self):
        return ("<<", ">>")
    @property
    def variable_delimiters(self):
        return (
            "__RL_",
            "__"
        )
class Path(object):

    @classmethod
    def from_text_version(cls, text):
        try:
            filepath_text, chunkpath_text = text.split(" // ", 1)
        except:
            filepath_text = text
            chunkpath_text = ""
        return cls(
            filepath_text.split("/") if filepath_text else [],
            chunkpath_text.split("/") if chunkpath_text else [],
        )

    @property
    def text_version(self):
        if self.has_both():
            sep = " // "
        else:
            sep = ""
        return "{}{}{}".format(
            "/".join(self.filepath),
            sep,
            "/".join(self.chunkpath)
        )

    @property
    def text_start(self):
        return self.text_end - len(self.last)

    @property
    def text_end(self):
        return len(self.text_version)

    def extend_chunk(self, chunk):
        return Path(
            copy.deepcopy(self.filepath),
            copy.deepcopy(self.chunkpath)+copy.deepcopy(chunk)
        )

    @property
    def filename(self):
        return self.filepath[-1] if self.filepath else ""

    @property
    def last(self):
        if len(self.chunkpath) > 0:
            return self.chunkpath[-1]
        elif len(self.filepath) > 0:
            return self.filepath[-1]
        else:
            return ""

    @property
    def is_empty(self):
        return self.length == 0

    @property
    def length(self):
        return len(self.chunkpath) + len(self.filepath)

    def __init__(self, filepath, chunkpath):
        self.filepath = filepath
        self.chunkpath = chunkpath

    def is_prefix(self, other):
        if len(self.chunkpath) > 0:
            return self.filepath == other.filepath and self.chunkpath == other.chunkpath[:len(self.chunkpath)]
        else:
            return self.filepath == other.filepath[:len(self.filepath)]

    def has_both(self):
        return len(self.filepath) > 0 and len(self.chunkpath) > 0

    @property
    def filepaths(self):
        for index in range(len(self.filepath)):
            yield (
                self.filepath[index],
                Path(self.filepath[:index+1], [])
            )

    @property
    def chunkpaths(self):
        for index in range(len(self.chunkpath)):
            yield (
                self.chunkpath[index],
                Path(self.filepath[:], self.chunkpath[:index+1])
            )
class CodeFragment(object):

    @staticmethod
    def create_list(document, code_paragraph, code_fragment_dicts):
        return [
            CodeFragment.create(document, code_paragraph, code_fragment_dict)
            for code_fragment_dict
            in code_fragment_dicts
        ]

    @staticmethod
    def create(document, code_paragraph, code_fragment_dict):
        return {
            "variable": VariableCodeFragment,
            "chunk": ChunkCodeFragment,
            "code": CodeCodeFragment,
        }.get(code_fragment_dict["type"], CodeFragment)(document, code_paragraph, code_fragment_dict)

    def __init__(self, document, code_paragraph, code_fragment_dict):
        self._document = document
        self._code_paragraph = code_paragraph
        self._code_fragment_dict = code_fragment_dict

    @property
    def type(self):
        return self._code_fragment_dict["type"]
class VariableCodeFragment(CodeFragment):

    @property
    def id(self):
        return self._code_fragment_dict["id"]

    @property
    def name(self):
        name = self._document.lookup_variable(self.id)
        if name is None:
            return fragment.id
        else:
            return name

    def fill_text_version(self, text_version):
        start, end = self._code_paragraph.variable_delimiters
        text_version.add(start)
        text_version.add(self.id)
        text_version.add(end)
class ChunkCodeFragment(CodeFragment):

    @property
    def prefix(self):
        return self._code_fragment_dict["prefix"]

    @property
    def path(self):
        return copy.deepcopy(self._code_fragment_dict["path"])

    def fill_text_version(self, text_version):
        start, end = self._code_paragraph.chunk_delimiters
        text_version.add(self.prefix)
        text_version.add(start)
        text_version.add("/".join(self.path))
        text_version.add(end)
        text_version.add("\n")
class CodeCodeFragment(CodeFragment):

    @property
    def text(self):
        return self._code_fragment_dict["text"]

    @property
    def text_version(self):
        text_version = TextVersion()
        self.fill_text_version(text_version)
        return text_version.text

    def fill_text_version(self, text_version):
        text_version.add(self.text)
class ImageParagraph(Paragraph):

    @property
    def fragments(self):
        return TextFragment.create_list(self._document, self._paragraph_dict["fragments"])

    @property
    def tokens(self):
        return [x.token for x in self.fragments]

    @property
    def image_base64(self):
        return self._paragraph_dict.get("image_base64", None)

    @property
    def text_version(self):
        return fragments_to_text(self.fragments)

    @text_version.setter
    def text_version(self, value):
        self.update({"fragments": text_to_fragments(value)})
class TextFragment(object):

    @staticmethod
    def create_list(document, text_fragment_dicts):
        return [
            TextFragment.create(document, text_fragment_dict, index)
            for index, text_fragment_dict
            in enumerate(text_fragment_dicts)
        ]

    @staticmethod
    def create(document, text_fragment_dict, index):
        return {
            "strong": StrongTextFragment,
            "emphasis": EmphasisTextFragment,
            "code": CodeTextFragment,
            "reference": ReferenceTextFragment,
            "link": LinkTextFragment,
        }.get(text_fragment_dict["type"], TextFragment)(document, text_fragment_dict, index)

    def __init__(self, document, text_fragment_dict, index):
        self._document = document
        self._text_fragment_dict = text_fragment_dict
        self._index = index

    @property
    def type(self):
        return self._text_fragment_dict["type"]

    @property
    def text(self):
        return self._text_fragment_dict["text"]

    @property
    def token(self):
        return Token(self.text, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add_with_index(self.text, self._index)
class StrongTextFragment(TextFragment):

    @property
    def token(self):
        return Token(self.text, token_type=TokenType.RLiterate.Strong, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add("**")
        text_version.add_with_index(self.text, self._index)
        text_version.add("**")
class EmphasisTextFragment(TextFragment):

    @property
    def token(self):
        return Token(self.text, token_type=TokenType.RLiterate.Emphasis, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add("*")
        text_version.add_with_index(self.text, self._index)
        text_version.add("*")
class CodeTextFragment(TextFragment):

    @property
    def token(self):
        return Token(self.text, token_type=TokenType.RLiterate.Code, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add("`")
        text_version.add_with_index(self.text, self._index)
        text_version.add("`")
class ReferenceTextFragment(TextFragment):

    @property
    def page_id(self):
        return self._text_fragment_dict["page_id"]

    @property
    def title(self):
        if self.text:
            return self.text
        if self._document.get_page(self.page_id) is not None:
            return self._document.get_page(self.page_id).title
        return self.page_id

    @property
    def token(self):
        return Token(self.title, token_type=TokenType.RLiterate.Reference, page_id=self.page_id, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add("[[")
        text_version.add_with_index(self.page_id, self._index)
        if self.text:
            text_version.add(":")
            text_version.add(self.text)
        text_version.add("]]")
class LinkTextFragment(TextFragment):

    @property
    def url(self):
        return self._text_fragment_dict["url"]

    @property
    def title(self):
        if self.text:
            return self.text
        return self.url

    @property
    def token(self):
        return Token(self.title, token_type=TokenType.RLiterate.Link, url=self.url, fragment_index=self._index)

    def fill_text_version(self, text_version):
        text_version.add("[")
        text_version.add_with_index(self.text, self._index)
        text_version.add("]")
        text_version.add("(")
        text_version.add(self.url)
        text_version.add(")")
class TextVersion(object):

    def __init__(self):
        self.text = ""
        self.indicies = {}
        self._index_prefix = []

    def get_selection(self, index):
        return self.indicies.get(index, (0, 0))

    @contextlib.contextmanager
    def index(self, index):
        self._index_prefix.append(index)
        yield
        self._index_prefix.pop(-1)

    def add_with_index(self, text, index):
        start = len(self.text)
        end = start + len(text)
        self.indicies[tuple(self._index_prefix + [index])] = (start, end)
        self.add(text)

    def add(self, text):
        self.text += text
class LegacyInlineTextParser(object):

    SPACE_RE = re.compile(r"\s+")
    PATTERNS = [
        (
            re.compile(r"\*\*(.+?)\*\*", flags=re.DOTALL),
            lambda parser, match: {
                "type": "strong",
                "text": match.group(1),
            }
        ),
        (
            re.compile(r"\*(.+?)\*", flags=re.DOTALL),
            lambda parser, match: {
                "type": "emphasis",
                "text": match.group(1),
            }
        ),
        (
            re.compile(r"`(.+?)`", flags=re.DOTALL),
            lambda parser, match: {
                "type": "code",
                "text": match.group(1),
            }
        ),
        (
            re.compile(r"\[\[(.+?)(:(.+?))?\]\]", flags=re.DOTALL),
            lambda parser, match: {
                "type": "reference",
                "text": match.group(3),
                "page_id": match.group(1),
            }
        ),
        (
            re.compile(r"\[(.*?)\]\((.+?)\)", flags=re.DOTALL),
            lambda parser, match: {
                "type": "link",
                "text": match.group(1),
                "url": match.group(2),
            }
        ),
    ]

    def parse(self, text):
        text = self._normalise_space(text)
        fragments = []
        partial = ""
        while text:
            result = self._get_special_fragment(text)
            if result is None:
                partial += text[0]
                text = text[1:]
            else:
                match, fragment = result
                if partial:
                    fragments.append({"type": "text", "text": partial})
                    partial = ""
                fragments.append(fragment)
                text = text[match.end(0):]
        if partial:
            fragments.append({"type": "text", "text": partial})
        return fragments

    def _normalise_space(self, text):
        return self.SPACE_RE.sub(" ", text).strip()

    def _get_special_fragment(self, text):
        for pattern, fn in self.PATTERNS:
            match = pattern.match(text)
            if match:
                return match, fn(self, match)
class LegacyListParser(object):

    ITEM_START_RE = re.compile(r"( *)([*]|\d+[.]) (.*)")

    def __init__(self, text):
        self.lines = text.strip().split("\n")

    def parse_items(self, level=0):
        items = []
        list_type = None
        while True:
            type_and_item = self.parse_item(level)
            if type_and_item is None:
                return list_type, items
            else:
                item_type, item = type_and_item
                if list_type is None:
                    list_type = item_type
                items.append(item)

    def parse_item(self, level):
        parts = self.consume_bodies()
        next_level = level + 1
        item_type = None
        if self.lines:
            match = self.ITEM_START_RE.match(self.lines[0])
            if match:
                matched_level = len(match.group(1))
                if matched_level >= level:
                    parts.append(match.group(3))
                    self.lines.pop(0)
                    parts.extend(self.consume_bodies())
                    next_level = matched_level + 1
                    if "*" in match.group(2):
                        item_type = "unordered"
                    else:
                        item_type = "ordered"
        if parts:
            child_type, children = self.parse_items(next_level)
            return (item_type, {
                "fragments": LegacyInlineTextParser().parse(" ".join(parts)),
                "children": children,
                "child_type": child_type,
            })

    def consume_bodies(self):
        bodies = []
        while self.lines:
            if self.ITEM_START_RE.match(self.lines[0]):
                break
            else:
                bodies.append(self.lines.pop(0))
        return bodies
class Project(Observable):

    def __init__(self, filepath):
        Observable.__init__(self)
        self._active_editor = None
        self._highlighted_variable = None
        self.title="{} ({})".format(
            os.path.basename(filepath),
            os.path.dirname(os.path.abspath(filepath))
        )
        self.theme = SolarizedTheme()
        self.document = Document.from_file(filepath)
        self.document.listen(self.notify_forwarder("document"))
        self.layout = Layout(os.path.join(
            os.path.dirname(filepath),
            ".{}.layout".format(os.path.basename(filepath))
        ))
        self.layout.listen(self.notify_forwarder("layout"))
        FileGenerator(self.document)
        self._foo = 600

    @property
    def PAGE_BODY_WIDTH(self):
        return self._foo

    @PAGE_BODY_WIDTH.setter
    def PAGE_BODY_WIDTH(self, value):
        with self.notify("document"):
            self._foo = value

    PAGE_PADDING = 13
    SHADOW_SIZE = 2
    PARAGRAPH_SPACE = 15
    CONTAINER_BORDER = PARAGRAPH_SPACE
    def get_page(self, *args, **kwargs):
        return self.document.get_page(*args, **kwargs)

    def get_paragraph(self, *args, **kwargs):
        return self.document.get_paragraph(*args, **kwargs)

    def add_page(self, *args, **kwargs):
        return self.document.add_page(*args, **kwargs)

    def add_paragraph(self, *args, **kwargs):
        return self.document.add_paragraph(*args, **kwargs)

    def get_undo_operation(self, *args, **kwargs):
        return self.document.get_undo_operation(*args, **kwargs)

    def get_redo_operation(self, *args, **kwargs):
        return self.document.get_redo_operation(*args, **kwargs)

    def rename_path(self, *args, **kwargs):
        return self.document.rename_path(*args, **kwargs)

    def lookup_variable(self, *args, **kwargs):
        return self.document.lookup_variable(*args, **kwargs)

    def rename_variable(self, *args, **kwargs):
        return self.document.rename_variable(*args, **kwargs)
    def toggle_collapsed(self, *args, **kwargs):
        return self.layout.toggle_collapsed(*args, **kwargs)

    def is_collapsed(self, *args, **kwargs):
        return self.layout.is_collapsed(*args, **kwargs)

    @property
    def columns(self):
        return self.layout.columns

    def is_open(self, *args, **kwargs):
        return self.layout.is_open(*args, **kwargs)

    def open_pages(self, *args, **kwargs):
        if self.active_editor is None:
            return self.layout.open_pages(*args, **kwargs)
        else:
            raise EditInProgress()

    def can_back(self, *args, **kwargs):
        return self.layout.can_back(*args, **kwargs)

    def back(self, *args, **kwargs):
        return self.layout.back(*args, **kwargs)

    def can_forward(self, *args, **kwargs):
        return self.layout.can_forward(*args, **kwargs)

    def forward(self, *args, **kwargs):
        return self.layout.forward(*args, **kwargs)

    def get_hoisted_page(self, *args, **kwargs):
        return self.layout.get_hoisted_page(*args, **kwargs)

    def set_hoisted_page(self, *args, **kwargs):
        return self.layout.set_hoisted_page(*args, **kwargs)
    def get_style(self, *args, **kwargs):
        return self.theme.get_style(*args, **kwargs)
    @property
    def active_editor(self):
        return self._active_editor

    @active_editor.setter
    def active_editor(self, editor):
        with self.notify("editor"):
            self._active_editor = editor
    @property
    def highlighted_variable(self):
        return self._highlighted_variable

    @highlighted_variable.setter
    def highlighted_variable(self, variable_id):
        with self.notify("highlights"):
            self._highlighted_variable = variable_id
class EditInProgress(Exception):
    pass
class Layout(Observable):
    def __init__(self, path):
        Observable.__init__(self)
        self.listen(lambda event: write_json_to_file(path, self.data))
        if os.path.exists(path):
            self.data = load_json_from_file(path)
        else:
            self.data = {}
        self._toc = ensure_key(self.data, "toc", {})
        self._toc_collapsed = ensure_key(self._toc, "collapsed", [])
        self._workspace = ensure_key(self.data, "workspace", {})
        self._workspace_columns = ensure_key(self._workspace, "columns", [])
        self._workspace_columns_history = History(copy.deepcopy(self._workspace_columns), size=20)
        if "scratch" in self._workspace:
            if not self._workspace["columns"]:
                self._workspace["columns"] = [self._workspace["scratch"]]
            del self._workspace["scratch"]
    def get_hoisted_page(self):
        return self._toc.get("hoisted_page_id", None)

    def set_hoisted_page(self, page_id):
        with self.notify("toc"):
            self._toc["hoisted_page_id"] = page_id
    def is_collapsed(self, page_id):
        return page_id in self._toc_collapsed

    def toggle_collapsed(self, page_id):
        with self.notify("toc"):
            if page_id in self._toc_collapsed:
                self._toc_collapsed.remove(page_id)
            else:
                self._toc_collapsed.append(page_id)
    @property
    def columns(self):
        return [column[:] for column in self._workspace_columns]

    def open_pages(self, page_ids, column_index=None):
        with self.notify("workspace"):
            with self._workspace_columns_history.new_value() as value:
                if column_index is None:
                    column_index = len(self._workspace_columns)
                value[column_index:] = [page_ids[:]]
                self._workspace_columns[:] = value

    def can_back(self):
        return self._workspace_columns_history.can_back()

    def back(self):
        with self.notify("workspace"):
            self._workspace_columns_history.back()
            self._workspace_columns[:] = self._workspace_columns_history.value

    def can_forward(self):
        return self._workspace_columns_history.can_forward()

    def forward(self):
        with self.notify("workspace"):
            self._workspace_columns_history.forward()
            self._workspace_columns[:] = self._workspace_columns_history.value

    def is_open(self, page_id):
        for column in self.columns:
            if page_id in column:
                return True
        return False
class BaseTheme(object):

    def get_style(self, token_type):
        if token_type in self.styles:
            return self.styles[token_type]
        return self.get_style(token_type.parent)
class SolarizedTheme(BaseTheme):

    base03  = "#002b36"
    base02  = "#073642"
    base01  = "#586e75"
    base00  = "#657b83"
    base0   = "#839496"
    base1   = "#93a1a1"
    base2   = "#eee8d5"
    base3   = "#fdf6e3"
    yellow  = "#b58900"
    orange  = "#cb4b16"
    red     = "#dc322f"
    magenta = "#d33682"
    violet  = "#6c71c4"
    blue    = "#268bd2"
    cyan    = "#2aa198"
    green   = "#859900"

    text    = "#2e3436"

    styles = {
        TokenType:                     Style(color=base00),
        TokenType.Keyword:             Style(color=green),
        TokenType.Keyword.Constant:    Style(color=cyan),
        TokenType.Keyword.Declaration: Style(color=blue),
        TokenType.Keyword.Namespace:   Style(color=orange),
        TokenType.Name.Builtin:        Style(color=red),
        TokenType.Name.Builtin.Pseudo: Style(color=blue),
        TokenType.Name.Class:          Style(color=blue),
        TokenType.Name.Decorator:      Style(color=blue),
        TokenType.Name.Entity:         Style(color=violet),
        TokenType.Name.Exception:      Style(color=yellow),
        TokenType.Name.Function:       Style(color=blue),
        TokenType.String:              Style(color=cyan),
        TokenType.Number:              Style(color=cyan),
        TokenType.Operator.Word:       Style(color=green),
        TokenType.Comment:             Style(color=base1),
        TokenType.RLiterate:           Style(color=text),
        TokenType.RLiterate.Emphasis:  Style(color=text, italic=True),
        TokenType.RLiterate.Strong:    Style(color=text, bold=True),
        TokenType.RLiterate.Code:      Style(color=text, monospace=True),
        TokenType.RLiterate.Link:      Style(color=blue, underlined=True),
        TokenType.RLiterate.Reference: Style(color=blue, italic=True),
        TokenType.RLiterate.Path:      Style(color=text, italic=True, bold=True),
        TokenType.RLiterate.Chunk:     Style(color=magenta, bold=True),
        TokenType.RLiterate.Sep:       Style(color=base1),
    }
class MainFrame(wx.Frame):

    def __init__(self, project):
        wx.Frame.__init__(
            self,
            None,
            size=(920, 500),
            title="{} - RLiterate".format(project.title)
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._create_main_panel(project), flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

    def _create_main_panel(self, project):
        self._panel = wx.Panel(self)
        self.SetToolBar(ToolBar(self._panel, project))
        self._focus_panel = wx.Panel(self)
        toc = TableOfContents(self._panel, project)
        workspace = Workspace(self._panel, project)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._focus_panel)
        sizer.Add(toc, flag=wx.EXPAND, proportion=0)
        sizer.Add(workspace, flag=wx.EXPAND, proportion=1)
        self._panel.SetSizer(sizer)
        return self._panel

    def ChildReRendered(self):
        self.Layout()
        self._focus_panel.SetFocus()
class ToolBar(wx.ToolBar):

    def __init__(self, parent, project, *args, **kwargs):
        wx.ToolBar.__init__(self, parent, *args, **kwargs)
        self._init_project(project)
        self._init_tools()

    def _init_project(self, project):
        self.project = project
        self.project.listen(
            lambda event: self._tool_groups.populate(self),
            "document", "layout", "editor"
        )

    def _init_tools(self):
        main_frame = self.GetTopLevelParent()
        self._tool_groups = ToolGroups(main_frame)
        editor_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is not None
        )
        editor_group.add_tool(
            wx.ART_FILE_SAVE,
            lambda: self.project.active_editor.Save(),
            short_help="Save",
            shortcuts=[
                (wx.ACCEL_CTRL, ord('S')),
                (wx.ACCEL_CTRL, wx.WXK_RETURN),
            ]
        )
        editor_group.add_tool(
            wx.ART_CROSS_MARK,
            lambda: self.project.active_editor.Cancel(),
            short_help="Cancel",
            shortcuts=[
                (wx.ACCEL_CTRL, ord('G')),
                (wx.ACCEL_NORMAL, wx.WXK_ESCAPE),
            ]
        )
        navigation_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is None
        )
        navigation_group.add_tool(
            wx.ART_GO_BACK,
            lambda: self.project.back(),
            short_help="Go back",
            enabled_fn=lambda: self.project.can_back()
        )
        navigation_group.add_tool(
            wx.ART_GO_FORWARD,
            lambda: self.project.forward(),
            short_help="Go forward",
            enabled_fn=lambda: self.project.can_forward()
        )
        undo_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is None
        )
        undo_group.add_tool(
            wx.ART_UNDO,
            lambda: self.project.get_undo_operation()[1](),
            short_help=lambda: "Undo" if self.project.get_undo_operation() is None else "Undo '{}'".format(self.project.get_undo_operation()[0]),
            enabled_fn=lambda: self.project.get_undo_operation() is not None,
            shortcuts=[
                (wx.ACCEL_CTRL, ord('Z')),
            ]
        )
        undo_group.add_tool(
            wx.ART_REDO,
            lambda: self.project.get_redo_operation()[1](),
            short_help=lambda: "Redo" if self.project.get_redo_operation() is None else "Redo '{}'".format(self.project.get_redo_operation()[0]),
            enabled_fn=lambda: self.project.get_redo_operation() is not None
        )
        settings_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is None
        )
        settings_group.add_tool(
            wx.ART_HELP_SETTINGS,
            lambda: SettingsDialog(main_frame, self.project).Show(),
            short_help="Settings"
        )
        quit_group = self._tool_groups.add_group()
        quit_group.add_tool(
            wx.ART_QUIT,
            lambda: main_frame.Close(),
            short_help="Quit",
            shortcuts=[
                (wx.ACCEL_CTRL, ord('Q')),
            ]
        )
        self._tool_groups.populate(self)
class ToolGroups(object):

    def __init__(self, frame):
        self._frame = frame
        self._tool_groups = []

    def add_group(self, *args, **kwargs):
        group = ToolGroup(self._frame, *args, **kwargs)
        self._tool_groups.append(group)
        return group

    def populate(self, toolbar):
        items = []
        toolbar.ClearTools()
        first = True
        for group in self._tool_groups:
            if group.is_active():
                if not first:
                    toolbar.AddSeparator()
                first = False
                group.populate(toolbar)
                items.extend(group.accelerator_entries())
        toolbar.Realize()
        self._frame.SetAcceleratorTable(wx.AcceleratorTable(items))
class ToolGroup(object):

    def __init__(self, frame, active_fn=None):
        self._tools = []
        self._frame = frame
        self._active_fn = active_fn

    def add_tool(self, *args, **kwargs):
        self._tools.append(Tool(self._frame, *args, **kwargs))

    def is_active(self):
        if self._active_fn is None:
            return True
        else:
            return self._active_fn()

    def accelerator_entries(self):
        entries = []
        for tool in self._tools:
            entries.extend(tool.accelerator_entries())
        return entries

    def populate(self, toolbar):
        for tool in self._tools:
            tool.populate(toolbar)
class Tool(object):

    def __init__(self, frame, art, action_fn, short_help="", enabled_fn=None, shortcuts=[]):
        self.id = wx.NewId()
        frame.Bind(wx.EVT_MENU, self._on_action, id=self.id)
        self.art = art
        self.short_help = short_help
        self.action_fn = action_fn
        self.enabled_fn = enabled_fn
        self.shortcuts = shortcuts

    def _on_action(self, event):
        if self.action_fn is not None:
            self.action_fn()

    def _is_enabled(self):
        if self.enabled_fn is None:
            return True
        else:
            return self.enabled_fn()

    def accelerator_entries(self):
        return [wx.AcceleratorEntry(a, b, self.id) for (a, b) in self.shortcuts]

    def populate(self, toolbar):
        toolbar.AddSimpleTool(
            self.id,
            wx.ArtProvider.GetBitmap(
                self.art,
                wx.ART_BUTTON,
                (24, 24)
            )
        )
        toolbar.EnableTool(self.id, self._is_enabled())
        if callable(self.short_help):
            text = self.short_help()
        else:
            text = self.short_help
        if self.shortcuts:
            text = "{} ({})".format(
                text,
                " / ".join(x.ToString() for x in self.accelerator_entries())
            )
        toolbar.SetToolShortHelp(self.id, text)
class TableOfContents(wx.Panel):

    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, size=(250, -1))
        self._init_project(project)
        self.SetDropTarget(TableOfContentsDropTarget(self, self.project))
        self._render()

    def _init_project(self, project):
        self.project = project
        self.project.listen(
            lambda event: self._re_render(),
            "document", "layout.toc", "layout.workspace"
        )

    def _render(self):
        with flicker_free_drawing(self):
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.sizer)
            self.unhoist_button = None
            self.page_sizer = wx.BoxSizer(wx.VERTICAL)
            self.page_container = CompactScrolledWindow(self)
            self.page_container.SetSizer(self.page_sizer)
            self.sizer.Add(self.page_container, flag=wx.EXPAND, proportion=1)
            self.SetBackgroundColour((255, 255, 255))
            self._re_render()

    def _re_render(self):
        with flicker_free_drawing(self):
            self.drop_points = []
            if self.unhoist_button is not None:
                self.unhoist_button.Destroy()
                self.unhoist_button = None
            self.page_sizer.Clear(True)
            self._render_unhoist_button()
            self._render_page_container()
            self.GetTopLevelParent().ChildReRendered()
    def _render_unhoist_button(self):
        if self._get_hoisted_page() is not None:
            self.unhoist_button = wx.Button(self, label="unhoist")
            self.unhoist_button.Bind(
                wx.EVT_BUTTON,
                lambda event: self.project.set_hoisted_page(None)
            )
            self.sizer.Insert(0, self.unhoist_button, flag=wx.EXPAND)
    def _render_page_container(self):
        if self._get_hoisted_page() is None:
            self._render_page(self.project.get_page())
        else:
            self._render_page(self._get_hoisted_page())

    def _get_hoisted_page(self):
        if self.project.get_hoisted_page() is None:
            return None
        else:
            return self.project.get_page(self.project.get_hoisted_page())

    def _render_page(self, page, indentation=0):
        is_collapsed = self.project.is_collapsed(page.id)
        self.page_sizer.Add(
            TableOfContentsRow(self.page_container, self.project, page, indentation),
            flag=wx.EXPAND
        )
        divider = Divider(self.page_container, padding=0, height=2)
        self.page_sizer.Add(
            divider,
            flag=wx.EXPAND
        )
        if is_collapsed or len(page.children) == 0:
            before_page_id = None
        else:
            before_page_id = page.children[0].id
        self.drop_points.append(TableOfContentsDropPoint(
            divider=divider,
            indentation=indentation+1,
            parent_page_id=page.id,
            before_page_id=before_page_id
        ))
        if not is_collapsed:
            for child, next_child in pairs(page.children):
                divider = self._render_page(child, indentation+1)
                self.drop_points.append(TableOfContentsDropPoint(
                    divider=divider,
                    indentation=indentation+1,
                    parent_page_id=page.id,
                    before_page_id=None if next_child is None else next_child.id
                ))
        return divider
    def FindClosestDropPoint(self, screen_pos):
        client_pos = (client_x, client_y) = self.page_container.ScreenToClient(screen_pos)
        if self.page_container.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
            y_distances = defaultdict(list)
            for drop_point in self.drop_points:
                y_distances[drop_point.y_distance_to(client_y)].append(drop_point)
            if y_distances:
                return min(
                    y_distances[min(y_distances.keys())],
                    key=lambda drop_point: drop_point.x_distance_to(client_x)
                )
class TableOfContentsDropPoint(object):

    def __init__(self, divider, indentation, parent_page_id, before_page_id):
        self.divider = divider
        self.indentation = indentation
        self.parent_page_id = parent_page_id
        self.before_page_id = before_page_id

    def x_distance_to(self, x):
        left_padding = TableOfContentsButton.SIZE+1+TableOfContentsRow.BORDER
        span_x_center = left_padding + TableOfContentsRow.INDENTATION_SIZE * (self.indentation + 1.5)
        return abs(span_x_center - x)

    def y_distance_to(self, y):
        return abs(self.divider.Position.y + self.divider.Size[1]/2 - y)

    def Show(self):
        self.divider.Show(sum([
            TableOfContentsRow.BORDER,
            TableOfContentsButton.SIZE,
            1,
            self.indentation*TableOfContentsRow.INDENTATION_SIZE,
        ]))

    def Hide(self):
        self.divider.Hide()
class TableOfContentsDropTarget(DropPointDropTarget):

    def __init__(self, toc, project):
        DropPointDropTarget.__init__(self, toc, "page")
        self.project = project

    def OnDataDropped(self, dropped_page, drop_point):
        self.project.get_page(dropped_page["page_id"]).move(
            parent_page_id=drop_point.parent_page_id,
            before_page_id=drop_point.before_page_id
        )
class TableOfContentsRow(wx.Panel):

    def __init__(self, parent, project, page, indentation):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.page = page
        self.indentation = indentation
        self._render()

    BORDER = 2
    INDENTATION_SIZE = 16

    def _render(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add((self.indentation*self.INDENTATION_SIZE, 1))
        if self.page.children:
            button = TableOfContentsButton(self, self.project, self.page)
            self.sizer.Add(button, flag=wx.EXPAND|wx.LEFT, border=self.BORDER)
        else:
            self.sizer.Add((TableOfContentsButton.SIZE+1+self.BORDER, 1))
        if self.project.is_open(self.page.id):
            self.Font = create_font(bold=True)
        text = wx.StaticText(self)
        text.SetLabelText(self.page.title)
        self.sizer.Add(text, flag=wx.ALL, border=self.BORDER)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        for helper in [MouseEventHelper(self), MouseEventHelper(text)]:
            helper.OnClick = self._on_click
            helper.OnRightClick = self._on_right_click
            helper.OnDrag = self._on_drag
    def _on_click(self):
        open_pages_gui(self, self.project, [self.page.id], column_index=0)

    def _on_right_click(self, event):
        menu = PageContextMenu(self.project, self.page)
        self.PopupMenu(menu)
        menu.Destroy()

    def _on_drag(self):
        data = RliterateDataObject("page", {
            "page_id": self.page.id,
        })
        drag_source = wx.DropSource(self)
        drag_source.SetData(data)
        result = drag_source.DoDragDrop(wx.Drag_DefaultMove)

    def _on_enter_window(self, event):
        self.SetBackgroundColour((240, 240, 240))

    def _on_leave_window(self, event):
        self.SetBackgroundColour((255, 255, 255))
class TableOfContentsButton(wx.Panel):

    SIZE = 16

    def __init__(self, parent, project, page):
        wx.Panel.__init__(self, parent, size=(self.SIZE+1, -1))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.project = project
        self.page = page
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def OnLeftDown(self, event):
        self.project.toggle_collapsed(self.page.id)

    def OnPaint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.BLACK_BRUSH)
        render = wx.RendererNative.Get()
        (w, h) = self.Size
        render.DrawTreeItemButton(
            self,
            dc,
            (0, (h-self.SIZE)/2, self.SIZE, self.SIZE),
            flags=0 if self.project.is_collapsed(self.page.id) else wx.CONTROL_EXPANDED
        )
class PageContextMenu(wx.Menu):

    def __init__(self, project, page):
        wx.Menu.__init__(self)
        self.project = project
        self.page = page
        self.child_ids = [page.id]+[child.id for child in page.children]
        self._create_menu()

    def _create_menu(self):
        self.Bind(
            wx.EVT_MENU,
            lambda event: open_pages_gui(self, self.project, [self.page.id], column_index=0),
            self.Append(wx.NewId(), "Open")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: open_pages_gui(self, self.project, [self.page.id]),
            self.Append(wx.NewId(), "Open append")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: open_pages_gui(self, self.project, self.child_ids, column_index=0),
            self.Append(wx.NewId(), "Open with children")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: open_pages_gui(self, self.project, self.child_ids),
            self.Append(wx.NewId(), "Open with children append")
        )
        self.AppendSeparator()
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.add_page(parent_id=self.page.id),
            self.Append(wx.NewId(), "Add child")
        )
        self.AppendSeparator()
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.set_hoisted_page(self.page.id),
            self.Append(wx.NewId(), "Hoist")
        )
        self.AppendSeparator()
        self.Bind(
            wx.EVT_MENU,
            lambda event: set_clipboard_text(self.page.id),
            self.Append(wx.NewId(), "Copy id")
        )
        self.AppendSeparator()
        delete_item = self.Append(wx.NewId(), "Delete")
        delete_item.Enable(self.page.id != self.project.get_page().id)
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.page.delete(),
            delete_item
        )
class Workspace(CompactScrolledWindow):

    def __init__(self, parent, project):
        CompactScrolledWindow.__init__(self, parent, style=wx.HSCROLL)
        self._init_project(project)
        self.SetDropTarget(WorkspaceDropTarget(self, self.project))
        self._render()

    def _init_project(self, project):
        self.project = project
        self.project.listen(
            lambda event: self._re_render(),
            "document",
            "layout.workspace",
            "highlights"
        )

    def _render(self):
        with flicker_free_drawing(self):
            self.SetBackgroundColour((200, 200, 200))
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer.AddSpacer(self.project.PAGE_PADDING)
            self.SetSizer(self.sizer)
            self.columns = []
            wx.CallAfter(self._re_render)

    def _re_render(self):
        with flicker_free_drawing(self):
            column_count_changed = self._ensure_num_columns(len(self.project.columns))
            last_column_changed_pages = False
            for index, page_ids in enumerate(self.project.columns):
                last_column_changed_pages = self.columns[index].SetPages(page_ids)
            self.GetTopLevelParent().ChildReRendered()
            if column_count_changed or last_column_changed_pages:
                self.ScrollToEnd()

    def _ensure_num_columns(self, num):
        count_changed = False
        while len(self.columns) > num:
            count_changed = True
            self.columns.pop(-1).Destroy()
        while len(self.columns) < num:
            count_changed = True
            self.columns.append(self._add_column())
        return count_changed

    def _add_column(self):
        column = Column(self, project=self.project, index=len(self.columns))
        self.sizer.Add(column, flag=wx.EXPAND)
        return column
    def FindClosestDropPoint(self, screen_pos):
        return find_first(
            self.columns,
            lambda column: column.FindClosestDropPoint(screen_pos)
        )
class WorkspaceDropTarget(DropPointDropTarget):

    def __init__(self, workspace, project):
        DropPointDropTarget.__init__(self, workspace, "paragraph")
        self.project = project

    def OnDataDropped(self, dropped_paragraph, drop_point):
        self.project.get_paragraph(
            dropped_paragraph["page_id"],
            dropped_paragraph["paragraph_id"]
        ).move(
            target_page=drop_point.page_id,
            before_paragraph=drop_point.next_paragraph_id
        )
class Column(CompactScrolledWindow):

    def __init__(self, parent, project, index):
        CompactScrolledWindow.__init__(
            self,
            parent,
            style=wx.VSCROLL,
            size=self._get_size(project)
        )
        self.project = project
        self.index = index
        self._page_ids = []
        self._setup_layout()
        self.Bind(EVT_HOVERED_TOKEN_CHANGED, self._on_hovered_token_changed)
        self.Bind(EVT_TOKEN_CLICK, self._on_token_click)

    def _on_hovered_token_changed(self, event):
        if event.token is not None and event.token.token_type in [
            TokenType.RLiterate.Link,
            TokenType.RLiterate.Reference,
        ]:
            event.widget.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            event.widget.SetDefaultCursor()

    def _on_token_click(self, event):
        if event.token.token_type == TokenType.RLiterate.Reference:
            self.OpenPage(event.token.extra["page_id"])
        elif event.token.token_type == TokenType.RLiterate.Link:
            webbrowser.open(event.token.extra["url"])

    def OpenPage(self, page_id):
        open_pages_gui(self, self.project,
            [page_id],
            column_index=self.index+1
        )

    def _setup_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def _get_size(self, project):
        return (
            project.PAGE_BODY_WIDTH+
            2*project.CONTAINER_BORDER+
            project.PAGE_PADDING+
            project.SHADOW_SIZE,
            -1
        )

    def SetPages(self, page_ids):
        self.containers = []
        self.MinSize = self._get_size(self.project)
        self.sizer.Clear(True)
        self.sizer.AddSpacer(self.project.PAGE_PADDING)
        for page_id in page_ids:
            if self.project.get_page(page_id) is not None:
                container = PageContainer(self, self.project, page_id)
                self.sizer.Add(
                    container,
                    flag=wx.RIGHT|wx.BOTTOM|wx.EXPAND,
                    border=self.project.PAGE_PADDING
                )
                self.containers.append(container)
        if page_ids == self._page_ids:
            return False
        else:
            self.ScrollToBeginning()
            self._page_ids = page_ids
            return True

    def FindClosestDropPoint(self, screen_pos):
        return find_first(
            self.containers,
            lambda container: container.FindClosestDropPoint(screen_pos)
        )
class PageContainer(wx.Panel):

    def __init__(self, parent, project, page_id):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.page_id = page_id
        self._render()

    def _render(self):
        self.SetBackgroundColour((150, 150, 150))
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_container = wx.Panel(self)
        self.inner_container.SetBackgroundColour((255, 255, 255))
        self.inner_container.SetSizer(self.inner_sizer)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(
            self.inner_container,
            flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM,
            border=self.project.SHADOW_SIZE
        )
        self.SetSizer(self.sizer)
        self.inner_sizer.AddSpacer(self.project.CONTAINER_BORDER)
        self.page = PagePanel(self.inner_container, self.project, self.page_id)
        self.inner_sizer.Add(
            self.page,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,
            border=self.project.CONTAINER_BORDER
        )

    def FindClosestDropPoint(self, screen_pos):
        return self.page.FindClosestDropPoint(screen_pos)
class PagePanel(wx.Panel):

    def __init__(self, parent, project, page_id):
        wx.Panel.__init__(self, parent, size=(
            project.PAGE_BODY_WIDTH,
            -1
        ))
        self.project = project
        self.page_id = page_id
        self._render()

    def _render(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.drop_points = []
        page = self.project.get_page(self.page_id)
        divider = self._render_paragraph(Title(self, self.project, page))
        for paragraph in page.paragraphs:
            self.drop_points.append(PageDropPoint(
                divider=divider,
                page_id=self.page_id,
                next_paragraph_id=paragraph.id
            ))
            divider = self._render_paragraph({
                "text": Text,
                "quote": Quote,
                "list": List,
                "code": Code,
                "image": Image,
                "factory": Factory,
            }[paragraph.type](self, self.project, self.page_id, paragraph))
        self.drop_points.append(PageDropPoint(
            divider=divider,
            page_id=self.page_id,
            next_paragraph_id=None
        ))
        self._render_add_button()

    def _render_paragraph(self, paragraph):
        self.sizer.Add(paragraph, flag=wx.EXPAND)
        divider = Divider(self, padding=(self.project.PARAGRAPH_SPACE-3)/2, height=3)
        self.sizer.Add(divider, flag=wx.EXPAND)
        return divider

    def _render_add_button(self):
        add_button = wx.BitmapButton(
            self,
            bitmap=wx.ArtProvider.GetBitmap(
                wx.ART_ADD_BOOKMARK,
                wx.ART_BUTTON,
                (16, 16)
            ),
            style=wx.NO_BORDER
        )
        add_button.Bind(wx.EVT_BUTTON, self._on_add_button)
        self.sizer.Add(
            add_button,
            flag=wx.TOP|wx.ALIGN_RIGHT,
            border=self.project.PARAGRAPH_SPACE
        )

    def _on_add_button(self, event):
        self.project.add_paragraph(self.page_id)
    def FindClosestDropPoint(self, screen_pos):
        client_pos = (client_x, client_y) = self.ScreenToClient(screen_pos)
        if self.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
            return min_or_none(
                self.drop_points,
                key=lambda drop_point: drop_point.y_distance_to(client_y)
            )
class PageDropPoint(object):

    def __init__(self, divider, page_id, next_paragraph_id):
        self.divider = divider
        self.page_id = page_id
        self.next_paragraph_id = next_paragraph_id

    def y_distance_to(self, y):
        return abs(self.divider.Position.y + self.divider.Size[1]/2 - y)

    def Show(self):
        self.divider.Show()

    def Hide(self):
        self.divider.Hide()
class Title(Editable):

    def __init__(self, parent, project, page):
        self.page = page
        Editable.__init__(self, parent, project)

    def CreateView(self):
        self.Font = create_font(size=16)
        view = TokenView(
            self,
            self.project,
            [Token(self.page.title)],
            max_width=self.project.PAGE_BODY_WIDTH
        )
        MouseEventHelper.bind(
            [view],
            double_click=lambda event: self._post_edit_start_from_token_view(event.Position)
        )
        return view

    def _post_edit_start_from_token_view(self, pos):
        edge_token = self.view.GetClosestToken(pos)
        selection = (0, 0)
        if edge_token is not None:
            edge, token = edge_token
            start = token.index
            if edge < 0:
                selection = (start, start)
            elif edge > 0:
                selection = (start+len(token.text), start+len(token.text))
            else:
                selection = (start, start+len(token.text))
        post_edit_start(self.view, selection=selection)

    def CreateEdit(self, extra):
        edit = SelectionableTextCtrl(
            self,
            style=wx.TE_PROCESS_ENTER,
            value=self.page.title
        )
        edit.Save = lambda: self.page.set_title(self.edit.Value)
        edit.SetSelection(*extra["selection"])
        return edit
class Text(ParagraphBase):

    def CreateView(self):
        return TextView(
            self,
            self.project,
            [
                token.with_extra("text_index", (token.extra["fragment_index"],))
                for token in self.paragraph.tokens
            ],
            self
        )

    def CreateEdit(self, extra):
        return TextEdit(
            self,
            self.project,
            self.paragraph,
            self.view,
            extra
        )

    def AddContextMenuItems(self, menu):
        menu.AppendItem(
            "To quote",
            lambda: self.paragraph.update({"type": "quote"})
        )
class TextView(TokenView):

    def __init__(self, parent, project, tokens, base, indented=0):
        TokenView.__init__(
            self,
            parent,
            project,
            tokens,
            line_height=1.2,
            max_width=project.PAGE_BODY_WIDTH-indented,
            skip_extra_space=True
        )
        MouseEventHelper.bind(
            [self],
            drag=base.DoDragDrop,
            right_click=lambda event: base.ShowContextMenu(),
            double_click=lambda event: post_edit_start(self, token=self.GetToken(event.Position)),
            move=self._on_mouse_move,
            click=self._on_click
        )
        self.token = None

    def _on_mouse_move(self, event):
        token = self.GetToken(event.Position)
        if token is not self.token:
            self.token = token
            post_hovered_token_changed(self, self.token)

    def _on_click(self):
        if self.token is not None:
            post_token_click(self, self.token)
class TextEdit(MultilineTextCtrl):

    def __init__(self, parent, project, paragraph, view, extra):
        MultilineTextCtrl.__init__(
            self,
            parent,
            value=paragraph.text_version,
            size=(-1, view.Size[1])
        )
        if extra.get("token", None) is None:
            self.SetSelection(0, 0)
        else:
            index = paragraph.get_text_index(extra["token"].extra["text_index"])
            start = index + extra["token"].index
            end = start + len(extra["token"].text)
            self.SetSelection(start, end)
        self.Font = create_font(monospace=True)
        self.project = project
        self.paragraph = paragraph

    def Save(self):
        self.paragraph.text_version = self.Value
class Quote(Text):

    INDENT = 20

    def CreateView(self):
        view = wx.Panel(self)
        self.text_view = TextView(
            view,
            self.project,
            [
                token.with_extra("text_index", (token.extra["fragment_index"],))
                for token in self.paragraph.tokens
            ],
            self,
            indented=self.INDENT
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((self.INDENT, 1))
        sizer.Add(self.text_view, flag=wx.EXPAND, proportion=1)
        view.SetSizer(sizer)
        return view

    def AddContextMenuItems(self, menu):
        menu.AppendItem(
            "To text",
            lambda: self.paragraph.update({"type": "text"})
        )
class List(ParagraphBase):

    INDENT = 20

    def CreateView(self):
        view = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_items(view, sizer, self.paragraph.children, self.paragraph.child_type)
        view.SetSizer(sizer)
        return view

    def CreateEdit(self, extra):
        return TextEdit(
            self,
            self.project,
            self.paragraph,
            self.view,
            extra
        )

    def add_items(self, view, sizer, items, child_type, indicies=[]):
        for index, item in enumerate(items):
            inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
            inner_sizer.Add((self.INDENT*len(indicies), 1))
            bullet = self._create_bullet_widget(view, child_type, index)
            inner_sizer.Add(bullet)
            inner_sizer.Add(
                TextView(
                    view,
                    self.project,
                    [
                        token.with_extra(
                            "text_index",
                            tuple(indicies+[index]+[token.extra["fragment_index"]])
                        )
                        for token in item.tokens
                    ],
                    self,
                    indented=self.INDENT*len(indicies)+bullet.GetMinSize()[0]
                ),
                proportion=1
            )
            sizer.Add(inner_sizer, flag=wx.EXPAND)
            self.add_items(view, sizer, item.children, item.child_type, indicies+[index])

    def _create_bullet_widget(self, view, list_type, index):
        return TokenView(
            view,
            self.project,
            [Token(self._get_bullet_text(list_type, index))]
        )

    def _get_bullet_text(self, list_type, index):
        if list_type == "ordered":
            return "{}. ".format(index + 1)
        else:
            return u"\u2022 "
class Code(ParagraphBase):

    def CreateView(self):
        return CodeView(self, self.project, self.paragraph, self)

    def CreateEdit(self, extra):
        return CodeEditor(self, self.project, self.paragraph, self.view, extra)
class CodeView(wx.Panel):

    BORDER = 0
    PADDING = 5

    def __init__(self, parent, project, paragraph, base):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.paragraph = paragraph
        self.base = base
        self._create_gui()

    def _create_gui(self):
        self.Font = create_font(monospace=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        if not self.paragraph.path.is_empty:
            sizer.Add(
                self._create_path(),
                flag=wx.ALL|wx.EXPAND, border=self.BORDER
            )
        sizer.Add(
            self._create_code(),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetSizer(sizer)
        self.SetBackgroundColour((243, 236, 219))
    def _create_path(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((248, 241, 223))
        self.path_token_view = TokenView(
            panel,
            self.project,
            self._create_path_tokens(self.paragraph.path),
            max_width=self.project.PAGE_BODY_WIDTH-2*self.PADDING
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.path_token_view, flag=wx.ALL|wx.EXPAND, border=self.PADDING)
        panel.SetSizer(sizer)
        self.base.BindMouse(
            self,
            [panel],
            double_click=lambda event: post_edit_start(self, subpath=None)
        )
        self.base.BindMouse(
            self,
            [self.path_token_view],
            move=self._token_move,
            right_click=self._token_right_click,
            double_click=self._path_double_click
        )
        return panel

    def _create_path_tokens(self, path):
        tokens = []
        last_subpath = None
        for (index, (name, subpath)) in enumerate(path.filepaths):
            if index > 0:
                tokens.append(Token(
                    "/",
                    token_type=TokenType.RLiterate.Sep,
                    prev_subpath=last_subpath,
                    next_subpath=subpath
                ))
            tokens.append(Token(
                name,
                token_type=TokenType.RLiterate.Path,
                subpath=subpath
            ))
            last_subpath = subpath
        if path.has_both():
            tokens.append(Token(
                " ",
                token_type=TokenType.RLiterate.Sep,
                prev_subpath=last_subpath,
                next_subpath=list(path.chunkpaths)[0][1]
            ))
            for (index, (name, subpath)) in enumerate(path.chunkpaths):
                if index > 0:
                    tokens.append(Token(
                        "/",
                        token_type=TokenType.RLiterate.Sep,
                        prev_subpath=last_subpath,
                        next_subpath=subpath
                    ))
                tokens.append(Token(
                    name,
                    token_type=TokenType.RLiterate.Chunk,
                    subpath=subpath
                ))
                last_subpath = subpath
        return tokens
    def _create_code(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((253, 246, 227))
        self.body_token_view = TokenView(
            panel,
            self.project,
            self._highlight_variables(self.paragraph.tokens),
            max_width=self.project.PAGE_BODY_WIDTH-2*self.PADDING
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.body_token_view, flag=wx.ALL|wx.EXPAND, border=self.PADDING, proportion=1)
        panel.SetSizer(sizer)
        self.base.BindMouse(
            self,
            [panel],
            double_click=lambda event: post_edit_start(self, body_token=None)
        )
        self.base.BindMouse(
            self,
            [self.body_token_view],
            move=self._token_move,
            right_click=self._token_right_click,
            double_click=self._body_double_click
        )
        return panel

    def _highlight_variables(self, tokens):
        def foo(token):
            if self.project.highlighted_variable is not None and self.project.highlighted_variable == token.extra.get("variable"):
                return token.with_extra("highlight", True)
            return token
        return [foo(token) for token in tokens]
    def _token_move(self, event):
        token = event.EventObject.GetToken(event.Position)
        if token is not None and token.extra.get("subpath") is not None:
            event.EventObject.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        elif token is not None and token.extra.get("variable") is not None:
            event.EventObject.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            event.EventObject.SetDefaultCursor()
        return CONTINUE_PROCESSING

    def _token_right_click(self, event):
        token = event.EventObject.GetToken(event.Position)
        if token is not None and token.extra.get("subpath") is not None:
            menu = ParagraphContextMenu()
            menu.AppendItem(
                "Rename '{}'".format(token.extra["subpath"].last),
                lambda: show_text_entry(
                    self,
                    title="Rename path",
                    body="Rename '{}'".format(token.extra["subpath"].last),
                    value=token.extra["subpath"].last,
                    ok_fn=lambda value: self.project.rename_path(
                        token.extra["subpath"],
                        value
                    )
                )
            )
            self.PopupMenu(menu)
            menu.Destroy()
        elif token is not None and token.extra.get("variable") is not None:
            rename_value = self.project.lookup_variable(token.extra["variable"]) or token.extra["variable"]
            rename_message = "Rename '{}'".format(rename_value)
            menu = ParagraphContextMenu()
            menu.AppendItem(
                rename_message,
                lambda: show_text_entry(
                    self,
                    title="Rename variable",
                    body=rename_message,
                    value=rename_value,
                    ok_fn=lambda value: self.project.rename_variable(
                        token.extra["variable"],
                        value
                    )
                )
            )
            menu.AppendItem(
                "Copy id",
                lambda: set_clipboard_text(token.extra["variable"])
            )
            menu.AppendItem(
                "Highlight",
                lambda: setattr(self.project, "highlighted_variable", token.extra["variable"])
            )
            menu.AppendSeparator()
            menu.AppendItem("Usages:", lambda: None)
            def create_open_page_handler(page):
                return lambda: self.Parent.Parent.Parent.Parent.Parent.OpenPage(page.id)
            for page, full_title in self._find_variable_usages(self.project.get_page(), token.extra["variable"]):
                menu.AppendItem(
                    "{}".format(full_title),
                    create_open_page_handler(page)
                )
            menu.AppendSeparator()
            menu.AppendItem("Possible usages:", lambda: None)
            for page, full_title in self._find_variable_pages(self.project.get_page(), rename_value):
                menu.AppendItem(
                    "{}".format(full_title),
                    create_open_page_handler(page)
                )
            self.PopupMenu(menu)
            menu.Destroy()
        else:
            return CONTINUE_PROCESSING

    def _find_variable_pages(self, page, name, parents=[]):
        if self._page_has_variable(page, name):
            yield page, " / ".join(page.title for page in parents+[page])
        for child in page.children:
            for child_page in self._find_variable_pages(child, name, parents+[page]):
                yield child_page

    def _find_variable_usages(self, page, variable_id, parents=[]):
        if self._page_uses_variable(page, variable_id):
            yield page, " / ".join(page.title for page in parents+[page])
        for child in page.children:
            for child_page in self._find_variable_usages(child, variable_id, parents+[page]):
                yield child_page

    def _page_has_variable(self, page, name):
        for paragraph in page.paragraphs:
            if paragraph.type == "code":
                for fragment in paragraph.fragments:
                    if fragment.type == "code":
                        if re.search(r"\b{}\b".format(re.escape(name)), fragment.text):
                            return True

    def _page_uses_variable(self, page, variable_id):
        for paragraph in page.paragraphs:
            if paragraph.type == "code":
                for fragment in paragraph.fragments:
                    if fragment.type == "variable":
                        if fragment.id == variable_id:
                            return True

    def _path_double_click(self, event):
        edge_token = event.EventObject.GetClosestToken(event.Position)
        if edge_token is None:
            post_edit_start(self, subpath=None)
        else:
            edge, token = edge_token
            if "subpath" in token.extra:
                post_edit_start(self, subpath=token.extra["subpath"], edge=edge)
            elif edge < 0:
                post_edit_start(self, subpath=token.extra["prev_subpath"], edge=1)
            else:
                post_edit_start(self, subpath=token.extra["next_subpath"], edge=-1)

    def _body_double_click(self, event):
        post_edit_start(
            self,
            body_token=event.EventObject.GetToken(event.Position)
        )
class CodeEditor(wx.Panel):

    def __init__(self, parent, project, paragraph, view, extra):
        wx.Panel.__init__(self, parent, size=(-1, max(90, view.Size[1])))
        self.project = project
        self.paragraph = paragraph
        self.view = view
        self.extra = extra
        self._create_gui()
        self._focus()

    def _create_gui(self):
        self.Font = create_font(monospace=True)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(
            self._create_path(),
            flag=wx.ALL|wx.EXPAND
        )
        self.vsizer.Add(
            self._create_code(),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND,
            proportion=1
        )
        self.SetSizer(self.vsizer)

    def _create_path(self):
        self.path = SelectionableTextCtrl(
            self,
            value=self.paragraph.path.text_version
        )
        return self.path

    def _create_code(self):
        self.text = MultilineTextCtrl(
            self,
            value=self.paragraph.text_version
        )
        return self.text
    def _focus(self):
        if "subpath" in self.extra:
            self._focus_path(self.extra["subpath"], self.extra.get("edge"))
        elif "body_token" in self.extra:
            self._focus_body(self.extra["body_token"])
        else:
            self._focus_body(None)

    def _focus_path(self, subpath, edge):
        self.path.SetFocus()
        if subpath is None:
            end = len(self.path.Value)
            self.path.SetSelection(end, end)
        elif edge < 0:
            self.path.SetSelection(subpath.text_start, subpath.text_start)
        elif edge > 0:
            self.path.SetSelection(subpath.text_end, subpath.text_end)
        else:
            self.path.SetSelection(subpath.text_start, subpath.text_end)

    def _focus_body(self, body_token):
        self.text.SetFocus()
    def Save(self):
        with self.paragraph.multi_update():
            self.paragraph.path = Path.from_text_version(self.path.Value)
            self.paragraph.text_version = self.text.Value
class Image(ParagraphBase):

    PADDING = 30

    def CreateView(self):
        view = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.StaticBitmap(
            view,
            bitmap=base64_to_bitmap(
                self.paragraph.image_base64,
                self.project.PAGE_BODY_WIDTH
            )
        )
        sizer.Add(
            bitmap,
            flag=wx.ALIGN_CENTER
        )
        sizer.Add(
            TextView(
                view,
                self.project,
                self.paragraph.tokens,
                self,
                indented=2*self.PADDING
            ),
            flag=wx.ALIGN_CENTER
        )
        view.SetSizer(sizer)
        self.BindMouse(view, [view, bitmap])
        return view

    def CreateEdit(self, extra):
        return ImageEdit(
            self,
            self.project,
            self.paragraph,
            self.view
        )
class ImageEdit(wx.Panel):

    def __init__(self, parent, project, paragraph, view):
        wx.Panel.__init__(self, parent)
        self.Font = create_font(monospace=True)
        self.project = project
        self.paragraph = paragraph
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.image = wx.StaticBitmap(
            self,
            bitmap=base64_to_bitmap(
                paragraph.image_base64,
                self.project.PAGE_BODY_WIDTH
            )
        )
        sizer.Add(self.image, flag=wx.ALIGN_CENTER)
        self.text = MultilineTextCtrl(self, value=fragments_to_text(paragraph.fragments))
        sizer.Add(self.text, flag=wx.EXPAND)
        paste_button = wx.Button(self, label="Paste")
        paste_button.Bind(wx.EVT_BUTTON, self._on_paste)
        sizer.Add(paste_button)
        self.SetSizer(sizer)
        self.image_base64 = None

    def _on_paste(self, event):
        image_data = wx.BitmapDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(image_data)
            wx.TheClipboard.Close()
        if success:
            bitmap = image_data.GetBitmap()
            self.image.SetBitmap(fit_image(
                wx.ImageFromBitmap(bitmap),
                self.project.PAGE_BODY_WIDTH
            ).ConvertToBitmap())
            self.image_base64 = bitmap_to_base64(bitmap)
            self.GetTopLevelParent().ChildReRendered()

    def Save(self):
        value = {"fragments": text_to_fragments(self.text.Value)}
        if self.image_base64:
            value["image_base64"] = self.image_base64
        self.paragraph.update(value)
class Factory(ParagraphBase):

    def CreateView(self):
        view = wx.Panel(self)
        MouseEventHelper.bind(
            [view],
            drag=self.DoDragDrop,
            right_click=lambda event: self.ShowContextMenu()
        )
        view.SetBackgroundColour((240, 240, 240))
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer.Add(
            wx.StaticText(view, label="Factory"),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=self.project.PARAGRAPH_SPACE
        )
        self.vsizer.Add(
            self.hsizer,
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=self.project.PARAGRAPH_SPACE
        )
        self._add_button("Text", {
            "type": "text",
            "fragments": [{"type": "text", "text": "Enter text here..."}],
        })
        self._add_button("Quote", {
            "type": "quote",
            "fragments": [{"type": "text", "text": "Enter quote here..."}],
        })
        self._add_button("List", {
            "type": "list",
            "child_type": "unordered",
            "children": [{
                "child_type": None,
                "children": [],
                "fragments": [{"type": "text", "text": "Enter list item here..."}],
            }],
        })
        self._add_button("Code", {
            "type": "code",
            "filepath": [],
            "chunkpath": [],
            "fragments": [{"type": "code", "text": "Enter code here..."}],
        })
        self._add_button("Image", {
            "type": "image",
            "fragments": [{"type": "text", "text": "Enter image text here..."}],
        })
        self.vsizer.AddSpacer(self.project.PARAGRAPH_SPACE)
        view.SetSizer(self.vsizer)
        return view

    def _add_button(self, text, value):
        def click_handler(event):
            if self.project.active_editor is None:
                self.paragraph.update(value)
            else:
                show_edit_in_progress_error(self)
        button = wx.Button(self, label=text)
        button.Bind(wx.EVT_BUTTON, click_handler)
        self.hsizer.Add(button, flag=wx.ALL, border=2)
class ParagraphContextMenu(wx.Menu):

    def AppendItem(self, text, fn):
        self.Bind(
            wx.EVT_MENU,
            lambda event: fn(),
            self.Append(wx.NewId(), text)
        )
class SettingsDialog(wx.Dialog):

    def __init__(self, parent, project):
        wx.Dialog.__init__(self, parent)
        self.project = project
        self._init_gui()

    def _init_gui(self):
        spin = wx.SpinCtrl(
            self,
            value="{}".format(self.project.PAGE_BODY_WIDTH),
            min=100,
            max=10000
        )
        self.Bind(
            wx.EVT_SPINCTRL,
            lambda event: setattr(
                self.project,
                "PAGE_BODY_WIDTH",
                event.Value
            )
        )
class RliterateDataObject(wx.CustomDataObject):

    def __init__(self, kind, json=None):
        wx.CustomDataObject.__init__(self, "rliterate/{}".format(kind))
        if json is not None:
            self.set_json(json)

    def set_json(self, data):
        self.SetData(json.dumps(data))

    def get_json(self):
        return json.loads(self.GetData())
class Divider(wx.Panel):

    def __init__(self, parent, padding=0, height=1):
        wx.Panel.__init__(self, parent, size=(-1, height+2*padding))
        self.line = wx.Panel(self, size=(-1, height))
        self.line.SetBackgroundColour((255, 100, 0))
        self.line.Hide()
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.AddStretchSpacer(1)
        self.vsizer.Add(self.hsizer, flag=wx.EXPAND|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        self.vsizer.AddStretchSpacer(1)
        self.SetSizer(self.vsizer)

    def Show(self, left_space=0):
        with flicker_free_drawing(self):
            self.line.Show()
            self.hsizer.Clear(False)
            self.hsizer.Add((left_space, 1))
            self.hsizer.Add(self.line, flag=wx.EXPAND, proportion=1)
            self.Layout()

    def Hide(self):
        with flicker_free_drawing(self):
            self.line.Hide()
            self.Layout()
class MouseEventHelper(object):

    @classmethod
    def bind(cls, windows, drag=None, click=None, right_click=None,
             double_click=None, move=None):
        for window in windows:
            mouse_event_helper = cls(window)
            if drag is not None:
                mouse_event_helper.OnDrag = drag
            if click is not None:
                mouse_event_helper.OnClick = click
            if right_click is not None:
                mouse_event_helper.OnRightClick = right_click
            if double_click is not None:
                mouse_event_helper.OnDoubleClick = double_click
            if move is not None:
                mouse_event_helper.OnMove = move

    def __init__(self, window):
        self.down_pos = None
        window.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        window.Bind(wx.EVT_MOTION, self._on_motion)
        window.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        window.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        window.Bind(wx.EVT_RIGHT_UP, self._on_right_up)

    def OnDrag(self):
        pass

    def OnClick(self):
        pass

    def OnRightClick(self, event):
        pass

    def OnDoubleClick(self, event):
        pass

    def OnMove(self, event):
        pass

    def _on_left_down(self, event):
        self.down_pos = event.Position

    def _on_motion(self, event):
        if self.down_pos is None:
            self.OnMove(event)
        if self._should_drag(event.Position):
            self.down_pos = None
            self.OnDrag()

    def _should_drag(self, pos):
        if self.down_pos is not None:
            diff = self.down_pos - pos
            if abs(diff.x) > 2:
                return True
            if abs(diff.y) > 2:
                return True
        return False

    def _on_left_up(self, event):
        if self.down_pos is not None:
            self.OnClick()
        self.down_pos = None

    def _on_left_dclick(self, event):
        self.OnDoubleClick(event)

    def _on_right_up(self, event):
        self.OnRightClick(event)
class Token(object):

    SPLIT_PATTERNS = [
        re.compile(r"\n"),
        re.compile(r"\s+"),
        re.compile(r"\S+"),
    ]

    def __init__(self, text, token_type=TokenType.RLiterate, index=0, **extra):
        self.text = text
        self.token_type = token_type
        self.extra = extra
        self.index = index

    def with_extra(self, key, value):
        self.extra[key] = value
        return self

    def is_newline(self):
        return self.text == "\n"

    def is_space(self):
        return re.match(r"^\s+$", self.text)

    def split(self):
        index = self.index
        subtokens = []
        text = self.text
        while text:
            for split_pattern in self.SPLIT_PATTERNS:
                match = split_pattern.match(text)
                if match:
                    subtokens.append(self._replace_text(match.group(0), index))
                    text = text[match.end(0):]
                    index += len(match.group(0))
        return subtokens

    def _replace_text(self, text, index):
        return Token(
            text=text,
            token_type=self.token_type,
            index=index,
            **self.extra
        )
class SelectionableTextCtrl(wx.TextCtrl):

    def SetSelection(self, start, end):
        wx.CallAfter(wx.TextCtrl.SetSelection, self, start, end)
class FileGenerator(object):

    def __init__(self, document):
        self.document = document
        self.document.listen(lambda event: self._generate())

    def _generate(self):
        self._parts = defaultdict(list)
        self._collect_parts(self.document.get_page())
        self._generate_files()

    def _collect_parts(self, page):
        for paragraph in page.paragraphs:
            if paragraph.type == "code":
                self._parts[(
                    tuple(paragraph.path.filepath),
                    tuple(paragraph.path.chunkpath),
                )].append(paragraph)
        for child in page.children:
            self._collect_parts(child)

    def _generate_files(self):
        for key in self._parts.keys():
            filepath = self._get_filepath(key)
            if filepath:
                with open(filepath, "w") as f:
                    self._render(f, key)

    def _render(self, f, key, prefix=""):
        text_buffer = ""
        for paragraph in self._parts[key]:
            for fragment in paragraph.fragments:
                if fragment.type == "chunk":
                    for line in text_buffer.splitlines():
                        if len(line) > 0:
                            f.write(prefix)
                            f.write(line)
                        f.write("\n")
                    text_buffer = ""
                    self._render(f, (key[0], key[1]+tuple(fragment.path)), prefix=prefix+fragment.prefix)
                elif fragment.type == "variable":
                    text_buffer += fragment.name
                else:
                    text_buffer += fragment.text
        for line in text_buffer.splitlines():
            if len(line) > 0:
                f.write(prefix)
                f.write(line)
            f.write("\n")
        text_buffer = ""

    def _get_filepath(self, key):
        if len(key[0]) > 0 and len(key[1]) == 0:
            return os.path.join(*key[0])
        else:
            return None
class HTMLBuilder(object):

    def __init__(self, document, **options):
        self.document = document
        self.parts = []
        self.generate_toc = options.get("generate_toc", True)
        self.toc_max_depth = options.get("toc_max_depth", 3)

    def build(self):
        self.page(self.document.get_page())
        return "".join(self.parts)

    def toc(self, root_page, levels_left):
        if levels_left > 0 and root_page.children:
            with self.tag("ul", newlines=False):
                for page in root_page.children:
                    with self.tag("li"):
                        with self.tag("a", args={"href": "#{}".format(page.id)}):
                            self.escaped(page.title)
                        self.toc(page, levels_left - 1)

    def page(self, page, level=1):
        with self.tag(self.header_tag(level)):
            with self.tag("a", newlines=False, args={"name": page.id}):
                pass
            self.escaped(page.title)
        for paragraph in page.paragraphs:
            {
                "text": self.paragraph_text,
                "quote": self.paragraph_quote,
                "list": self.paragraph_list,
                "code": self.paragraph_code,
                "image": self.paragraph_image,
            }.get(paragraph.type, self.paragraph_unknown)(paragraph)
        if level == 1 and self.generate_toc:
            self.toc(page, self.toc_max_depth)
        for child in page.children:
            self.page(child, level+1)

    def header_tag(self, level):
        if level > 6:
            return "b"
        else:
            return "h{}".format(level)

    def paragraph_text(self, text):
        with self.tag("p"):
            self.tokens(text.tokens)

    def paragraph_quote(self, text):
        with self.tag("blockquote"):
            self.tokens(text.tokens)

    def paragraph_list(self, paragraph):
        self.list(paragraph)

    def list(self, a_list):
        if a_list.children:
            with self.tag({"ordered": "ol"}.get(a_list.child_type, "ul")):
                for item in a_list.children:
                    with self.tag("li"):
                        self.tokens(item.tokens)
                        self.list(item)

    def tokens(self, tokens):
        for token in tokens:
            {
                TokenType.RLiterate.Emphasis: self.token_emphasis,
                TokenType.RLiterate.Strong: self.token_strong,
                TokenType.RLiterate.Code: self.token_code,
                TokenType.RLiterate.Link: self.token_link,
                TokenType.RLiterate.Reference: self.token_reference,
            }.get(token.token_type, self.token_default)(token)

    def token_emphasis(self, token):
        with self.tag("em", newlines=False):
            self.escaped(token.text)

    def token_strong(self, token):
        with self.tag("strong", newlines=False):
            self.escaped(token.text)

    def token_code(self, token):
        with self.tag("code", newlines=False):
            self.escaped(token.text)

    def token_link(self, token):
        with self.tag("a", args={"href": token.extra["url"]}, newlines=False):
            self.escaped(token.text)

    def token_reference(self, token):
        with self.tag("a", args={"href": "#{}".format(token.extra["page_id"])}, newlines=False):
            with self.tag("em", newlines=False):
                self.escaped(token.text)

    def token_default(self, token):
        self.escaped(token.text)

    def paragraph_code(self, code):
        if not code.path.is_empty:
            with self.tag("div", args={"class": "rliterate-code-header"}):
                with self.tag("p", newlines=False):
                    self.escaped(code.path.text_version)
        with self.tag("div", args={"class": "rliterate-code-body"}):
            with self.tag("pre", newlines=False):
                for token in code.tokens:
                    with self.tag(
                        "span",
                        newlines=False,
                        args={"class": pygments.token.STANDARD_TYPES.get(token.token_type, "")}
                    ):
                        self.escaped(token.text)

    def paragraph_image(self, paragraph):
        with self.tag("div", args={"class": "rliterate-image"}):
            with self.tag("img", args={
                "src": "data:image/png;base64,{}".format(paragraph.image_base64)
            }):
                pass
        with self.tag("div", args={"class": "rliterate-image-text"}):
            with self.tag("p"):
                self.tokens(paragraph.tokens)

    def paragraph_unknown(self, paragraph):
        with self.tag("p"):
            self.escaped("Unknown paragraph...")

    @contextlib.contextmanager
    def tag(self, tag, newlines=True, args={}):
        args_string = ""
        if args:
            args_string = " " + " ".join("{}=\"{}\"".format(k, v) for k, v in args.items())
        self.raw("<{}{}>".format(tag, args_string))
        yield
        self.raw("</{}>".format(tag))
        if newlines:
            self.raw("\n\n")

    def raw(self, text):
        self.parts.append(text)

    def escaped(self, text):
        self.parts.append(xml.sax.saxutils.escape(text))
class DiffBuilder(object):

    def __init__(self, document):
        self.document = document

    def build(self):
        self.parts = []
        self._foo()
        return "".join(self.parts)

    def _foo(self):
        self.pages = []
        self._collect_pages(self.document.get_page())
        self._render_pages()

    def _collect_pages(self, page):
        self.pages.append(page)
        for child in page.children:
            self._collect_pages(child)

    def _render_pages(self):
        for page in sorted(self.pages, key=lambda page: page.id):
            self._write(page.id)
            self._write(": ")
            self._write(page.title)
            for child in page.children:
                self._write("\n")
                self._write("    ")
                self._write(child.id)
                self._write(": ")
                self._write(child.title)
            self._write("\n\n")
            for paragraph in page.paragraphs:
                {
                    "text": self._render_text,
                    "quote": self._render_quote,
                    "list": self._render_list,
                    "code": self._render_code,
                }.get(paragraph.type, self._render_unknown)(paragraph)

    def _render_text(self, text):
        self._wrapped_text(text.text_version)

    def _render_quote(self, paragraph):
        self._wrapped_text(paragraph.text_version, indent=4)

    def _render_list(self, paragraph):
        self._write(paragraph.text_version)

    def _wrapped_text(self, text, indent=0):
        current_line = []
        for part in text.replace("\n", " ").split(" "):
            if len(" ".join(current_line)) > 60-indent:
                self._write(" "*indent+" ".join(current_line))
                self._write("\n")
                current_line = []
            if part.strip():
                current_line.append(part.strip())
        if current_line:
            self._write(" "*indent+" ".join(current_line))
            self._write("\n")
        self._write("\n")

    def _render_code(self, code):
        self._write(code.path.text_version+":\n\n")
        for line in code.text_version.splitlines():
            self._write("    "+line+"\n")
        self._write("\n")

    def _render_unknown(self, paragraph):
        self._write("Unknown type = "+paragraph.type+"\n\n")

    def _write(self, text):
        self.parts.append(text)
class History(object):

    def __init__(self, initial_value, size=10):
        self._history = [("", initial_value)]
        self._history_index = 0
        self._new_history_entry = None
        self._size = size

    @property
    def value(self):
        return self._history[self._history_index][1]

    @contextlib.contextmanager
    def new_value(self, name=""):
        if self._new_history_entry is None:
            self._new_history_entry = (name, copy.deepcopy(self.value))
            yield self._new_history_entry[1]
            self._history = self._history[:self._history_index+1]
            self._history.append(self._new_history_entry)
            self._history = self._history[-self._size:]
            self._history_index = len(self._history) - 1
            self._new_history_entry = None
        else:
            yield self._new_history_entry[1]

    def can_back(self):
        return self._history_index > 0

    def back_name(self):
        if self.can_back():
            return self._history[self._history_index][0]

    def back(self):
        if self.can_back():
            self._history_index -= 1

    def can_forward(self):
        return self._history_index < (len(self._history) - 1)

    def forward_name(self):
        return self._history[self._history_index+1][0]

    def forward(self):
        if self.can_forward():
            self._history_index += 1
def index_with_id(items, item_id):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            return index
def fragments_to_text(fragments):
    text_version = TextVersion()
    for fragment in fragments:
        fragment.fill_text_version(text_version)
    return text_version.text


def text_to_fragments(text):
    return LegacyInlineTextParser().parse(text)
def split_legacy_path(path):
    filepath = []
    chunkpath = []
    while path and not (path[0].startswith("<<") and path[0].endswith(">>")):
        filepath.extend(path.pop(0).split("/"))
    for chunk in path:
        if chunk.startswith("<<"):
            chunk = chunk[2:]
        if chunk.endswith(">>"):
            chunk = chunk[:-2]
        chunkpath.extend(chunk.split("/"))
    return filepath, chunkpath
def legacy_code_text_to_fragments(text):
    fragments = []
    current_text = ""
    for line in text.splitlines():
        match = re.match(r"^(\s*)<<(.*)>>\s*$", line)
        if match:
            if current_text:
                fragments.append({"type": "code", "text": current_text})
            current_text = ""
            fragments.append({"type": "chunk", "path": match.group(2).split("/"), "prefix": match.group(1)})
        else:
            current_text += line
            current_text += "\n"
    if current_text:
        fragments.append({"type": "code", "text": current_text})
    return fragments
def genid():
    return uuid.uuid4().hex
def ensure_key(a_dict, key, default):
    if key not in a_dict:
        a_dict[key] = default
    return a_dict[key]
def pairs(items):
    return zip(items, items[1:]+[None])
def set_clipboard_text(text):
    if wx.TheClipboard.Open():
        try:
            wx.TheClipboard.SetData(wx.TextDataObject(text.encode("utf-8")))
        finally:
            wx.TheClipboard.Close()
def min_or_none(items, key):
    if not items:
        return None
    return min(items, key=key)
def post_token_click(widget, token):
    wx.PostEvent(widget, TokenClick(0, widget=widget, token=token))
def post_hovered_token_changed(widget, token):
    wx.PostEvent(widget, HoveredTokenChanged(0, widget=widget, token=token))
def base64_to_bitmap(data, max_width):
    try:
        image = fit_image(wx.ImageFromStream(
            StringIO.StringIO(base64.b64decode(data)),
            wx.BITMAP_TYPE_ANY
        ), max_width)
        return image.ConvertToBitmap()
    except:
        return wx.ArtProvider.GetBitmap(
            wx.ART_MISSING_IMAGE,
            wx.ART_BUTTON,
            (16, 16)
        )
def bitmap_to_base64(bitmap):
    output = StringIO.StringIO()
    image = wx.ImageFromBitmap(bitmap)
    image.SaveStream(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())
def fit_image(image, width):
    if image.Width <= width:
        return image
    factor = float(width) / image.Width
    return image.Scale(
        int(image.Width*factor),
        int(image.Height*factor),
        wx.IMAGE_QUALITY_HIGH
    )
def edit_in_gvim(text, filename):
    with tempfile.NamedTemporaryFile(suffix="-rliterate-external-"+filename) as f:
        f.write(text)
        f.flush()
        p = subprocess.Popen(["gvim", "--nofork", f.name])
        while p.poll() is None:
            wx.Yield()
            time.sleep(0.1)
        f.seek(0)
        return f.read()
def post_edit_start(control, **extra):
    wx.PostEvent(control, EditStart(0, extra=extra))
def find_first(items, action):
    for item in items:
        result = action(item)
        if result is not None:
            return result
    return None
def open_pages_gui(window, project, *args, **kwargs):
    try:
        project.open_pages(*args, **kwargs)
    except EditInProgress:
        show_edit_in_progress_error(window)
def show_edit_in_progress_error(window):
    dialog = wx.MessageDialog(
        window,
        "An edit is already in progress.",
        style=wx.CENTRE|wx.ICON_ERROR|wx.OK
    )
    dialog.ShowModal()
    dialog.Destroy()
@contextlib.contextmanager
def flicker_free_drawing(widget):
    widget.Freeze()
    yield
    widget.Thaw()
def create_font(monospace=False, size=10, bold=False):
    return wx.Font(
        size,
        wx.FONTFAMILY_TELETYPE if monospace else wx.FONTFAMILY_DEFAULT,
        wx.FONTSTYLE_NORMAL,
        wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL,
        False
    )
def show_text_entry(parent, **kwargs):
    dialog = wx.TextEntryDialog(
        parent,
        message=kwargs.get("body", ""),
        caption=kwargs.get("title", ""),
        defaultValue=kwargs.get("value", "")
    )
    if dialog.ShowModal() == wx.ID_OK:
        kwargs.get("ok_fn", lambda value: None)(dialog.Value)
    dialog.Destroy()
def is_prefix(left, right):
    return left == right[:len(left)]
def load_json_from_file(path):
    with open(path, "r") as f:
        return json.load(f)
def write_json_to_file(path, data):
    with safely_write_file(path) as f:
        json.dump(
            data, f,
            sort_keys=True, indent=0, separators=(',', ':')
        )
@contextlib.contextmanager
def safely_write_file(path):
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(path),
        prefix=os.path.basename(path) + ".tmp",
        delete=False
    ) as tmp:
        yield tmp
    os.rename(tmp.name, path)

if __name__ == "__main__":
    if sys.argv[2:] == ["--html"]:
        sys.stdout.write(HTMLBuilder(Document.from_file(sys.argv[1])).build())
    elif sys.argv[2:] == ["--diff"]:
        sys.stdout.write(DiffBuilder(Document.from_file(sys.argv[1])).build())
    else:
        app = wx.App()
        main_frame = MainFrame(Project(sys.argv[1]))
        main_frame.Show()
        app.MainLoop()
