# This file is automatically extracted from rliterate.rliterate.


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
from pygments.token import Token, STANDARD_TYPES
import wx
import wx.lib.newevent


FragmentClick, EVT_FRAGMENT_CLICK = wx.lib.newevent.NewCommandEvent()
HoveredFragmentChanged, EVT_HOVERED_FRAGMENT_CHANGED = wx.lib.newevent.NewCommandEvent()
EditStart, EVT_EDIT_START = wx.lib.newevent.NewCommandEvent()
PAGE_BODY_WIDTH = 600
PAGE_PADDING = 13
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 15
CONTAINER_BORDER = PARAGRAPH_SPACE
class Editable(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.view = self.CreateView()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.view, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)
        self.view.Bind(EVT_EDIT_START, self.OnEditStart)

    def OnEditStart(self, event):
        with flicker_free_drawing(self):
            self.edit = self.CreateEdit()
            self.edit.SetFocus()
            self.sizer.Add(self.edit, flag=wx.EXPAND, proportion=1)
            self.sizer.Hide(self.view)
            self.GetTopLevelParent().Layout()
class ParagraphBase(Editable):

    def __init__(self, parent, project, page_id, paragraph):
        self.project = project
        self.page_id = page_id
        self.paragraph = paragraph
        Editable.__init__(self, parent)

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
        self._add_base(menu)
        self.PopupMenu(menu)
        menu.Destroy()

    def _add_base(self, menu):
        menu.AppendItem(
            "Delete",
            lambda: self.project.delete_paragraph(
                page_id=self.page_id,
                paragraph_id=self.paragraph.id
            )
        )
        menu.AppendItem(
            "Edit in gvim",
            lambda: self.paragraph.update({
                "text": edit_in_gvim(self.paragraph.text, self.paragraph.filename)
            })
        )
        menu.AppendSeparator()
        menu.AppendItem(
            "To quote",
            lambda: self.paragraph.update({"type": "quote"})
        )
        menu.AppendItem(
            "To text",
            lambda: self.paragraph.update({"type": "text"})
        )
        menu.AppendItem(
            "To list",
            lambda: self.paragraph.update({"type": "list"})
        )
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
class RichTextDisplay(wx.Panel):
    def __init__(self, parent, project, fragments, **kwargs):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.fragments = fragments
        self.line_height = kwargs.get("line_height", 1)
        self.max_width = kwargs.get("max_width", 100)
        self._set_fragments()
        self.Bind(wx.EVT_PAINT, self._on_paint)
    def _set_fragments(self):
        dc = wx.MemoryDC()
        dc.SetFont(self.GetFont())
        dc.SelectObject(wx.EmptyBitmap(1, 1))
        w, h = self._calculate_fragments(dc)
        self.SetMinSize((w, h))

    def _calculate_fragments(self, dc):
        self.draw_fragments = []
        x = 0
        y = 0
        max_x, max_y = dc.GetTextExtent("M")
        line_height_pixels = int(round(dc.GetTextExtent("M")[1]*self.line_height))
        for fragment in self._newline_fragments():
            if fragment is None:
                x = 0
                y += line_height_pixels
                max_y = max(max_y, y)
                continue
            style = self.project.get_style(fragment.token)
            style.apply_to_wx_dc(dc, self.GetFont())
            w, h = dc.GetTextExtent(fragment.text)
            if x > 0 and x+w > self.max_width:
                x = 0
                y += line_height_pixels
            self.draw_fragments.append((fragment, style, wx.Rect(x, y, w, h)))
            max_x = max(max_x, x+w)
            max_y = max(max_y, y+line_height_pixels)
            x += w
        return (max_x, max_y)

    def _newline_fragments(self):
        for fragment in self.fragments:
            if "\n" in fragment.text:
                for x in insert_between(None, fragment.text.split("\n")):
                    if x is None:
                        yield x
                    else:
                        for subfragment in Fragment(x, token=fragment.token, **fragment.extra).word_split():
                            yield subfragment
            else:
                for subfragment in fragment.word_split():
                    yield subfragment
    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        for fragment, style, box in self.draw_fragments:
            style.apply_to_wx_dc(dc, self.GetFont())
            dc.DrawText(fragment.text, box.X, box.Y)
    def GetFragment(self, position):
        for fragment, style, box in self.draw_fragments:
            if box.Contains(position):
                return fragment
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
        self.Scroll(*self.Size)
class MultilineTextCtrl(wx.TextCtrl):

    MIN_HEIGHT = 50

    def __init__(self, parent, value, size=wx.DefaultSize):
        w, h = size
        size = (w, max(h, self.MIN_HEIGHT))
        wx.TextCtrl.__init__(
            self,
            parent,
            style=wx.TE_MULTILINE,
            value=value,
            size=size
        )
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

    def apply_to_wx_dc(self, dc, base_font):
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
        dc.SetFont(font)
        dc.SetTextForeground(self.color_rgb)
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
class MainFrame(wx.Frame):

    def __init__(self, filepath):
        wx.Frame.__init__(self, None)
        project = Project(filepath)
        workspace = Workspace(self, project)
        toc = TableOfContents(self, project)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(toc, flag=wx.EXPAND, proportion=0)
        sizer.Add(workspace, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)
class TableOfContents(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, size=(250, -1))
        self.project_listener = Listener(
            self._re_render_from_event,
            "document", "layout.toc", "layout.workspace"
        )
        self.SetProject(project)
        self.SetDropTarget(TableOfContentsDropTarget(self, self.project))
        self._render()

    def SetProject(self, project):
        self.project = project
        self.project_listener.set_observable(self.project)
    def _re_render_from_event(self, event):
        wx.CallAfter(self._re_render)
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
            self.Layout()
    def _render_unhoist_button(self):
        if self.project.get_hoisted_page() is not None:
            self.unhoist_button = wx.Button(self, label="unhoist")
            self.unhoist_button.Bind(
                wx.EVT_BUTTON,
                lambda event: self.project.set_hoisted_page(None)
            )
            self.sizer.Insert(0, self.unhoist_button, flag=wx.EXPAND)
    def _render_page_container(self):
        self._render_page(self.project.get_page(self.project.get_hoisted_page()))

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
        client_pos = self.page_container.ScreenToClient(screen_pos)
        if self.page_container.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
            scroll_pos = (scroll_x, scroll_y) = self.page_container.CalcUnscrolledPosition(client_pos)
            y_distances = defaultdict(list)
            for drop_point in self.drop_points:
                y_distances[drop_point.y_distance_to(scroll_y)].append(drop_point)
            if y_distances:
                return min(
                    y_distances[min(y_distances.keys())],
                    key=lambda drop_point: drop_point.x_distance_to(scroll_x)
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
        self.project.open_pages([self.page.id], column_index=0)

    def _on_right_click(self):
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
            lambda event: self.project.open_pages([self.page.id], column_index=0),
            self.Append(wx.NewId(), "Open")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.open_pages([self.page.id]),
            self.Append(wx.NewId(), "Open append")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.open_pages(self.child_ids, column_index=0),
            self.Append(wx.NewId(), "Open with children")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.open_pages(self.child_ids),
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
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.page.delete(),
            self.Append(wx.NewId(), "Delete")
        )
class Workspace(CompactScrolledWindow):
    def __init__(self, parent, project):
        CompactScrolledWindow.__init__(self, parent, style=wx.HSCROLL)
        self.project_listener = Listener(
            self._re_render_from_event,
            "document",
            "layout.workspace"
        )
        self.SetProject(project)
        self.SetDropTarget(WorkspaceDropTarget(self, self.project))
        self._render()

    def SetProject(self, project):
        self.project = project
        self.project_listener.set_observable(self.project)
    def _render(self):
        with flicker_free_drawing(self):
            self.SetBackgroundColour((200, 200, 200))
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer.AddSpacer(PAGE_PADDING)
            self.SetSizer(self.sizer)
            self.columns = []
            self._re_render()

    def _re_render(self):
        with flicker_free_drawing(self):
            column_count_changed = self._ensure_num_columns(len(self.project.columns))
            last_column_changed_pages = False
            for index, page_ids in enumerate(self.project.columns):
                last_column_changed_pages = self.columns[index].SetPages(
                    self.project,
                    page_ids
                )
            self.Parent.Layout()
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
        column = Column(self, index=len(self.columns))
        self.sizer.Add(column, flag=wx.EXPAND)
        return column
    def _re_render_from_event(self, event):
        wx.CallAfter(self._re_render)
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
        self.project.move_paragraph(
            source_page=dropped_paragraph["page_id"],
            source_paragraph=dropped_paragraph["paragraph_id"],
            target_page=drop_point.page_id,
            before_paragraph=drop_point.next_paragraph_id
        )
class Column(CompactScrolledWindow):

    def __init__(self, parent, index):
        CompactScrolledWindow.__init__(
            self,
            parent,
            style=wx.VSCROLL,
            size=(PAGE_BODY_WIDTH+2*CONTAINER_BORDER+PAGE_PADDING+SHADOW_SIZE, -1)
        )
        self.project = None
        self.index = index
        self._page_ids = []
        self._setup_layout()
        self.Bind(EVT_HOVERED_FRAGMENT_CHANGED, self._on_hovered_fragment_changed)
        self.Bind(EVT_FRAGMENT_CLICK, self._on_fragment_click)

    def _on_hovered_fragment_changed(self, event):
        if event.fragment is not None and event.fragment.token in [
            Token.RLiterate.Link,
            Token.RLiterate.Reference,
        ]:
            event.widget.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            event.widget.SetDefaultCursor()

    def _on_fragment_click(self, event):
        if self.project is None:
            return
        if event.fragment.token == Token.RLiterate.Reference:
            self.project.open_pages(
                [event.fragment.extra["page_id"]],
                column_index=self.index+1
            )
        elif event.fragment.token == Token.RLiterate.Link:
            webbrowser.open(event.fragment.extra["url"])

    def _setup_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def SetPages(self, project, page_ids):
        self.project = project
        self.containers = []
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PAGE_PADDING)
        for page_id in page_ids:
            if project.get_page(page_id) is not None:
                container = PageContainer(self, project, page_id)
                self.sizer.Add(
                    container,
                    flag=wx.RIGHT|wx.BOTTOM|wx.EXPAND,
                    border=PAGE_PADDING
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
            border=SHADOW_SIZE
        )
        self.SetSizer(self.sizer)
        self.inner_sizer.AddSpacer(CONTAINER_BORDER)
        self.page = Page(self.inner_container, self.project, self.page_id)
        self.inner_sizer.Add(
            self.page,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,
            border=CONTAINER_BORDER
        )

    def FindClosestDropPoint(self, screen_pos):
        return self.page.FindClosestDropPoint(screen_pos)
class Page(wx.Panel):

    def __init__(self, parent, project, page_id):
        wx.Panel.__init__(self, parent)
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
        divider = Divider(self, padding=(PARAGRAPH_SPACE-3)/2, height=3)
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
            border=PARAGRAPH_SPACE
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
        self.project = project
        self.page = page
        Editable.__init__(self, parent)

    def CreateView(self):
        self.Font = create_font(size=16)
        view = RichTextDisplay(
            self,
            self.project,
            [Fragment(self.page.title)],
            max_width=PAGE_BODY_WIDTH
        )
        MouseEventHelper.bind(
            [view],
            double_click=lambda: post_edit_start(view)
        )
        return view

    def CreateEdit(self):
        edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.page.title)
        edit.Bind(
            wx.EVT_TEXT_ENTER,
            lambda _: self.page.set_title(self.edit.Value)
        )
        return edit
class Text(ParagraphBase):

    def CreateView(self):
        return TextView(
            self,
            self.project,
            self.paragraph.formatted_text,
            self
        )

    def CreateEdit(self):
        return TextEdit(
            self,
            self.project,
            self.paragraph,
            self.view
        )
class TextView(RichTextDisplay):

    def __init__(self, parent, project, fragments, base, indented=0):
        RichTextDisplay.__init__(
            self,
            parent,
            project,
            fragments,
            line_height=1.2,
            max_width=PAGE_BODY_WIDTH-indented
        )
        MouseEventHelper.bind(
            [self],
            drag=base.DoDragDrop,
            right_click=base.ShowContextMenu,
            double_click=lambda: post_edit_start(self),
            move=self._on_mouse_move,
            click=self._on_click
        )
        self.default_cursor = self.GetCursor()
        self.fragment = None

    def SetDefaultCursor(self):
        self.SetCursor(self.default_cursor)

    def _on_mouse_move(self, position):
        fragment = self.GetFragment(position)
        if fragment is not self.fragment:
            self.fragment = fragment
            post_hovered_fragment_changed(self, self.fragment)

    def _on_click(self):
        if self.fragment is not None:
            post_fragment_click(self, self.fragment)
class TextEdit(MultilineTextCtrl):

    def __init__(self, parent, project, paragraph, view):
        MultilineTextCtrl.__init__(
            self,
            parent,
            value=fragments_to_text(paragraph.fragments),
            size=(-1, view.Size[1])
        )
        self.Font = create_font(monospace=True)
        self.project = project
        self.paragraph = paragraph
        self.Bind(wx.EVT_CHAR, self._on_char)

    def _on_char(self, event):
        if event.KeyCode == wx.WXK_CONTROL_S:
            self._save()
        elif event.KeyCode == wx.WXK_RETURN and event.ControlDown():
            self._save()
        else:
            event.Skip()

    def _save(self):
        self.paragraph.update({"fragments": text_to_fragments(self.Value)})
class Quote(Text):

    INDENT = 20

    def CreateView(self):
        view = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((self.INDENT, 1))
        sizer.Add(
            TextView(
                view,
                self.project,
                self.paragraph.formatted_text,
                self,
                indented=self.INDENT
            ),
            flag=wx.EXPAND,
            proportion=1
        )
        view.SetSizer(sizer)
        return view
class List(ParagraphBase):

    INDENT = 20

    def CreateView(self):
        view = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_items(view, sizer, self.paragraph.children, self.paragraph.child_type)
        view.SetSizer(sizer)
        return view

    def CreateEdit(self):
        return ListTextEdit(
            self,
            self.project,
            self.paragraph,
            self.view
        )

    def add_items(self, view, sizer, items, child_type, indent=0):
        for index, item in enumerate(items):
            inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
            inner_sizer.Add((self.INDENT*indent, 1))
            bullet = self._create_bullet_widget(view, child_type, index)
            inner_sizer.Add(bullet)
            inner_sizer.Add(
                TextView(
                    view,
                    self.project,
                    item.formatted_text,
                    self,
                    indented=self.INDENT*indent+bullet.GetMinSize()[0]
                ),
                proportion=1
            )
            sizer.Add(inner_sizer, flag=wx.EXPAND)
            self.add_items(view, sizer, item.children, item.child_type, indent+1)

    def _create_bullet_widget(self, view, list_type, index):
        return RichTextDisplay(
            view,
            self.project,
            [Fragment(self._get_bullet_text(list_type, index))]
        )

    def _get_bullet_text(self, list_type, index):
        if list_type == "ordered":
            return "{}. ".format(index + 1)
        else:
            return u"\u2022 "


class ListTextEdit(MultilineTextCtrl):

    def __init__(self, parent, project, paragraph, view):
        MultilineTextCtrl.__init__(
            self,
            parent,
            value=list_to_text(paragraph),
            size=(-1, view.Size[1])
        )
        self.Font = create_font(monospace=True)
        self.project = project
        self.paragraph = paragraph
        self.Bind(wx.EVT_CHAR, self._on_char)

    def _on_char(self, event):
        if event.KeyCode == wx.WXK_CONTROL_S:
            self._save()
        elif event.KeyCode == wx.WXK_RETURN and event.ControlDown():
            self._save()
        else:
            event.Skip()

    def _save(self):
        child_type, children = text_to_list(self.Value)
        self.paragraph.update({
            "child_type": child_type,
            "children": children
        })
class Code(ParagraphBase):

    def CreateView(self):
        return CodeView(self, self.project, self.paragraph, self)

    def CreateEdit(self):
        return CodeEditor(self, self.project, self.paragraph, self.view)
class CodeView(wx.Panel):

    BORDER = 0
    PADDING = 5

    def __init__(self, parent, project, paragraph, base):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.base = base
        self.Font = create_font(monospace=True)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        if paragraph.has_path:
            self.vsizer.Add(
                self._create_path(paragraph),
                flag=wx.ALL|wx.EXPAND, border=self.BORDER
            )
        self.vsizer.Add(
            self._create_code(paragraph),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetSizer(self.vsizer)
        self.SetBackgroundColour((243, 236, 219))

    def _create_path(self, paragraph):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((248, 241, 223))
        text = RichTextDisplay(
            panel,
            self.project,
            insert_between(
                Fragment(" / "),
                [Fragment(x, token=pygments.token.Token.RLiterate.Strong) for x in paragraph.path]
            ),
            max_width=PAGE_BODY_WIDTH-2*self.PADDING
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(text, flag=wx.ALL|wx.EXPAND, border=self.PADDING)
        panel.SetSizer(sizer)
        MouseEventHelper.bind(
            [panel, text],
            double_click=self._post_paragraph_edit_start,
            drag=self.base.DoDragDrop,
            right_click=self.base.ShowContextMenu
        )
        return panel

    def _create_code(self, paragraph):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((253, 246, 227))
        body = RichTextDisplay(
            panel,
            self.project,
            paragraph.formatted_text,
            max_width=PAGE_BODY_WIDTH-2*self.PADDING
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(body, flag=wx.ALL|wx.EXPAND, border=self.PADDING, proportion=1)
        panel.SetSizer(sizer)
        MouseEventHelper.bind(
            [panel, body],
            double_click=self._post_paragraph_edit_start,
            drag=self.Parent.DoDragDrop,
            right_click=self.Parent.ShowContextMenu
        )
        return panel

    def _post_paragraph_edit_start(self):
        post_edit_start(self)
class CodeEditor(wx.Panel):

    BORDER = 1
    PADDING = 3

    def __init__(self, parent, project, paragraph, view):
        wx.Panel.__init__(self, parent)
        self.Font = create_font(monospace=True)
        self.project = project
        self.paragraph = paragraph
        self.view = view
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(
            self._create_path(paragraph),
            flag=wx.ALL|wx.EXPAND, border=self.BORDER
        )
        self.vsizer.Add(
            self._create_code(paragraph),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.vsizer.Add(
            self._create_save(),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetSizer(self.vsizer)

    def _create_path(self, paragraph):
        self.path = wx.TextCtrl(
            self,
            value=" / ".join(paragraph.path)
        )
        return self.path

    def _create_code(self, paragraph):
        self.text = MultilineTextCtrl(
            self,
            value=paragraph.text,
            size=(-1, self.view.Size[1])
        )
        return self.text

    def _create_save(self):
        button = wx.Button(
            self,
            label="Save"
        )
        self.Bind(wx.EVT_BUTTON, self._on_save)
        return button

    def _on_save(self, event):
        self.paragraph.update({
            "path": self.path.Value.split(" / "),
            "text": self.text.Value,
        })
class Image(ParagraphBase):

    PADDING = 30

    def CreateView(self):
        view = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.StaticBitmap(
            view,
            bitmap=base64_to_bitmap(self.paragraph.image_base64)
        )
        sizer.Add(
            bitmap,
            flag=wx.ALIGN_CENTER
        )
        sizer.Add(
            TextView(
                view,
                self.project,
                self.paragraph.formatted_text,
                self,
                indented=2*self.PADDING
            ),
            flag=wx.ALIGN_CENTER
        )
        view.SetSizer(sizer)
        MouseEventHelper.bind(
            [view, bitmap],
            double_click=lambda: post_edit_start(view),
        )
        return view

    def CreateEdit(self):
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
        self.image = wx.StaticBitmap(self, bitmap=base64_to_bitmap(paragraph.image_base64))
        sizer.Add(self.image, flag=wx.ALIGN_CENTER)
        self.text = MultilineTextCtrl(self, value=fragments_to_text(paragraph.fragments))
        sizer.Add(self.text, flag=wx.EXPAND)
        paste_button = wx.Button(self, label="Paste")
        paste_button.Bind(wx.EVT_BUTTON, self._on_paste)
        sizer.Add(paste_button)
        save = wx.Button(self, label="Save")
        save.Bind(wx.EVT_BUTTON, self._on_save)
        sizer.Add(save)
        self.SetSizer(sizer)
        self.image_base64 = None

    def _on_paste(self, event):
        image_data = wx.BitmapDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(image_data)
            wx.TheClipboard.Close()
        if success:
            bitmap = image_data.GetBitmap()
            self.image.SetBitmap(fit_image(wx.ImageFromBitmap(bitmap), PAGE_BODY_WIDTH).ConvertToBitmap())
            self.image_base64 = bitmap_to_base64(bitmap)
            self.GetTopLevelParent().Layout()

    def _on_save(self, event):
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
            right_click=self.ShowContextMenu
        )
        view.SetBackgroundColour((240, 240, 240))
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer.Add(
            wx.StaticText(view, label="Factory"),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        self.vsizer.Add(
            self.hsizer,
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        text_button = wx.Button(self, label="Text")
        text_button.Bind(wx.EVT_BUTTON, self._on_text_button)
        self.hsizer.Add(text_button, flag=wx.ALL, border=2)
        code_button = wx.Button(self, label="Code")
        code_button.Bind(wx.EVT_BUTTON, self._on_code_button)
        self.hsizer.Add(code_button, flag=wx.ALL, border=2)
        image_button = wx.Button(self, label="Image")
        image_button.Bind(wx.EVT_BUTTON, self._on_image_button)
        self.hsizer.Add(image_button, flag=wx.ALL, border=2)
        self.vsizer.AddSpacer(PARAGRAPH_SPACE)
        view.SetSizer(self.vsizer)
        return view

    def _on_text_button(self, event):
        self.paragraph.update({
            "type": "text",
            "fragments": [{"type": "text", "text": "Enter text here..."}],
        })

    def _on_code_button(self, event):
        self.paragraph.update({
            "type": "code",
            "path": [],
            "text": "Enter code here...",
        })

    def _on_image_button(self, event):
        self.paragraph.update({
            "type": "image",
            "fragments": [{"type": "text", "text": "Enter text here..."}],
        })
class ParagraphContextMenu(wx.Menu):

    def AppendItem(self, text, fn):
        self.Bind(
            wx.EVT_MENU,
            lambda event: fn(),
            self.Append(wx.NewId(), text)
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

    def OnRightClick(self):
        pass

    def OnDoubleClick(self):
        pass

    def OnMove(self, position):
        pass

    def _on_left_down(self, event):
        self.down_pos = event.Position

    def _on_motion(self, event):
        if self.down_pos is None:
            self.OnMove(event.Position)
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
        self.OnDoubleClick()

    def _on_right_up(self, event):
        self.OnRightClick()
class Fragment(object):

    def __init__(self, text, token=Token.RLiterate, **extra):
        self.text = text
        self.token = token
        self.extra = extra

    def word_split(self):
        fragments = []
        text = self.text
        while text:
            match = re.match(r".+?(\s+|$)", text, flags=re.DOTALL)
            fragments.append(Fragment(text=match.group(0), token=self.token, **self.extra))
            text = text[match.end(0):]
        return fragments
class Document(Observable):

    @classmethod
    def from_file(cls, path):
        return cls(path)

    def __init__(self, path):
        Observable.__init__(self)
        self._load(path)
        self.listen(lambda event: write_json_to_file(path, self._state["root_page"]))

    def _load(self, path):
        if os.path.exists(path):
            root_page = load_json_from_file(path)
        else:
            root_page = self._empty_page()
        self._state = {
            "root_page": root_page,
            "pages": {},
            "parent_pages": {},
            "paragraphs": {},
        }
        self._new_state = None
        self._cache_page(root_page)
        for paragraph in self._state["paragraphs"].values():
            if paragraph["type"] in ["text", "quote", "image"] and "text" in paragraph:
                paragraph["fragments"] = LegacyInlineTextParser().parse(paragraph["text"])
                del paragraph["text"]
            elif paragraph["type"] in ["list"] and "text" in paragraph:
                paragraph["child_type"], paragraph["children"] = LegacyListParser(paragraph["text"]).parse_items()
                del paragraph["text"]

    def _cache_page(self, page, parent_page=None):
        self._state["pages"][page["id"]] = page
        self._state["parent_pages"][page["id"]] = parent_page
        for paragraph in page["paragraphs"]:
            self._state["paragraphs"][paragraph["id"]] = paragraph
        for child in page["children"]:
            self._cache_page(child, page)
    @contextlib.contextmanager
    def new_state(self):
        with self.notify():
            if self._new_state is None:
                self._new_state = copy.deepcopy(self._state)
                yield self._new_state
                self._state = self._new_state
                self._new_state = None
            else:
                yield self._new_state
    def add_page(self, title="New page", parent_id=None):
        with self.new_state() as state:
            page = self._empty_page()
            parent_page = state["pages"][parent_id]
            parent_page["children"].append(page)
            state["pages"][page["id"]] = page
            state["parent_pages"][page["id"]] = parent_page

    def _empty_page(self):
        return {
            "id": genid(),
            "title": "New page...",
            "children": [],
            "paragraphs": [],
        }
    def add_paragraph(self, page_id, before_id=None):
        with self.new_state() as state:
            paragraph = {
                "id": genid(),
                "type": "factory",
            }
            state["pages"][page_id]["paragraphs"].append(paragraph)
            state["paragraphs"][paragraph["id"]] = paragraph

    def move_paragraph(self, source_page, source_paragraph, target_page, before_paragraph):
        with self.new_state() as state:
            if (source_page == target_page and
                source_paragraph == before_paragraph):
                return
            paragraph = self.delete_paragraph(source_page, source_paragraph)
            self._add_paragraph(state, target_page, paragraph, before_id=before_paragraph)

    def _add_paragraph(self, state, page_id, paragraph, before_id):
        paragraphs = state["pages"][page_id]["paragraphs"]
        if before_id is None:
            paragraphs.append(paragraph)
        else:
            paragraphs.insert(index_with_id(paragraphs, before_id), paragraph)
        state["paragraphs"][paragraph["id"]] = paragraph

    def delete_paragraph(self, page_id, paragraph_id):
        with self.new_state() as state:
            paragraphs = state["pages"][page_id]["paragraphs"]
            paragraphs.pop(index_with_id(paragraphs, paragraph_id))
            return state["paragraphs"].pop(paragraph_id)
    def get_page(self, page_id=None):
        if page_id is None:
            page_id = self._state["root_page"]["id"]
        page_dict = self._state["pages"].get(page_id, None)
        if page_dict is None:
            return None
        return DictPage(self, page_dict)
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
class DictPage(object):

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
        with self._document.new_state() as state:
            state["pages"][self.id]["title"] = title

    @property
    def paragraphs(self):
        return [
            DictParagraph.create(self._document, paragraph_dict)
            for paragraph_dict
            in self._page_dict["paragraphs"]
        ]

    @property
    def children(self):
        return [
            DictPage(self._document, child_dict)
            for child_dict
            in self._page_dict["children"]
        ]

    def delete(self):
        with self._document.new_state() as state:
            page = state["pages"][self.id]
            parent_page = state["parent_pages"][self.id]
            index = index_with_id(parent_page["children"], self.id)
            parent_page["children"].pop(index)
            state["pages"].pop(self.id)
            state["parent_pages"].pop(self.id)
            for child in reversed(page["children"]):
                parent_page["children"].insert(index, child)
                state["parent_pages"][child["id"]] = parent_page

    def move(self, parent_page_id, before_page_id):
        with self._document.new_state() as state:
            if self.id == before_page_id:
                return
            parent = state["pages"][parent_page_id]
            while parent is not None:
                if parent["id"] == self.id:
                    return
                parent = state["parent_pages"][parent["id"]]
            parent = state["parent_pages"][self.id]
            page = parent["children"].pop(index_with_id(parent["children"], self.id))
            new_parent = state["pages"][parent_page_id]
            state["parent_pages"][self.id] = new_parent
            if before_page_id is None:
                new_parent["children"].append(page)
            else:
                new_parent["children"].insert(
                    index_with_id(new_parent["children"], before_page_id),
                    page
                )
class DictParagraph(object):

    @staticmethod
    def create(document, paragraph_dict):
        return {
            "text": DictTextParagraph,
            "quote": DictQuoteParagraph,
            "list": DictListParagraph,
            "code": DictCodeParagraph,
            "image": DictImageParagraph,
        }.get(paragraph_dict["type"], DictParagraph)(document, paragraph_dict)

    def __init__(self, document, paragraph_dict):
        self._document = document
        self._paragraph_dict = paragraph_dict

    @property
    def id(self):
        return self._paragraph_dict["id"]

    @property
    def type(self):
        return self._paragraph_dict["type"]

    def update(self, data):
        with self._document.new_state() as state:
            state["paragraphs"][self.id].update(data)
class DictTextParagraph(DictParagraph):

    @property
    def filename(self):
        return "paragraph.txt"

    @property
    def fragments(self):
        return [
            DictTextFragment.create(self._document, fragment)
            for fragment
            in self._paragraph_dict["fragments"]
        ]

    @property
    def formatted_text(self):
        return [
            fragment.formatted_text
            for fragment
            in self.fragments
        ]
class DictQuoteParagraph(DictTextParagraph):
    pass
class DictListParagraph(DictParagraph):

    @property
    def child_type(self):
        return self._paragraph_dict["child_type"]

    @property
    def children(self):
        return [ListItem(self._document, x) for x in self._paragraph_dict["children"]]


class ListItem(object):

    def __init__(self, document, item_dict):
        self._document = document
        self._item_dict = item_dict

    @property
    def fragments(self):
        return [
            DictTextFragment.create(self._document, fragment)
            for fragment
            in self._item_dict["fragments"]
        ]

    @property
    def child_type(self):
        return self._item_dict["child_type"]

    @property
    def children(self):
        return [ListItem(self._document, x) for x in self._item_dict["children"]]

    @property
    def formatted_text(self):
        return [x.formatted_text for x in self.fragments]
class DictCodeParagraph(DictParagraph):

    @property
    def text(self):
        return self._paragraph_dict["text"]

    @property
    def formatted_text(self):
        try:
            lexer = self._get_lexer()
        except:
            lexer = pygments.lexers.TextLexer(stripnl=False)
        return self._tokens_to_fragments(lexer.get_tokens(self.text))

    @property
    def has_path(self):
        return len("".join(self.path)) > 0

    @property
    def path(self):
        return tuple(self._paragraph_dict["path"])

    @property
    def filename(self):
        last_part = ""
        for part in self.path:
            if part.startswith("<<"):
                break
            last_part = part
        return last_part

    @property
    def language(self):
        try:
            return "".join(self._get_lexer().aliases[:1])
        except:
            return ""

    def _get_lexer(self):
        return pygments.lexers.get_lexer_for_filename(
            self.filename,
            stripnl=False
        )

    def _tokens_to_fragments(self, tokens):
        fragments = []
        for token, text in tokens:
            fragments.append(Fragment(text, token=token))
        return fragments
class DictImageParagraph(DictParagraph):

    @property
    def fragments(self):
        return [
            DictTextFragment.create(self._document, fragment)
            for fragment
            in self._paragraph_dict["fragments"]
        ]

    @property
    def formatted_text(self):
        return [
            fragment.formatted_text
            for fragment
            in self.fragments
        ]

    @property
    def image_base64(self):
        return self._paragraph_dict.get("image_base64", None)
class DictTextFragment(object):

    @staticmethod
    def create(document, text_fragment_dict):
        return {
            "strong": DictStrongTextFragment,
            "emphasis": DictEmphasisTextFragment,
            "code": DictCodeTextFragment,
            "reference": DictReferenceTextFragment,
            "link": DictLinkTextFragment,
        }.get(text_fragment_dict["type"], DictTextFragment)(document, text_fragment_dict)

    def __init__(self, document, text_fragment_dict):
        self._document = document
        self._text_fragment_dict = text_fragment_dict

    @property
    def type(self):
        return self._text_fragment_dict["type"]

    @property
    def text(self):
        return self._text_fragment_dict["text"]

    @property
    def formatted_text(self):
        return Fragment(self.text)
class DictStrongTextFragment(DictTextFragment):

    @property
    def formatted_text(self):
        return Fragment(self.text, token=Token.RLiterate.Strong)
class DictEmphasisTextFragment(DictTextFragment):

    @property
    def formatted_text(self):
        return Fragment(self.text, token=Token.RLiterate.Emphasis)
class DictCodeTextFragment(DictTextFragment):

    @property
    def formatted_text(self):
        return Fragment(self.text, token=Token.RLiterate.Code)
class DictReferenceTextFragment(DictTextFragment):

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
    def formatted_text(self):
        return Fragment(self.title, token=Token.RLiterate.Reference, page_id=self.page_id)
class DictLinkTextFragment(DictTextFragment):

    @property
    def url(self):
        return self._text_fragment_dict["url"]

    @property
    def title(self):
        if self.text:
            return self.text
        return self.url

    @property
    def formatted_text(self):
        return Fragment(self.title, token=Token.RLiterate.Link, url=self.url)
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
            if column_index is None:
                column_index = len(self._workspace_columns)
            self._workspace_columns[column_index:] = [page_ids[:]]

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
        Token:                     Style(color=base00),
        Token.Keyword:             Style(color=green),
        Token.Keyword.Constant:    Style(color=cyan),
        Token.Keyword.Declaration: Style(color=blue),
        Token.Keyword.Namespace:   Style(color=orange),
        Token.Name.Builtin:        Style(color=red),
        Token.Name.Builtin.Pseudo: Style(color=blue),
        Token.Name.Class:          Style(color=blue),
        Token.Name.Decorator:      Style(color=blue),
        Token.Name.Entity:         Style(color=violet),
        Token.Name.Exception:      Style(color=yellow),
        Token.Name.Function:       Style(color=blue),
        Token.String:              Style(color=cyan),
        Token.Number:              Style(color=cyan),
        Token.Operator.Word:       Style(color=green),
        Token.Comment:             Style(color=base1),
        Token.RLiterate:           Style(color=text),
        Token.RLiterate.Emphasis:  Style(color=text, italic=True),
        Token.RLiterate.Strong:    Style(color=text, bold=True),
        Token.RLiterate.Code:      Style(color=text, monospace=True),
        Token.RLiterate.Link:      Style(color=blue, underlined=True),
        Token.RLiterate.Reference: Style(color=blue, italic=True),
    }
class Project(Observable):

    def __init__(self, filepath):
        Observable.__init__(self)
        self.theme = SolarizedTheme()
        self.document = Document.from_file(filepath)
        self.document.listen(self.notify_forwarder("document"))
        self.layout = Layout(".{}.layout".format(filepath))
        self.layout.listen(self.notify_forwarder("layout"))
        FileGenerator().set_document(self.document)

    def get_page(self, *args, **kwargs):
        return self.document.get_page(*args, **kwargs)

    def add_page(self, *args, **kwargs):
        return self.document.add_page(*args, **kwargs)

    def add_paragraph(self, *args, **kwargs):
        return self.document.add_paragraph(*args, **kwargs)

    def move_paragraph(self, *args, **kwargs):
        return self.document.move_paragraph(*args, **kwargs)

    def delete_paragraph(self, *args, **kwargs):
        return self.document.delete_paragraph(*args, **kwargs)
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
        return self.layout.open_pages(*args, **kwargs)

    def get_hoisted_page(self, *args, **kwargs):
        return self.layout.get_hoisted_page(*args, **kwargs)

    def set_hoisted_page(self, *args, **kwargs):
        return self.layout.set_hoisted_page(*args, **kwargs)
    def get_style(self, *args, **kwargs):
        return self.theme.get_style(*args, **kwargs)
class FileGenerator(object):

    def __init__(self):
        self.listener = Listener(lambda event: self._generate())

    def set_document(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def _generate(self):
        self._parts = defaultdict(list)
        self._collect_parts(self.document.get_page())
        self._generate_files()

    def _collect_parts(self, page):
        for paragraph in page.paragraphs:
            if paragraph.type == "code":
                for line in paragraph.text.splitlines():
                    self._parts[paragraph.path].append(line)
        for child in page.children:
            self._collect_parts(child)

    def _generate_files(self):
        for key in self._parts.keys():
            filepath = self._get_filepath(key)
            if filepath:
                with open(filepath, "w") as f:
                    self._render(f, key)

    def _render(self, f, key, prefix=""):
        for line in self._parts[key]:
            match = re.match(r"^(\s*)(<<.*>>)\s*$", line)
            if match:
                self._render(f, key + (match.group(2),), prefix=prefix+match.group(1))
            else:
                if len(line) > 0:
                    f.write(prefix)
                    f.write(line)
                f.write("\n")

    def _get_filepath(self, key):
        if len(key) == 0:
            return None
        for part in key:
            if part.startswith("<<") and part.endswith(">>"):
                return None
        return os.path.join(*key)
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
            self.fragments(text.formatted_text)

    def paragraph_quote(self, text):
        with self.tag("blockquote"):
            self.fragments(text.formatted_text)

    def paragraph_list(self, paragraph):
        self.list(paragraph)

    def list(self, a_list):
        if a_list.children:
            with self.tag({"ordered": "ol"}.get(a_list.child_type, "ul")):
                for item in a_list.children:
                    with self.tag("li"):
                        self.fragments(item.formatted_text)
                        self.list(item)

    def fragments(self, fragments):
        for fragment in fragments:
            {
                Token.RLiterate.Emphasis: self.fragment_emphasis,
                Token.RLiterate.Strong: self.fragment_strong,
                Token.RLiterate.Code: self.fragment_code,
                Token.RLiterate.Link: self.fragment_link,
                Token.RLiterate.Reference: self.fragment_reference,
            }.get(fragment.token, self.fragment_default)(fragment)

    def fragment_emphasis(self, fragment):
        with self.tag("em", newlines=False):
            self.escaped(fragment.text)

    def fragment_strong(self, fragment):
        with self.tag("strong", newlines=False):
            self.escaped(fragment.text)

    def fragment_code(self, fragment):
        with self.tag("code", newlines=False):
            self.escaped(fragment.text)

    def fragment_link(self, fragment):
        with self.tag("a", args={"href": fragment.extra["url"]}, newlines=False):
            self.escaped(fragment.text)

    def fragment_reference(self, fragment):
        with self.tag("a", args={"href": "#{}".format(fragment.extra["page_id"])}, newlines=False):
            with self.tag("em", newlines=False):
                self.escaped(fragment.text)

    def fragment_default(self, fragment):
        self.escaped(fragment.text)

    def paragraph_code(self, code):
        if code.has_path:
            with self.tag("div", args={"class": "rliterate-code-header"}):
                with self.tag("p", newlines=False):
                    self.escaped(" / ".join(code.path))
        with self.tag("div", args={"class": "rliterate-code-body"}):
            with self.tag("pre", newlines=False):
                for fragment in code.formatted_text:
                    with self.tag(
                        "span",
                        newlines=False,
                        args={"class": STANDARD_TYPES.get(fragment.token, "")}
                    ):
                        self.escaped(fragment.text)

    def paragraph_image(self, paragraph):
        with self.tag("div", args={"class": "rliterate-image"}):
            with self.tag("img", args={
                "src": "data:image/png;base64,{}".format(paragraph.image_base64)
            }):
                pass
        with self.tag("div", args={"class": "rliterate-image-text"}):
            with self.tag("p"):
                self.fragments(paragraph.formatted_text)

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
        self._wrapped_text(fragments_to_text(text.fragments))

    def _render_quote(self, paragraph):
        self._wrapped_text(fragments_to_text(paragraph.fragments), indent=4)

    def _render_list(self, paragraph):
        self._write(list_to_text(paragraph))

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
        self._write(" / ".join(code.path)+":\n\n")
        for line in code.text.splitlines():
            self._write("    "+line+"\n")
        self._write("\n")

    def _render_unknown(self, paragraph):
        self._write("Unknown type = "+paragraph.type+"\n\n")

    def _write(self, text):
        self.parts.append(text)
class Listener(object):

    def __init__(self, fn, *events):
        self.fn = fn
        self.events = events
        self.observable = None

    def set_observable(self, observable):
        if self.observable is not None:
            self.observable.unlisten(self.fn, *self.events)
        self.observable = observable
        self.observable.listen(self.fn, *self.events)
        self.fn("")
def set_clipboard_text(text):
    if wx.TheClipboard.Open():
        try:
            wx.TheClipboard.SetData(wx.TextDataObject(text.encode("utf-8")))
        finally:
            wx.TheClipboard.Close()
def post_fragment_click(widget, fragment):
    wx.PostEvent(widget, FragmentClick(0, widget=widget, fragment=fragment))
def post_hovered_fragment_changed(widget, fragment):
    wx.PostEvent(widget, HoveredFragmentChanged(0, widget=widget, fragment=fragment))
def fragments_to_text(fragments):
    formatters = {
        "emphasis": lambda x: "*{}*".format(x.text),
        "code": lambda x: "`{}`".format(x.text),
        "strong": lambda x: "**{}**".format(x.text),
        "reference": lambda x: "[[{}{}]]".format(x.page_id, ":{}".format(x.text) if x.text else ""),
        "link": lambda x: "[{}]({})".format(x.text, x.url),
    }
    return "".join([
        formatters.get(fragment.type, lambda x: x.text)(fragment)
        for fragment
        in fragments
    ])


def text_to_fragments(text):
    return LegacyInlineTextParser().parse(text)
def list_to_text(paragraph):
    def list_item_to_text(child_type, item, indent=0, index=0):
        text = "    "*indent
        if child_type == "ordered":
            text += "{}. ".format(index+1)
        else:
            text += "* "
        text += fragments_to_text(item.fragments)
        text += "\n"
        for index, child in enumerate(item.children):
            text += list_item_to_text(item.child_type, child, index=index, indent=indent+1)
        return text
    res = ""
    for index, child in enumerate(paragraph.children):
        res += list_item_to_text(paragraph.child_type, child, index=index)
    return res


def text_to_list(text):
    return LegacyListParser(text).parse_items()

def insert_between(separator, items):
    result = []
    for i, item in enumerate(items):
        if i > 0:
            result.append(separator)
        result.append(item)
    return result
def base64_to_bitmap(data):
    try:
        image = fit_image(wx.ImageFromStream(
            StringIO.StringIO(base64.b64decode(data)),
            wx.BITMAP_TYPE_ANY
        ), PAGE_BODY_WIDTH)
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
def post_edit_start(control):
    wx.PostEvent(control, EditStart(0))
@contextlib.contextmanager
def flicker_free_drawing(widget):
    widget.Freeze()
    yield
    widget.Thaw()
def ensure_key(a_dict, key, default):
    if key not in a_dict:
        a_dict[key] = default
    return a_dict[key]
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
def genid():
    return uuid.uuid4().hex


def create_font(monospace=False, size=10, bold=False):
    return wx.Font(
        size,
        wx.FONTFAMILY_TELETYPE if monospace else wx.FONTFAMILY_DEFAULT,
        wx.FONTSTYLE_NORMAL,
        wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL,
        False
    )


def find_first(items, action):
    for item in items:
        result = action(item)
        if result is not None:
            return result
    return None


def pairs(items):
    return zip(items, items[1:]+[None])


def min_or_none(items, key):
    if not items:
        return None
    return min(items, key=key)


def index_with_id(items, item_id):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            return index
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


if __name__ == "__main__":
    if sys.argv[2:] == ["--html"]:
        sys.stdout.write(HTMLBuilder(Document.from_file(sys.argv[1])).build())
    elif sys.argv[2:] == ["--diff"]:
        sys.stdout.write(DiffBuilder(Document.from_file(sys.argv[1])).build())
    else:
        app = wx.App()
        main_frame = MainFrame(filepath=sys.argv[1])
        main_frame.Show()
        app.MainLoop()
