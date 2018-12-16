# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!

from collections import defaultdict, namedtuple
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
def rltime(text):
    def wrap(fn):
        def fn_with_timing(*args, **kwargs):
            t1 = time.time()
            value = fn(*args, **kwargs)
            t2 = time.time()
            print("{: <20} {}ms".format(text, (1000*(t2-t1))))
            return value
        if "--profile" in sys.argv:
            return fn_with_timing
        else:
            return fn
    return wrap
class GuiUpdateMixin(object):

    DEFAULTS = {}

    def __init__(self, **kwargs):
        self.values = {}
        self.values.update(self.DEFAULTS)
        self.values.update(kwargs)
        self.changed = None
        self._create_gui()
        self._update_gui()

    @property
    def has_changes(self):
        return self.changed is None or len(self.changed) > 0

    def UpdateGui(self, **kwargs):
        self.changed = []
        for key, value in kwargs.items():
            if key not in self.values or self.values[key] != value:
                self.values[key] = value
                self.changed.append(key)
        self._update_gui()

    def did_change(self, name):
        return name in self.changed

    def _create_gui(self):
        pass

    def _update_gui(self):
        pass
class GuiUpdatePanel(wx.Panel, GuiUpdateMixin):

    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent)
        self._init_mixins()
        GuiUpdateMixin.__init__(self, **kwargs)

    def _init_mixins(self):
        pass
class BoxSizerMixin(object):

    def __init__(self, orientation):
        self.Sizer = wx.BoxSizer(orientation)

    def AppendChild(self, window, **kwargs):
        return self.AppendChildWithSizer(window, **kwargs)[0]

    def AppendChildWithSizer(self, window, **kwargs):
        return window, self.Sizer.Add(window, **kwargs)

    def InsertChild(self, position, window, **kwargs):
        self.Sizer.Insert(position, window, **kwargs)
        return window

    def AppendSpace(self, size=0):
        return SizeWrapper(
            self.Sizer.Orientation,
            self.Sizer.Add((0, 0))
        ).WithSize(size)

    def AppendStretch(self, proportion):
        self.Sizer.AddStretchSpacer(proportion)

    def RemoveChildren(self):
        self.Sizer.Clear(True)
class VerticalPanel(wx.Panel, BoxSizerMixin):

    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        BoxSizerMixin.__init__(self, wx.VERTICAL)
class HorizontalPanel(wx.Panel, BoxSizerMixin):

    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        BoxSizerMixin.__init__(self, wx.HORIZONTAL)
class HorizontalBasePanel(GuiUpdatePanel, BoxSizerMixin):

    def __init__(self, parent, **kwargs):
        GuiUpdatePanel.__init__(self, parent, **kwargs)

    def _init_mixins(self):
        BoxSizerMixin.__init__(self, wx.HORIZONTAL)
class VerticalBasePanel(GuiUpdatePanel, BoxSizerMixin):

    def __init__(self, parent, **kwargs):
        GuiUpdatePanel.__init__(self, parent, **kwargs)

    def _init_mixins(self):
        BoxSizerMixin.__init__(self, wx.VERTICAL)
class SizeWrapper(object):

    def __init__(self, orientation, sizer_item):
        self._orientation = orientation
        self._sizer_item = sizer_item

    def SetSize(self, size):
        if self._orientation == wx.HORIZONTAL:
            self._sizer_item.SetMinSize((size, 1))
        else:
            self._sizer_item.SetMinSize((1, size))

    def WithSize(self, size):
        self.SetSize(size)
        return self
class Editable(VerticalBasePanel):

    @property
    def project(self):
        return self.values["project"]

    @property
    def page_id(self):
        return self.values["page_id"]

    @property
    def paragraph(self):
        return self.values["paragraph"]

    @property
    def selection(self):
        return self.values["selection"]

    def _create_gui(self):
        self.view = self.AppendChild(
            self.CreateView(),
            flag=wx.EXPAND,
            proportion=1
        )
        self.view.Bind(EVT_EDIT_START, self.OnEditStart)

    def _update_gui(self):
        if hasattr(self, "edit"):
            self.edit.Destroy()
            del self.edit
            self.view.Destroy()
            self._create_gui()
        else:
            self._update_paragraph_gui()

    def _update_paragraph_gui(self):
        self.view.Destroy()
        self._create_gui()

    def OnEditStart(self, event):
        if self.project.active_editor is not None:
            show_edit_in_progress_error(self)
            return
        with flicker_free_drawing(self):
            self.edit = self.CreateEdit(event.extra)
            self.edit.SetFocus()
            self.GetSizer().Add(self.edit, flag=wx.EXPAND, proportion=1)
            self.GetSizer().Hide(self.view)
            self.GetTopLevelParent().Layout()
            self.project.active_editor = self

    def Cancel(self):
        self.project.active_editor = None

    def Save(self):
        self.edit.Save()
        self.project.active_editor = None
class Observable(object):

    def __init__(self):
        self._notify_count = 0
        self._listeners = []

    def listen(self, fn):
        self._listeners.append(fn)

    def unlisten(self, fn):
        self._listeners.remove(fn)

    @contextlib.contextmanager
    def notify(self):
        self._notify_count += 1
        try:
            yield
        finally:
            self._notify_count -= 1
            self._notify()

    def notify_forwarder(self):
        return self._notify

    def _notify(self):
        if self._notify_count == 0:
            for fn in self._listeners:
                fn()
class Style(namedtuple("Style", "foreground background bold underlined italic monospace")):

    @classmethod
    def create(cls, **kwargs):
        values = {
            "foreground": "#000000",
            "background": None,
            "bold": False,
            "underlined": False,
            "italic": False,
            "monospace": False,
        }
        values.update(kwargs)
        return cls(**values)

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
        dc.SetTextForeground(self.foreground)
        if self.background is None:
            dc.SetBackgroundMode(wx.TRANSPARENT)
        else:
            dc.SetTextBackground(self.background)
            dc.SetBackgroundMode(wx.SOLID)
        dc.SetFont(font)

    def highlight(self):
        return self._replace(foreground="#fcf4df", background="#b58900")
class ParagraphBase(Editable):

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
        SimpleContextMenu.ShowRecursive(self)

    def CreateContextMenu(self):
        menu = SimpleContextMenu("Paragraph")
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
        return menu

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
            wx.CallAfter(self.OnDataDropped, self.rliterate_data.get_json(), drop_point)
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
class TextProjection(GuiUpdatePanel):

    DEFAULTS = {
        "characters": [],
        "line_height": 1,
        "max_width": None,
        "break_at_word": True,
    }

    def _create_gui(self):
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.timer = wx.Timer(self)
        self._show_beams = True

    def _update_gui(self):
        if self.has_changes:
            self._layout()
            if self._beams:
                self.timer.Start(400)
            else:
                self.timer.Stop()

    def _setup_beams(self):
        self._show_beams = True
        if self._beams:
            self.Bind(wx.EVT_TIMER, self._on_timer)
            self.timer = wx.Timer(self)
            self.timer.Start(400)

    def _on_timer(self, event):
        self._show_beams = not self._show_beams
        self.Refresh()

    def _layout(self):
        self._partition_characters()
        self._measure_character_size()
        self._calculate_lines()
        self._partition_strings()
        self._set_min_size()

    def _partition_characters(self):
        self._boxes = []
        self._boxes_by_style = defaultdict(list)
        self._beams = []
        for character in self.values["characters"]:
            box = Box(character)
            self._boxes.append(box)
            self._boxes_by_style[character.style].append(box)
            if character.marker == "beam":
                self._beams.append(box)

    def _measure_character_size(self):
        dc = wx.MemoryDC()
        dc.SetFont(self.GetFont())
        dc.SelectObject(wx.EmptyBitmap(1, 1))
        self._line_height_pixels = int(round(dc.GetTextExtent("M")[1]*self.values["line_height"]))
        for style, boxes in self._boxes_by_style.iteritems():
            style.apply_to_wx_dc(dc, self.GetFont())
            for box in boxes:
                box.rect.Size = dc.GetTextExtent(box.char.text)

    def _calculate_lines(self):
        self._lines = []
        current_line = []
        x, y = 0, 0
        index = 0
        previous_box, break_index, break_len = None, None, None
        while index < len(self._boxes):
            box = self._boxes[index]
            if previous_box and previous_box.char.text == " " and box.char.text != " ":
                break_index, break_len = index, len(current_line)
            if (box.char.text == "\n" or
                (x > 0 and self.values["max_width"] is not None and x+box.rect.Width > self.values["max_width"])):
                x = 0
                y += self._line_height_pixels
                if box.char.text != "\n" and break_index is not None and self.values["break_at_word"]:
                    index = break_index
                    box = self._boxes[index]
                    current_line = current_line[:break_len]
                self._lines.append(current_line)
                current_line = []
                previous_box, break_index, break_len = None, None, None
            box.rect.Position = (x, y)
            x += box.rect.Width
            if box.char.text != "\n":
                current_line.append(box)
            previous_box = box
            index += 1
        if current_line:
            self._lines.append(current_line)

    def _partition_strings(self):
        self._strings_by_style = defaultdict(lambda: ([], []))
        def push():
            if text:
                strings, poss = self._strings_by_style[style]
                strings.append("".join(text))
                poss.append(position)
        for line in self._lines:
            style = None
            position = None
            text = []
            for box in line:
                if style is None or style != box.char.style:
                    push()
                    style = box.char.style
                    position = box.rect.Position
                    text = []
                text.append(box.char.text)
            push()

    def _set_min_size(self):
        max_x = 10
        max_y = self._line_height_pixels
        for line in self._lines:
            for box in line:
                max_x = max(max_x, box.rect.X+box.rect.Width)
                max_y = max(max_y, box.rect.Y+box.rect.Height)
        self.SetMinSize((max_x, max_y))

    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        for style, strings_positions in self._strings_by_style.iteritems():
            style.apply_to_wx_dc(dc, self.GetFont())
            dc.DrawTextList(*strings_positions)
        if self._show_beams:
            dc.SetPen(wx.Pen(wx.RED, width=2, style=wx.PENSTYLE_SOLID))
            for box in self._beams:
                dc.DrawLinePoint(box.rect.TopLeft, box.rect.BottomLeft)

    def GetCharacterAt(self, position):
        for box in self._boxes:
            if box.rect.Contains(position):
                return box.char

    def GetClosestCharacter(self, position):
        if len(self._boxes) == 0:
            return None
        characters_by_y_distance = defaultdict(list)
        for box in self._boxes:
            if box.rect.Contains(position):
                characters_by_y_distance[0] = [box]
                break
            characters_by_y_distance[
                abs(box.rect.Y + int(box.rect.Height / 2) - position.y)
            ].append(box)
        return min(
            characters_by_y_distance[min(characters_by_y_distance.keys())],
            key=lambda box: abs(box.rect.X + int(box.rect.Width / 2) - position.x)
        ).char
class TokenView(TextProjection):

    def __init__(self, parent, project, tokens, **kwargs):
        TextProjection.__init__(
            self,
            parent,
            characters=self._generate_characters(project, tokens),
            line_height=kwargs.get("line_height", 1),
            max_width=kwargs.get("max_width", 100),
            break_at_word=kwargs.get("skip_extra_space", False)
        )
        self.last_tokens = []
        self._default_cursor = self.GetCursor()

    def UpdateTokens(self, project, tokens, max_width):
        if tokens != self.last_tokens:
            self.UpdateGui(
                characters=self._generate_characters(project, tokens),
                max_width=max_width
            )
            self.last_tokens = tokens
        else:
            self.UpdateGui(
                max_width=max_width
            )

    @rltime("generate characters")
    def _generate_characters(self, project, tokens):
        self.characters = []
        for token in tokens:
            style = project.get_style(token.token_type)
            if token.extra.get("highlight"):
                style = style.highlight()
            for subtoken in token.split():
                for char in subtoken.text:
                    self.characters.append(Character.create(
                        char,
                        style,
                        extra=subtoken
                    ))
        return self.characters

    def GetToken(self, position):
        character = self.GetCharacterAt(position)
        if character is not None:
            return character.extra
    def GetClosestToken(self, position):
        character = self.GetClosestCharacter(position)
        if character is not None:
            return (0, character.extra)
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
class VerticalScrolledWindow(CompactScrolledWindow, BoxSizerMixin):

    def __init__(self, *args, **kwargs):
        CompactScrolledWindow.__init__(self, *args, **kwargs)
        BoxSizerMixin.__init__(self, wx.VERTICAL)
class HorizontalScrolledWindow(CompactScrolledWindow, BoxSizerMixin):

    def __init__(self, *args, **kwargs):
        CompactScrolledWindow.__init__(self, *args, **kwargs)
        BoxSizerMixin.__init__(self, wx.HORIZONTAL)
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
class SimpleContextMenu(wx.Menu):

    def __init__(self, name):
        wx.Menu.__init__(self)
        self._name = name

    def AppendItem(self, text, fn):
        self.Bind(
            wx.EVT_MENU,
            lambda event: fn(),
            self.Append(wx.NewId(), text)
        )

    def AddToMenu(self, menu):
        menu.AppendSubMenu(self, self._name)

    def Popup(self, widget):
        self._append_parents(widget)
        widget.PopupMenu(self)
        self.Destroy()

    def _append_parents(self, widget):
        parent = widget.Parent
        sub_menus = []
        while parent is not None:
            if hasattr(parent, "CreateContextMenu"):
                sub_menus.append(parent.CreateContextMenu())
            parent = parent.Parent
        if sub_menus:
            self.AppendSeparator()
            for x in sub_menus:
                x.AddToMenu(self)

    @staticmethod
    def ShowRecursive(widget):
        while widget is not None:
            if hasattr(widget, "CreateContextMenu"):
                widget.CreateContextMenu().Popup(widget)
                return
            widget = widget.Parent
class JsonSettings(Observable):

    def __init__(self, settings_dict):
        Observable.__init__(self)
        self._settings_dict = settings_dict

    @classmethod
    def from_file(cls, path):
        if os.path.exists(path):
            settings_dict = load_json_from_file(path)
        else:
            settings_dict = {}
        settings = cls(settings_dict)
        settings.listen(lambda:
            write_json_to_file(
                path,
                settings_dict
            )
        )
        return settings
    def get(self, path, default=None):
        keys = path.split(".")
        return copy.deepcopy(
            self._dict_at(keys[:-1]).get(keys[-1], default)
        )

    def set(self, path, value):
        keys = path.split(".")
        with self.notify():
            self._dict_at(keys[:-1], create=True)[keys[-1]] = copy.deepcopy(value)

    def _dict_at(self, keys, create=False):
        sub_dict = self._settings_dict
        while keys:
            key = keys.pop(0)
            if key not in sub_dict and create:
                sub_dict[key] = {}
            sub_dict = sub_dict.get(key, {})
        return sub_dict
    @staticmethod
    def property(path, default=None):
        return property(
            fget=lambda self: self.get(path, default),
            fset=lambda self, value: self.set(path, value)
        )
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
        document.listen(rltime("write document")(lambda:
            write_json_to_file(
                path,
                document.read_only_document_dict
            )
        ))
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

    def iter_pages(self):
        def iter_pages(page):
            yield page
            for child in page.children:
                for sub_page in iter_pages(child):
                    yield sub_page
        return iter_pages(self.get_page())
    def get_page(self, page_id=None):
        page_dict = self.read_only_document_dict.get_page_dict(page_id)
        if page_dict is None:
            return None
        return Page(self, page_dict)

    def get_parent_page(self, page_id):
        page_dict = self.read_only_document_dict.get_parent_page_dict(page_id)
        if page_dict is None:
            return None
        return Page(self, page_dict)
    def add_paragraph(self, page_id, before_id=None, paragraph_dict={"type": "factory"}):
        with self.modify("Add paragraph") as document_dict:
            document_dict.add_paragraph_dict(
                dict(paragraph_dict, id=genid()),
                page_id,
                before_id=before_id
            )

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

    def get_parent_page_dict(self, page_id):
        return self._parent_pages.get(page_id, None)

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
    def parent(self):
        return self._document.get_parent_page(self.id)

    @property
    def full_title(self):
        return " / ".join(page.title for page in self.chain)

    @property
    def chain(self):
        result = []
        page = self
        while page is not None:
            result.insert(0, page)
            page = page.parent
        return result

    def iter_code_fragments(self):
        for paragraph in self.paragraphs:
            for fragment in paragraph.iter_code_fragments():
                yield fragment

    def iter_text_fragments(self):
        for paragraph in self.paragraphs:
            for fragment in paragraph.iter_text_fragments():
                yield fragment

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
            "expanded_code": ExpandedCodeParagraph,
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
                dict(copy.deepcopy(self._paragraph_dict), id=genid()),
                page_id=self._page.id,
                before_id=self.next_id
            )

    @property
    def filename(self):
        return "paragraph.txt"

    def iter_code_fragments(self):
        return iter([])

    def iter_text_fragments(self):
        return iter([])
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

    def iter_text_fragments(self):
        return iter(self.fragments)
class TextParser(object):

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
            re.compile(r"``(.+?)``", flags=re.DOTALL),
            lambda parser, match: {
                "type": "variable",
                "id": match.group(1),
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

    def iter_text_fragments(self):
        for item in self.children:
            for fragment in item.iter_text_fragments():
                yield fragment
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

    def iter_text_fragments(self):
        for fragment in self.fragments:
            yield fragment
        for child in self.children:
            for fragment in child.iter_text_fragments():
                yield fragment
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

    def iter_code_fragments(self):
        return iter(self.fragments)
    @property
    def text_version(self):
        self._variable_map = {}
        text_version = TextVersion()
        for fragment in self.fragments:
            fragment.fill_text_version(text_version)
        return text_version.text

    def add_variable_map(self, name, id_):
        entry = name
        index = 1
        while entry in self._variable_map and self._variable_map[entry] != id_:
            entry = "{}{}".format(name, index)
            index += 1
        self._variable_map[entry] = id_
        return entry
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
                body_match = re.match(r"^(.*?)(, blank_lines_before=(\d+))?$", match.group(2))
                if body_match.group(2):
                    blank_lines_before = int(body_match.group(3))
                else:
                    blank_lines_before = 0
                self._parsed_fragments.append({
                    "type": "chunk",
                    "path": body_match.group(1).split("/"),
                    "prefix": match.group(1),
                    "blank_lines_before": blank_lines_before,
                })
            else:
                while line:
                    variable_match = re.match(self._variable_fragment_re(), line)
                    tabstop_match = re.match(self._tabstop_fragment_re(), line)
                    if variable_match:
                        self._parse_clear()
                        self._parsed_fragments.append({
                            "type": "variable",
                            "id": self._get_variable_id(variable_match.group(1))
                        })
                        line = line[len(variable_match.group(0)):]
                    elif tabstop_match:
                        self._parse_clear()
                        self._parsed_fragments.append({
                            "type": "tabstop",
                            "index": int(tabstop_match.group(1))
                        })
                        line = line[len(tabstop_match.group(0)):]
                    else:
                        self._parse_buffer += line[0]
                        line = line[1:]
                self._parse_buffer += "\n"
        self._parse_clear()
        return self._parsed_fragments

    def _get_variable_id(self, identifier):
        if identifier in self._variable_map:
            return self._variable_map[identifier]
        elif self._document.lookup_variable(identifier) is None:
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

    def _tabstop_fragment_re(self):
        start, end = self.chunk_delimiters
        return r"{}{{(\d+)}}{}".format(re.escape(start), re.escape(end))
    @property
    def tokens(self):
        chain = CharChain()
        for fragment in self.fragments:
            if fragment.type == "chunk":
                text_version = TextVersion()
                fragment.fill_text_version(text_version, for_view=True)
                chain.append(
                    text_version.text,
                    token_type=TokenType.Comment.Preproc,
                    subpath=self.path.extend_chunk(fragment.path)
                )
            elif fragment.type == "variable":
                chain.append(fragment.name, variable=fragment.id)
            elif fragment.type == "code":
                chain.append(fragment.text)
            elif fragment.type == "tabstop":
                chain.mark_tabstop(fragment.index)
        chain.align_tabstops()
        chain.colorize(self.pygments_lexer)
        return chain.to_tokens()
    @property
    def language(self):
        if self.raw_language:
            return self.raw_language
        else:
            return "".join(self.pygments_lexer.aliases[:1])

    @property
    def raw_language(self):
        return self._paragraph_dict.get("language", "")

    @raw_language.setter
    def raw_language(self, value):
        self.update({
            "language": value,
        })

    @property
    def pygments_lexer(self):
        try:
            if self.raw_language:
                return pygments.lexers.get_lexer_by_name(
                    self.raw_language,
                    stripnl=False
                )
            else:
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
            "tabstop": TabstopCodeFragment,
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
            return self.id
        else:
            return name

    def fill_text_version(self, text_version):
        start, end = self._code_paragraph.variable_delimiters
        text_version.add(start)
        text_version.add(self._code_paragraph.add_variable_map(self.name, self.id))
        text_version.add(end)
class ChunkCodeFragment(CodeFragment):

    @property
    def prefix(self):
        return self._code_fragment_dict["prefix"]

    @property
    def blank_lines_before(self):
        return self._code_fragment_dict.get("blank_lines_before", 0)

    @property
    def path(self):
        return copy.deepcopy(self._code_fragment_dict["path"])

    def fill_text_version(self, text_version, for_view=False):
        start, end = self._code_paragraph.chunk_delimiters
        text_version.add(self.prefix)
        text_version.add(start)
        text_version.add("/".join(self.path))
        if self.blank_lines_before > 0 and not for_view:
            text_version.add(", blank_lines_before=")
            text_version.add(str(self.blank_lines_before))
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
class TabstopCodeFragment(CodeFragment):

    @property
    def index(self):
        return self._code_fragment_dict["index"]

    def fill_text_version(self, text_version):
        start, end = self._code_paragraph.chunk_delimiters
        text_version.add(start)
        text_version.add("{")
        text_version.add(str(self.index))
        text_version.add("}")
        text_version.add(end)
class CharChain(object):

    def __init__(self):
        self.head = None
        self.tail = None
        self.tabstops = defaultdict(list)

    def __iter__(self):
        char = self.head
        while char is not None:
            yield char
            char = char.next

    def mark_tabstop(self, index):
        self.tabstops[index].append(self.tail)

    def align_tabstops(self):
        align_length = 0
        for index in sorted(self.tabstops.keys()):
            align_length = max([align_length+1]+[
                char.count_chars_to_start_of_line()
                for char in self.tabstops[index]
            ])
            for char in self.tabstops[index]:
                x = range(align_length - char.count_chars_to_start_of_line())
                for _ in x:
                    self._insert_after(char, Char(" ", {}))

    def append(self, string, **meta):
        for char in string:
            self._insert_after(self.tail, Char(char, dict(meta)))

    def to_tokens(self):
        return [Token(char.value, **char.meta) for char in self]

    def colorize(self, pygments_lexer):
        pygments_text = self._extract_non_colored_text()
        pygments_tokens = pygments_lexer.get_tokens(pygments_text)
        self._apply_pygments_tokens(pygments_tokens)

    def _extract_non_colored_text(self):
        return "".join(
            char.value
            for char in self
            if char.meta.get("token_type") is None
        )

    def _apply_pygments_tokens(self, pygments_tokens):
        char = self.head
        for pygments_token, text in pygments_tokens:
            for _ in text:
                while char is not None and char.meta.get("token_type") is not None:
                    char = char.next
                if char is not None:
                    char.meta["token_type"] = pygments_token
                    char = char.next

    def _insert_after(self, before, char):
        if self.tail is None:
            self.head = char
            self.tail = char
        else:
            char.next = before.next
            char.previuos = before
            if before.next is not None:
                before.next.previuos = char
            before.next = char
            if before is self.tail:
                self.tail = char


class Char(object):

    def __init__(self, value, meta):
        self.previuos = None
        self.next = None
        self.value = value
        self.meta = meta

    def count_chars_to_start_of_line(self):
        count = 0
        char = self
        while char is not None and not char.is_newline():
            char = char.previuos
            count += 1
        return count

    def is_newline(self):
        return self.value == "\n"
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

    def iter_text_fragments(self):
        return iter(self.fragments)
class ExpandedCodeParagraph(Paragraph):

    @property
    def tokens(self):
        paragraph, chain = CodeExpander(self._document).expand_id(self.code_id)
        if paragraph is not None:
            chain.colorize(paragraph.pygments_lexer)
        return chain.to_tokens()

    @property
    def code_id(self):
        return self._paragraph_dict.get("code_id")
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
            "variable": VariableTextFragment,
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
class VariableTextFragment(TextFragment):

    @property
    def id(self):
        return self._text_fragment_dict["id"]

    @property
    def name(self):
        name = self._document.lookup_variable(self.id)
        if name is None:
            return self.id
        else:
            return name

    def fill_text_version(self, text_version):
        text_version.add("``")
        text_version.add_with_index(self.id, self._index)
        text_version.add("``")

    @property
    def token(self):
        return Token(self.name, token_type=TokenType.RLiterate.Variable, fragment_index=self._index)
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
        self._selection = Selection()
        self._active_editor = None
        self._highlighted_variable = None
        self._needs_saving = False
        self.title="{} ({})".format(
            os.path.basename(filepath),
            os.path.dirname(os.path.abspath(filepath))
        )
        self.document = Document.from_file(filepath)
        self.document.listen(self._mark_for_saving)
        self.document.listen(self.notify_forwarder())
        self.layout = Layout.from_file(os.path.join(
            os.path.dirname(filepath),
            ".{}.layout".format(os.path.basename(filepath))
        ))
        self.layout.listen(self.notify_forwarder())
        self.global_settings = GlobalSettings.from_file(
            os.path.join(
                wx.StandardPaths.Get().GetUserConfigDir(),
                ".rliterate.settings"
            )
        )
        self.global_settings.listen(self.notify_forwarder())

    @property
    def theme(self):
        return self.global_settings
    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        with self.notify():
            self._selection = value
    def get_page(self, *args, **kwargs):
        return self.document.get_page(*args, **kwargs)

    def iter_pages(self, *args, **kwargs):
        return self.document.iter_pages(*args, **kwargs)

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

    @property
    def hoisted_page(self):
        return self.layout.hoisted_page

    @hoisted_page.setter
    def hoisted_page(self, value):
        self.layout.hoisted_page = value
    def get_style(self, *args, **kwargs):
        return SolarizedTheme().get_style(*args, **kwargs)
    @property
    def active_editor(self):
        return self._active_editor

    @active_editor.setter
    def active_editor(self, editor):
        with self.notify():
            self._active_editor = editor
    @property
    def highlighted_variable(self):
        return self._highlighted_variable

    @highlighted_variable.setter
    def highlighted_variable(self, variable_id):
        with self.notify():
            self._highlighted_variable = variable_id
    def _mark_for_saving(self):
        self._needs_saving = True
    @property
    def needs_saving(self):
        return self._needs_saving
    def save(self):
        if self._needs_saving:
            with self.notify():
                CodeExpander(self.document).generate_files()
                self._needs_saving = False
class EditInProgress(Exception):
    pass
class Selection(object):

    def __init__(self, value=None, trail=None):
        self.value = value
        self.trail = [] if trail is None else trail

    @property
    def present(self):
        return self.value is not None

    def get(self, key):
        return Selection(
            self.value.get(key) if self.value is not None else None,
            trail=[key]+self.trail
        )

    def create(self, value):
        for key in self.trail:
            value = {key: value}
        return Selection(value)
class GlobalSettings(JsonSettings):

    page_body_width = JsonSettings.property(
        "theme.page_body_width", 600
    )
    page_padding = JsonSettings.property(
        "theme.page_padding", 15
    )
    shadow_size = JsonSettings.property(
        "theme.shadow_size", 2
    )
    paragraph_space = JsonSettings.property(
        "theme.paragraph_space", 15
    )
    container_border = JsonSettings.property(
        "theme.container_border", 15
    )
    editor_font = JsonSettings.property(
        "theme.fonts.editor", {"monospace": True, "size": 9}
    )
    toc_font = JsonSettings.property(
        "theme.fonts.toc", {"size": 10}
    )
    title_font = JsonSettings.property(
        "theme.fonts.title", {"size": 16}
    )
    code_font = JsonSettings.property(
        "theme.fonts.code", {"monospace": True}
    )
    text_font = JsonSettings.property(
        "theme.fonts.text", {"size": 10}
    )
    workspace_background = JsonSettings.property(
        "theme.workspace.background", "#cccccc"
    )
class Layout(JsonSettings):

    def __init__(self, *args, **kwargs):
        JsonSettings.__init__(self, *args, **kwargs)
        if "workspace" in self._settings_dict:
            workspace = self._settings_dict["workspace"]
            if "scratch" in workspace:
                if "columns" not in workspace:
                    workspace["columns"] = [workspace["scratch"]]
                del workspace["scratch"]
        self._workspace_columns_history = History(
            self.columns,
            size=20
        )

    hoisted_page = JsonSettings.property(
        "toc.hoisted_page_id",
        None
    )
    def is_collapsed(self, page_id):
        return page_id in self.get("toc.collapsed", [])

    def toggle_collapsed(self, page_id):
        collapsed = self.get("toc.collapsed", [])
        if page_id in collapsed:
            collapsed.remove(page_id)
        else:
            collapsed.append(page_id)
        self.set("toc.collapsed", collapsed)
    columns = JsonSettings.property(
        "workspace.columns",
        []
    )

    def open_pages(self, page_ids, column_index=None):
        with self._workspace_columns_history.new_value() as value:
            if column_index is None:
                column_index = len(self.columns)
            value[column_index:] = [page_ids[:]]
            self.columns = value

    def can_back(self):
        return self._workspace_columns_history.can_back()

    def back(self):
        self._workspace_columns_history.back()
        self.columns = self._workspace_columns_history.value

    def can_forward(self):
        return self._workspace_columns_history.can_forward()

    def forward(self):
        self._workspace_columns_history.forward()
        self.columns = self._workspace_columns_history.value

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
        TokenType:                     Style.create(foreground=base00),
        TokenType.Keyword:             Style.create(foreground=green),
        TokenType.Keyword.Constant:    Style.create(foreground=cyan),
        TokenType.Keyword.Declaration: Style.create(foreground=blue),
        TokenType.Keyword.Namespace:   Style.create(foreground=orange),
        TokenType.Name.Builtin:        Style.create(foreground=red),
        TokenType.Name.Builtin.Pseudo: Style.create(foreground=blue),
        TokenType.Name.Class:          Style.create(foreground=blue),
        TokenType.Name.Decorator:      Style.create(foreground=blue),
        TokenType.Name.Entity:         Style.create(foreground=violet),
        TokenType.Name.Exception:      Style.create(foreground=yellow),
        TokenType.Name.Function:       Style.create(foreground=blue),
        TokenType.String:              Style.create(foreground=cyan),
        TokenType.Number:              Style.create(foreground=cyan),
        TokenType.Operator.Word:       Style.create(foreground=green),
        TokenType.Comment:             Style.create(foreground=base1),
        TokenType.Comment.Preproc:     Style.create(foreground=magenta, bold=True),
        TokenType.RLiterate:           Style.create(foreground=text),
        TokenType.RLiterate.Emphasis:  Style.create(foreground=text, italic=True),
        TokenType.RLiterate.Strong:    Style.create(foreground=text, bold=True),
        TokenType.RLiterate.Code:      Style.create(foreground=text, monospace=True),
        TokenType.RLiterate.Variable:  Style.create(foreground=text, monospace=True, italic=True),
        TokenType.RLiterate.Link:      Style.create(foreground=blue, underlined=True),
        TokenType.RLiterate.Reference: Style.create(foreground=blue, italic=True),
        TokenType.RLiterate.Path:      Style.create(foreground=text, italic=True, bold=True),
        TokenType.RLiterate.Chunk:     Style.create(foreground=magenta, bold=True),
        TokenType.RLiterate.Sep:       Style.create(foreground=base1),
    }
class MainFrame(wx.Frame, BoxSizerMixin):

    def __init__(self, project):
        wx.Frame.__init__(
            self,
            None,
            size=(920, 500),
            title="{} - RLiterate".format(project.title)
        )
        BoxSizerMixin.__init__(self, wx.HORIZONTAL)
        self.project = project
        self.AppendChild(self._create_main_panel(), flag=wx.EXPAND, proportion=1)

    def _create_main_panel(self):
        panel = HorizontalPanel(self)
        self.SetToolBar(ToolBar(panel, self.project))
        self._focus_panel = panel.AppendChild(
            wx.Panel(self)
        )
        self.toc = panel.AppendChild(
            TableOfContents(panel, project=self.project),
            flag=wx.EXPAND,
            proportion=0
        )
        self.workspace = panel.AppendChild(
            Workspace(panel, project=self.project),
            flag=wx.EXPAND,
            proportion=1
        )
        self.project.listen(self.UpdateGui)
        return panel

    @rltime("update main frame")
    def UpdateGui(self):
        with flicker_free_drawing(self):
            self.toc.UpdateGui(project=self.project)
            self.workspace.UpdateGui(project=self.project)
            self.ChildReRendered()

    def ChildReRendered(self):
        self.Layout()
        if self.project.active_editor is None:
            focused_widget = wx.Window.FindFocus()
            if focused_widget and hasattr(focused_widget, "DONT_RESET_FOCUS"):
                return
            self._focus_panel.SetFocus()
class ToolBar(wx.ToolBar):

    def __init__(self, parent, project, *args, **kwargs):
        wx.ToolBar.__init__(self, parent, *args, **kwargs)
        self._init_project(project)
        self._init_tools()

    def _init_project(self, project):
        self.project = project
        self.project.listen(lambda:
            self._tool_groups.populate(self)
        )

    def _init_tools(self):
        main_frame = self.GetTopLevelParent()
        self._tool_groups = ToolGroups(main_frame)
        save_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is None
        )
        save_group.add_tool(
            wx.ART_FILE_SAVE,
            lambda: self.project.save(),
            short_help="Save",
            shortcuts=[
                (wx.ACCEL_CTRL, ord('S')),
            ],
            enabled_fn=lambda: self.project.needs_saving
        )
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
        quit_group = self._tool_groups.add_group(
            lambda: self.project.active_editor is None
        )
        def quit():
            self.project.save()
            main_frame.Close()
        quit_group.add_tool(
            wx.ART_QUIT,
            quit,
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

    @rltime("update toolbar")
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
class TableOfContents(VerticalBasePanel):

    def _create_gui(self):
        self.SetMinSize((250, -1))
        self.SetBackgroundColour((255, 255, 255))
        self.SetDropTarget(TableOfContentsDropTarget(self, self.values["project"]))
        self._create_unhoist_button()
        self._create_page_container()

    @rltime("update toc")
    def _update_gui(self):
        self._update_unhoist_button()
        self._update_page_container()
    def _create_unhoist_button(self):
        self.unhoist_button = self.AppendChild(
            wx.Button(self, label="unhoist"),
            flag=wx.EXPAND
        )
        self.unhoist_button.Bind(
            wx.EVT_BUTTON,
            lambda event: setattr(self.values["project"], "hoisted_page", None)
        )

    def _update_unhoist_button(self):
        self.unhoist_button.Show(self._get_hoisted_page() is not None)
    def _create_page_container(self):
        self.page_container = self.AppendChild(
            VerticalScrolledWindow(self),
            flag=wx.EXPAND,
            proportion=1
        )
        self.row_widgets = []

    def _update_page_container(self):
        self.row_index = 0
        self.drop_points = []
        if self._get_hoisted_page() is None:
            self._flatten_page(self.values["project"].get_page())
        else:
            self._flatten_page(self._get_hoisted_page())
        while self.row_index < len(self.row_widgets):
            for widget in self.row_widgets.pop(-1):
                widget.Destroy()

    def _flatten_page(self, page, indentation=0):
        is_collapsed = self.values["project"].is_collapsed(page.id)
        divider = self._get_or_create_row(page, indentation)
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
                divider = self._flatten_page(child, indentation+1)
                self.drop_points.append(TableOfContentsDropPoint(
                    divider=divider,
                    indentation=indentation+1,
                    parent_page_id=page.id,
                    before_page_id=None if next_child is None else next_child.id
                ))
        return divider

    def _get_or_create_row(self, page, indentation):
        if self.row_index < len(self.row_widgets):
            row, divider = self.row_widgets[self.row_index]
            row.UpdateGui(project=self.values["project"], page=page, indentation=indentation)
        else:
            row = self.page_container.AppendChild(
                TableOfContentsRow(self.page_container, project=self.values["project"], page=page, indentation=indentation),
                flag=wx.EXPAND
            )
            divider = self.page_container.AppendChild(
                Divider(self.page_container, padding=0, height=2),
                flag=wx.EXPAND
            )
            self.row_widgets.append((row, divider))
        self.row_index += 1
        return divider
    def _get_hoisted_page(self):
        if self.values["project"].hoisted_page is None:
            return None
        else:
            return self.values["project"].get_page(self.values["project"].hoisted_page)
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
class TableOfContentsRow(HorizontalBasePanel):

    BORDER = 2
    INDENTATION_SIZE = 16

    def _create_gui(self):
        self._create_indent()
        self._create_expand_collapse()
        self._create_text()
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        for helper in [MouseEventHelper(self), MouseEventHelper(self.text)]:
            helper.OnClick = self._on_click
            helper.OnRightClick = self._on_right_click
            helper.OnDrag = self._on_drag

    def _create_indent(self):
        self.indent = self.AppendSpace()

    def _create_expand_collapse(self):
        self.expand_collapse = self.AppendChild(
            TableOfContentsButton(self, **self.values),
            flag=wx.EXPAND|wx.LEFT|wx.RESERVE_SPACE_EVEN_IF_HIDDEN,
            border=self.BORDER
        )

    def _create_text(self):
        self.text = self.AppendChild(
            TextProjection(self),
            flag=wx.ALL,
            border=self.BORDER
        )
    def _on_click(self):
        open_pages_gui(self, self.values["project"], [self.values["page"].id], column_index=0)

    def _on_right_click(self, event):
        menu = PageContextMenu(self.values["project"], self.values["page"])
        self.PopupMenu(menu)
        menu.Destroy()

    def _on_drag(self):
        data = RliterateDataObject("page", {
            "page_id": self.values["page"].id,
        })
        drag_source = wx.DropSource(self)
        drag_source.SetData(data)
        result = drag_source.DoDragDrop(wx.Drag_DefaultMove)

    def _on_enter_window(self, event):
        self.SetBackgroundColour((240, 240, 240))

    def _on_leave_window(self, event):
        self.SetBackgroundColour((255, 255, 255))
    def _update_gui(self):
        self.indent.SetSize(self.values["indentation"]*self.INDENTATION_SIZE)
        self.expand_collapse.UpdateGui(**self.values)
        self.text.UpdateGui(characters=self._get_characters())

    def _get_characters(self):
        if self.values["project"].is_open(self.values["page"].id):
            token_type = TokenType.RLiterate.Strong
        else:
            token_type = TokenType.RLiterate
        style = self.values["project"].get_style(token_type)
        return [
            Character.create(x, style)
            for x
            in self.values["page"].title
        ]
class TableOfContentsButton(GuiUpdatePanel):

    SIZE = 16

    def _create_gui(self):
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.SetMinSize((self.SIZE+1, -1))

    def _on_left_down(self, event):
        self.values["project"].toggle_collapsed(self.values["page"].id)

    def _on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.BLACK_BRUSH)
        render = wx.RendererNative.Get()
        (w, h) = self.Size
        render.DrawTreeItemButton(
            self,
            dc,
            (0, (h-self.SIZE)/2, self.SIZE, self.SIZE),
            flags=0 if self.values["project"].is_collapsed(self.values["page"].id) else wx.CONTROL_EXPANDED
        )
    def _update_gui(self):
        self.Show(bool(self.values["page"].children))
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
            lambda event: setattr(self.project, "hoisted_page", self.page.id),
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
class Workspace(HorizontalScrolledWindow, GuiUpdateMixin):

    def __init__(self, parent, **kwargs):
        HorizontalScrolledWindow.__init__(self, parent, style=wx.HSCROLL)
        GuiUpdateMixin.__init__(self, **kwargs)

    def _create_gui(self):
        self.SetDropTarget(WorkspaceDropTarget(self, self.project))
        self.space = self.AppendSpace()
        self.columns = []
    @rltime("update workspace")
    def _update_gui(self):
        if self.project.active_editor is not None:
            return
        self.SetBackgroundColour(self.project.theme.workspace_background)
        self._update_space()
        self._update_columns()
    @property
    def project(self):
        return self.values["project"]
    def _update_space(self):
        self.space.SetSize(self.project.theme.page_padding)
    def _update_columns(self):
        self.column_count_changed = False
        for index, page_ids in enumerate(self.project.columns):
            self._add_column(page_ids, index)
        while len(self.columns) > len(self.project.columns):
            self.columns.pop(-1).Destroy()
            self.column_count_changed = True
        if self.column_count_changed or self.columns[index].did_change("page_ids"):
            wx.CallAfter(self.ScrollToEnd)

    def _add_column(self, page_ids, index):
        if index < len(self.columns):
            self.columns[index].UpdateGui(
                project=self.project,
                index=index,
                page_ids=page_ids,
                selection=self.project.selection.get(index)
            )
        else:
            self.columns.append(self.AppendChild(
                Column(
                    self,
                    project=self.project,
                    index=index,
                    page_ids=page_ids,
                    selection=self.project.selection.get(index)
                ),
                flag=wx.EXPAND
            ))
            self.column_count_changed = True
        return self.columns[index]
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
class Column(VerticalScrolledWindow, GuiUpdateMixin):

    def __init__(self, parent, **kwargs):
        VerticalScrolledWindow.__init__(
            self,
            parent,
            style=wx.VSCROLL
        )
        GuiUpdateMixin.__init__(self, **kwargs)

    def _create_gui(self):
        self.Bind(EVT_HOVERED_TOKEN_CHANGED, self._on_hovered_token_changed)
        self.Bind(EVT_TOKEN_CLICK, self._on_token_click)
        self._containers = []
        self._space = self.AppendSpace()
    def _update_gui(self):
        self._adjust_space()
        self._adjust_size()
        self._adjust_containers()

    def _adjust_space(self):
        self._space.SetSize(self.project.theme.page_padding)

    def _adjust_size(self):
        self.MinSize = (
            self.project.theme.page_body_width+
            2*self.project.theme.container_border+
            self.project.theme.page_padding+
            self.project.theme.shadow_size,
            -1
        )

    def _adjust_containers(self):
        num_added = 0
        for index, page_id in enumerate(self.values["page_ids"]):
            if self.project.get_page(page_id) is not None:
                if index >= len(self._containers):
                    self._containers.append(
                        self.AppendChild(
                            PageContainer(
                                self,
                                project=self.project,
                                page_id=page_id,
                                selection=self.values["selection"].get(index)
                            ),
                            flag=wx.RIGHT|wx.BOTTOM|wx.EXPAND,
                            border=self.project.theme.page_padding
                        )
                    )
                else:
                    self._containers[index].UpdateGui(
                        project=self.project,
                        page_id=page_id,
                        selection=self.values["selection"].get(index)
                    )
                num_added += 1
        while len(self._containers) > num_added:
            self._containers.pop(-1).Destroy()
        # When?
        #self.ScrollToBeginning()

    @property
    def project(self):
        return self.values["project"]

    @property
    def index(self):
        return self.values["index"]
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
    def FindClosestDropPoint(self, screen_pos):
        return find_first(
            self._containers,
            lambda container: container.FindClosestDropPoint(screen_pos)
        )
class PageContainer(VerticalBasePanel):

    @property
    def project(self):
        return self.values["project"]

    @property
    def page_id(self):
        return self.values["page_id"]

    @property
    def selection(self):
        return self.values["selection"]
    def _create_gui(self):
        self._create_first_row()
        self._create_second_row()
        MouseEventHelper.bind(
            [
                self.inner_container,
                self.right,
                self.right_border,
                self.bottom,
                self.bottom_border,
            ],
            right_click=lambda event:
                SimpleContextMenu.ShowRecursive(self)
        )

    def _create_first_row(self):
        first_row = self.AppendChild(
            HorizontalPanel(self),
            flag=wx.EXPAND,
            proportion=1
        )
        self.inner_container = first_row.AppendChild(
            VerticalPanel(first_row),
            flag=wx.EXPAND,
            proportion=1
        )
        self.page, self.page_sizer = self.inner_container.AppendChildWithSizer(
            PagePanel(
                self.inner_container,
                project=self.project,
                page_id=self.page_id,
                selection=self.selection.get(self.page_id)
            ),
            flag=wx.ALL|wx.EXPAND,
            proportion=1
        )
        self.right = first_row.AppendChild(
            VerticalPanel(first_row),
            flag=wx.EXPAND
        )
        self.right_space = self.right.AppendSpace()
        self.right_border = self.right.AppendChild(
            wx.Panel(self.right),
            flag=wx.EXPAND,
            proportion=1
        )

    def _create_second_row(self):
        self.bottom = self.AppendChild(
            HorizontalPanel(self),
            flag=wx.EXPAND
        )
        self.bottom_space = self.bottom.AppendSpace()
        self.bottom_border = self.bottom.AppendChild(
            wx.Panel(self.bottom),
            flag=wx.EXPAND,
            proportion=1
        )
    def _update_gui(self):
        self.page.UpdateGui(
            project=self.project,
            page_id=self.page_id,
            selection=self.selection.get(self.page_id)
        )
        self.inner_container.SetBackgroundColour((255, 255, 255))
        self.right_border.SetBackgroundColour((150, 150, 150))
        self.bottom_border.SetBackgroundColour((150, 150, 150))
        self.right.MinSize = (self.project.theme.shadow_size, -1)
        self.right_space.SetSize(self.project.theme.shadow_size)
        self.bottom.MinSize = (-1, self.project.theme.shadow_size)
        self.bottom_space.SetSize(self.project.theme.shadow_size)
        self.page_sizer.Border = self.project.theme.container_border
    def CreateContextMenu(self):
        menu = SimpleContextMenu("Page")
        menu.AppendItem("Change width", lambda:
            SettingsDialog(
                wx.GetTopLevelParent(self),
                self.project
            ).Show()
        )
        return menu
    def FindClosestDropPoint(self, screen_pos):
        return self.page.FindClosestDropPoint(screen_pos)
class PagePanel(VerticalBasePanel):

    @property
    def project(self):
        return self.values["project"]

    @property
    def page_id(self):
        return self.values["page_id"]

    @property
    def selection(self):
        return self.values["selection"]
    def _create_gui(self):
        self._create_title()
        self._create_top_divider()
        self._create_paragraph_container()
        self._create_add_button()
        MouseEventHelper.bind([self], right_click=lambda event:
            SimpleContextMenu.ShowRecursive(self)
        )

    def _create_title(self):
        self.title = self.AppendChild(Title(
            self,
            project=self.project,
            page=self.project.get_page(self.page_id),
            selection=self.selection.get("title")
        ), flag=wx.EXPAND)

    def _create_top_divider(self):
        self.top_divider = self.AppendChild(
            self._create_divider(self),
            flag=wx.EXPAND
        )

    def _create_paragraph_container(self):
        self.paragraph_container = self.AppendChild(
            VerticalPanel(self),
            flag=wx.EXPAND
        )
        self.paragraph_rows = []

    def _create_add_button(self):
        add_button = self.AppendChild(
            wx.BitmapButton(
                self,
                bitmap=wx.ArtProvider.GetBitmap(
                    wx.ART_ADD_BOOKMARK,
                    wx.ART_BUTTON,
                    (16, 16)
                ),
                style=wx.NO_BORDER
            ),
            flag=wx.ALIGN_RIGHT,
            border=self.project.theme.paragraph_space
        )
        add_button.Bind(wx.EVT_BUTTON, self._on_add_button)

    def _on_add_button(self, event):
        self.project.add_paragraph(self.page_id)

    def _update_gui(self):
        self._update_title()
        self._update_paragraphs()
        self.MinSize = (
            self.project.theme.page_body_width,
            -1
        )

    def _update_title(self):
        self.title.UpdateGui(
            project=self.project,
            page=self.project.get_page(self.page_id),
            selection=self.selection.get("title")
        )

    def _update_paragraphs(self):
        self.drop_points = []
        divider = self.top_divider
        index = 0
        for index, paragraph in enumerate(self.project.get_page(self.page_id).paragraphs):
            self.drop_points.append(PageDropPoint(
                divider=divider,
                page_id=self.page_id,
                next_paragraph_id=paragraph.id
            ))
            divider = self._render_paragraph(index, paragraph)
        self.drop_points.append(PageDropPoint(
            divider=divider,
            page_id=self.page_id,
            next_paragraph_id=None
        ))
        while index < len(self.paragraph_rows) - 1:
            for widget in self.paragraph_rows.pop(-1):
                widget.Destroy()

    def _render_paragraph(self, index, paragraph):
        widget_class = {
            "text": Text,
            "quote": Quote,
            "list": List,
            "code": Code,
            "image": Image,
            "expanded_code": ExpandedCode,
            "factory": Factory,
        }[paragraph.type]
        while index < len(self.paragraph_rows) and type(self.paragraph_rows[index][0]) != widget_class:
            for widget in self.paragraph_rows.pop(index):
                widget.Destroy()
        if index < len(self.paragraph_rows):
            widget, divider = self.paragraph_rows[index]
            widget.UpdateGui(
                project=self.project,
                page_id=self.page_id,
                paragraph=paragraph,
                selection=self.selection.get("paragraph").get(paragraph.id)
            )
            return divider
        else:
            widget = self.paragraph_container.AppendChild(widget_class(
                self.paragraph_container,
                project=self.project,
                page_id=self.page_id,
                paragraph=paragraph,
                selection=self.selection.get("paragraph").get(paragraph.id)
            ), flag=wx.EXPAND)
            divider = self.paragraph_container.AppendChild(
                self._create_divider(self.paragraph_container),
                flag=wx.EXPAND
            )
            self.paragraph_rows.append((widget, divider))
            return divider

    def _create_divider(self, parent):
        return Divider(
            parent,
            padding=(self.project.theme.paragraph_space-3)/2,
            height=3
        )
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
class Title(HorizontalBasePanel):

    def _create_gui(self):
        self.Font = create_font(**self.project.theme.title_font)
        self.text = self.AppendChild(TextProjection(
            self,
            characters=self._get_characters(),
            max_width=self.project.theme.page_body_width
        ), flag=wx.EXPAND, proportion=1)
        MouseEventHelper.bind(
            [self.text],
            double_click=lambda event:
                self._select(event.Position)
            ,
            right_click=lambda event:
                SimpleContextMenu.ShowRecursive(self)
        )
        self.text.Bind(wx.EVT_CHAR, self._on_char)

    def _update_gui(self):
        self.text.UpdateGui(
            characters=self._get_characters(),
            max_width=self.project.theme.page_body_width
        )
        if self.selection.present:
            self.text.SetFocus()
            self.text.DONT_RESET_FOCUS = True
        else:
            self.text.DONT_RESET_FOCUS = False
        self.text.SetToolTipString(self.page.full_title)

    def _get_characters(self):
        characters = []
        for index, character in list(enumerate(self.page.title))+[(len(self.page.title), " ")]:
            characters.append(Character.create(
                character,
                self.project.get_style(TokenType.RLiterate),
                marker="beam" if self.selection.present and self.selection.value == index else None,
                extra=index
            ))
        return characters

    def _on_char(self, event):
        if self.selection.present:
            character = event.GetUnicodeKey()
            if character >= 32:
                text = unichr(character)
                with self.project.notify():
                    self.page.set_title(self.page.title[:self.selection.value]+text+self.page.title[self.selection.value:])
                    self.project.selection = self.selection.create(self.selection.value+1)
            elif event.GetKeyCode() == wx.WXK_BACK:
                with self.project.notify():
                    self.page.set_title(self.page.title[:self.selection.value-1]+self.page.title[self.selection.value:])
                    self.project.selection = self.selection.create(self.selection.value-1)

    def _select(self, pos):
        character = self.text.GetClosestCharacter(pos)
        if character is None:
            self.project.selection = self.selection.create(0)
        else:
            self.project.selection = self.selection.create(character.extra)

    @property
    def project(self):
        return self.values["project"]

    @property
    def page(self):
        return self.values["page"]

    @property
    def selection(self):
        return self.values["selection"]
class Text(ParagraphBase):

    def CreateView(self):
        return TextView(
            self,
            self.project,
            self._tokens(),
            self
        )

    def _update_paragraph_gui(self):
        self.view.UpdateTokens(
            self.project,
            self._tokens(),
            self.project.theme.page_body_width
        )

    def _tokens(self):
        return [
            token.with_extra("text_index", (token.extra["fragment_index"],))
            for token in self.paragraph.tokens
        ]

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
            max_width=project.theme.page_body_width-indented,
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
        self.Font = create_font(**project.theme.text_font)
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
        self.Font = create_font(**project.theme.editor_font)
        self.project = project
        self.paragraph = paragraph

    def Save(self):
        self.paragraph.text_version = self.Value
class Quote(Text):

    INDENT = 20

    def CreateView(self):
        view = HorizontalPanel(self)
        view.AppendSpace(self.INDENT)
        self.text_view = view.AppendChild(
            TextView(
                view,
                self.project,
                self._tokens(),
                self,
                indented=self.INDENT
            ),
            flag=wx.EXPAND,
            proportion=1
        )
        return view

    def _update_paragraph_gui(self):
        self.text_view.UpdateTokens(
            self.project,
            self._tokens(),
            self.project.theme.page_body_width-self.INDENT
        )

    def AddContextMenuItems(self, menu):
        menu.AppendItem(
            "To text",
            lambda: self.paragraph.update({"type": "text"})
        )
class List(ParagraphBase):

    INDENT = 20

    def CreateView(self):
        view = VerticalPanel(self)
        view.Font = create_font(**self.project.theme.text_font)
        self.add_items(view, self.paragraph.children, self.paragraph.child_type)
        return view

    def CreateEdit(self, extra):
        return TextEdit(
            self,
            self.project,
            self.paragraph,
            self.view,
            extra
        )

    def add_items(self, view, items, child_type, indicies=[]):
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
            view.AppendChild(inner_sizer, flag=wx.EXPAND)
            self.add_items(view, item.children, item.child_type, indicies+[index])

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
        return CodeView(
            self,
            project=self.project,
            paragraph=self.paragraph,
            base=self
        )

    def CreateEdit(self, extra):
        return CodeEditor(self, self.project, self.paragraph, self.view, extra)

    def AddContextMenuItems(self, menu):
        menu.AppendItem(
            "Create expanded view",
            lambda: self.project.add_paragraph(
                self.page_id,
                before_id=self.paragraph.next_id,
                paragraph_dict={
                    "type": "expanded_code",
                    "code_id": self.paragraph.id,
                }
            )
        )

    @rltime("update code view")
    def _update_paragraph_gui(self):
        self.view.UpdateGui(
            project=self.project,
            paragraph=self.paragraph,
            base=self
        )
class CodeView(VerticalBasePanel):

    BORDER = 0
    PADDING = 5

    @property
    def project(self):
        return self.values["project"]

    @property
    def paragraph(self):
        return self.values["paragraph"]

    @property
    def base(self):
        return self.values["base"]

    def _create_gui(self):
        self.Font = create_font(**self.project.theme.code_font)
        self.path = self.AppendChild(
            self._create_path(),
            flag=wx.ALL|wx.EXPAND, border=self.BORDER
        )
        self.code = self.AppendChild(
            self._create_code(),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetBackgroundColour((243, 236, 219))

    def _update_gui(self):
        self.path.Show(not self.paragraph.path.is_empty)
        self.path_token_view.UpdateTokens(
            self.project,
            self._create_path_tokens(self.paragraph.path),
            self.project.theme.page_body_width-2*self.PADDING
        )
        self.body_token_view.UpdateTokens(
            self.project,
            self._highlight_variables(self.paragraph.tokens),
            self.project.theme.page_body_width-2*self.PADDING
        )
    def _create_path(self):
        panel = HorizontalPanel(self)
        panel.SetBackgroundColour((248, 241, 223))
        self.path_token_view = panel.AppendChild(
            TokenView(
                panel,
                self.project,
                self._create_path_tokens(self.paragraph.path),
                max_width=self.project.theme.page_body_width-2*self.PADDING
            ),
            flag=wx.ALL|wx.EXPAND,
            border=self.PADDING
        )
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

    @rltime("create path tokens")
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
        panel = HorizontalPanel(self)
        panel.SetBackgroundColour((253, 246, 227))
        self.body_token_view = panel.AppendChild(
            TokenView(
                panel,
                self.project,
                self._highlight_variables(self.paragraph.tokens),
                max_width=self.project.theme.page_body_width-2*self.PADDING
            ),
            flag=wx.ALL|wx.EXPAND,
            border=self.PADDING,
            proportion=1
        )
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

    @rltime("create code tokens")
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
            menu = SimpleContextMenu("Path")
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
            menu.Popup(self)
        elif token is not None and token.extra.get("variable") is not None:
            rename_value = self.project.lookup_variable(token.extra["variable"]) or token.extra["variable"]
            rename_message = "Rename '{}'".format(rename_value)
            menu = SimpleContextMenu("Variable")
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
                return lambda: self.Parent.Parent.Parent.Parent.Parent.Parent.Parent.OpenPage(page.id)
            for page in self._find_variable_usages(token.extra["variable"]):
                menu.AppendItem(
                    "{}".format(page.full_title),
                    create_open_page_handler(page)
                )
            menu.AppendSeparator()
            menu.AppendItem("Possible usages:", lambda: None)
            for page in self._find_variable_pages(rename_value):
                menu.AppendItem(
                    "{}".format(page.full_title),
                    create_open_page_handler(page)
                )
            menu.Popup(self)
        else:
            return CONTINUE_PROCESSING

    def _find_variable_pages(self, name):
        for page in self.project.iter_pages():
            if self._page_has_variable(page, name):
                yield page

    def _find_variable_usages(self, variable_id):
        for page in self.project.iter_pages():
            if self._page_uses_variable(page, variable_id):
                yield page

    def _page_has_variable(self, page, name):
        pattern = re.compile(r"\b{}\b".format(re.escape(name)))
        for text_fragment in page.iter_text_fragments():
            if text_fragment.type == "code":
                if pattern.search(text_fragment.text):
                    return True
        for code_fragment in page.iter_code_fragments():
            if code_fragment.type == "code":
                if pattern.search(code_fragment.text):
                    return True

    def _page_uses_variable(self, page, variable_id):
        for text_fragment in page.iter_text_fragments():
            if text_fragment.type == "variable" and text_fragment.id == variable_id:
                return True
        for code_fragment in page.iter_code_fragments():
            if code_fragment.type == "variable" and code_fragment.id == variable_id:
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
class CodeEditor(VerticalPanel):

    def __init__(self, parent, project, paragraph, view, extra):
        VerticalPanel.__init__(self, parent, size=(-1, max(90, view.Size[1])))
        self.project = project
        self.paragraph = paragraph
        self.view = view
        self.extra = extra
        self._create_gui()
        self._focus()

    def _create_gui(self):
        self.Font = create_font(**self.project.theme.editor_font)
        self.header = self.AppendChild(
            HorizontalPanel(self),
            flag=wx.ALL|wx.EXPAND
        )
        self.path = self.header.AppendChild(
            SelectionableTextCtrl(
                self.header,
                value=self.paragraph.path.text_version
            ),
            flag=wx.ALL|wx.EXPAND,
            proportion=1
        )
        self.language = self.header.AppendChild(
            SelectionableTextCtrl(
                self.header,
                value=self.paragraph.raw_language
            ),
            flag=wx.ALL,
            proportion=0
        )
        self.text = self.AppendChild(
            MultilineTextCtrl(
                self,
                value=self.paragraph.text_version
            ),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND,
            proportion=1
        )
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
            self.paragraph.raw_language = self.language.Value
class Image(ParagraphBase):

    PADDING = 30

    def CreateView(self):
        view = VerticalPanel(self)
        bitmap = view.AppendChild(
            wx.StaticBitmap(
                view,
                bitmap=base64_to_bitmap(
                    self.paragraph.image_base64,
                    self.project.theme.page_body_width
                )
            ),
            flag=wx.ALIGN_CENTER
        )
        view.AppendChild(
            TextView(
                view,
                self.project,
                self.paragraph.tokens,
                self,
                indented=2*self.PADDING
            ),
            flag=wx.ALIGN_CENTER
        )
        self.BindMouse(view, [view, bitmap])
        return view

    def CreateEdit(self, extra):
        return ImageEdit(
            self,
            self.project,
            self.paragraph,
            self.view
        )
class ImageEdit(VerticalPanel):

    def __init__(self, parent, project, paragraph, view):
        VerticalPanel.__init__(self, parent)
        self.Font = create_font(**project.theme.editor_font)
        self.project = project
        self.paragraph = paragraph
        self.image = self.AppendChild(
            wx.StaticBitmap(
                self,
                bitmap=base64_to_bitmap(
                    paragraph.image_base64,
                    self.project.theme.page_body_width
                )
            ),
            flag=wx.ALIGN_CENTER
        )
        self.text = self.AppendChild(
            MultilineTextCtrl(self, value=fragments_to_text(paragraph.fragments)),
            flag=wx.EXPAND
        )
        paste_button = self.AppendChild(
            wx.Button(self, label="Paste")
        )
        paste_button.Bind(wx.EVT_BUTTON, self._on_paste)
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
                self.project.theme.page_body_width
            ).ConvertToBitmap())
            self.image_base64 = bitmap_to_base64(bitmap)
            self.GetTopLevelParent().ChildReRendered()

    def Save(self):
        value = {"fragments": text_to_fragments(self.text.Value)}
        if self.image_base64:
            value["image_base64"] = self.image_base64
        self.paragraph.update(value)
class ExpandedCode(ParagraphBase):

    def CreateView(self):
        self.Font = create_font(**self.project.theme.code_font)
        view = VerticalPanel(self)
        token_view = view.AppendChild(
            TokenView(
                view,
                self.project,
                self.paragraph.tokens,
                max_width=self.project.theme.page_body_width
            ),
            flag=wx.ALL|wx.EXPAND
        )
        MouseEventHelper.bind(
            [view, token_view],
            drag=self.DoDragDrop,
            right_click=lambda event: self.ShowContextMenu()
        )
        view.SetBackgroundColour((240, 240, 240))
        return view
class Factory(ParagraphBase):

    def CreateView(self):
        view = VerticalPanel(self)
        MouseEventHelper.bind(
            [view],
            drag=self.DoDragDrop,
            right_click=lambda event: self.ShowContextMenu()
        )
        view.SetBackgroundColour((240, 240, 240))
        view.AppendChild(
            wx.StaticText(view, label="Factory"),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=self.project.theme.paragraph_space
        )
        self.button_panel = view.AppendChild(
            HorizontalPanel(view),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=self.project.theme.paragraph_space
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
        view.AppendSpace(self.project.theme.paragraph_space)
        return view

    def _add_button(self, text, value):
        def click_handler(event):
            if self.project.active_editor is None:
                self.paragraph.update(value)
            else:
                show_edit_in_progress_error(self)
        button = self.button_panel.AppendChild(
            wx.Button(self.button_panel, label=text),
            flag=wx.ALL,
            border=2
        )
        button.Bind(wx.EVT_BUTTON, click_handler)
class SettingsDialog(wx.Dialog):

    def __init__(self, parent, project):
        wx.Dialog.__init__(self, parent)
        self.project = project
        self._init_gui()

    def _init_gui(self):
        spin = wx.SpinCtrl(
            self,
            value="{}".format(self.project.theme.page_body_width),
            min=100,
            max=10000
        )
        self.Bind(
            wx.EVT_SPINCTRL,
            lambda event: setattr(
                self.project.theme,
                "page_body_width",
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
class Divider(VerticalPanel):

    def __init__(self, parent, padding=0, height=1):
        VerticalPanel.__init__(self, parent, size=(-1, height+2*padding))
        self.line = wx.Panel(self, size=(-1, height))
        self.line.SetBackgroundColour((255, 100, 0))
        self.line.Hide()
        self.AppendStretch(1)
        self.hsizer = self.AppendChild(
            wx.BoxSizer(wx.HORIZONTAL),
            flag=wx.EXPAND|wx.RESERVE_SPACE_EVEN_IF_HIDDEN
        )
        self.AppendStretch(1)
        MouseEventHelper.bind(
            [self, self.line],
            right_click=lambda event:
                SimpleContextMenu.ShowRecursive(self)
        )

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
class Character(namedtuple("Character", "text style marker extra")):

    @classmethod
    def create(cls, text, style, marker=None, extra=None):
        return cls(text, style, marker, extra)
class Box(object):

    def __init__(self, char):
        self.char = char
        self.rect = wx.Rect(0, 0, 0, 0)
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

    def __eq__(self, other):
        return (
            isinstance(other, Token) and
            self.text == other.text and
            self.token_type == other.token_type and
            self.extra == other.extra and
            self.index == other.index
        )

    def __ne__(self, other):
        return not (self == other)

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
class CodeExpander(object):

    def __init__(self, document):
        self.document = document
        self._parts = defaultdict(list)
        self._ids = {}
        self._collect_parts(self.document.get_page())

    def _collect_parts(self, page):
        for paragraph in page.paragraphs:
            if paragraph.type == "code":
                self._parts[(
                    tuple(paragraph.path.filepath),
                    tuple(paragraph.path.chunkpath),
                )].append(paragraph)
                self._ids[paragraph.id] = paragraph
        for child in page.children:
            self._collect_parts(child)

    def generate_files(self):
        for key in self._parts.keys():
            filepath = self._get_filepath(key)
            if filepath:
                chain = self._expand(self._parts[key])
                with open(filepath, "w") as f:
                    f.write("".join(char.value for char in chain))

    def expand_id(self, paragraph_id):
        if paragraph_id in self._ids:
            return (self._ids[paragraph_id], self._expand([self._ids[paragraph_id]]))
        else:
            chain = CharChain()
            chain.append("Could not find {}".format(paragraph_id))
            return (None, chain)

    def _expand(self, paragraphs):
        self._tabstops = []
        chain = CharChain()
        self._render(chain, paragraphs)
        chain.align_tabstops()
        return chain

    def _render(self, chain, paragraphs, prefix="", blank_lines_before=0):
        for index, paragraph in enumerate(paragraphs):
            if index > 0:
                self._add_text_to_chain("\n"*blank_lines_before, chain, prefix)
            for fragment in paragraph.fragments:
                if fragment.type == "chunk":
                    self._render(
                        chain,
                        self._parts[(
                            tuple(paragraph.path.filepath),
                            tuple(paragraph.path.chunkpath)+tuple(fragment.path)
                        )],
                        prefix=prefix+fragment.prefix,
                        blank_lines_before=fragment.blank_lines_before
                    )
                elif fragment.type == "variable":
                    self._add_text_to_chain(fragment.name, chain, prefix)
                elif fragment.type == "code":
                    self._add_text_to_chain(fragment.text, chain, prefix)
                elif fragment.type == "tabstop":
                    self._tabstops.append(fragment.index)
        self._mark_tabstops(chain)
        if chain.tail is not None and chain.tail.value != "\n":
            chain.append("\n")

    def _add_text_to_chain(self, text, chain, prefix):
        for char in text:
            if chain.tail is None or (chain.tail.value == "\n" and char != "\n"):
                chain.append(prefix)
            self._mark_tabstops(chain)
            chain.append(char)

    def _mark_tabstops(self, chain):
        while self._tabstops:
            chain.mark_tabstop(self._tabstops.pop())

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
                "expanded_code": self.paragraph_expanded_code,
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
                TokenType.RLiterate.Variable: self.token_variable,
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

    def token_variable(self, token):
        with self.tag("code", newlines=False):
            self.escaped(token.text)

    def token_default(self, token):
        self.escaped(token.text)

    def paragraph_code(self, code):
        with self.tag("div", args={"class": "rliterate-code"}):
            if not code.path.is_empty:
                with self.tag("div", args={"class": "rliterate-code-header"}):
                    with self.tag("ol", args={"class": "rliterate-code-path"}):
                        for path in code.path.filepath:
                            with self.tag("li", newlines=False):
                                self.escaped(path)
                        for path in code.path.chunkpath:
                            with self.tag("li", newlines=False):
                                with self.tag("span", args={"class": pygments.token.STANDARD_TYPES.get(TokenType.Comment.Preproc, "")}):
                                    self.escaped(path)
            with self.tag("div", args={"class": "rliterate-code-body"}):
                with self.tag("pre", newlines=False):
                    for token in code.tokens:
                        with self.tag(
                            "span",
                            newlines=False,
                            args={"class": pygments.token.STANDARD_TYPES.get(token.token_type, "")}
                        ):
                            self.escaped(token.text)

    def paragraph_expanded_code(self, expanded_code):
        with self.tag("div", args={"class": "rliterate-code"}):
            with self.tag("div", args={"class": "rliterate-code-body"}):
                with self.tag("pre", newlines=False):
                    for token in expanded_code.tokens:
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
    return TextParser().parse(text)
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
