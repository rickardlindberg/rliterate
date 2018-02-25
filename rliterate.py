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

import pygments.lexers
from pygments.token import Token, STANDARD_TYPES
import wx
import wx.lib.newevent


PAGE_BODY_WIDTH = 600
PAGE_PADDING = 13
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 15
CONTAINER_BORDER = PARAGRAPH_SPACE


ParagraphEditStart, EVT_PARAGRAPH_EDIT_START = wx.lib.newevent.NewCommandEvent()
ParagraphEditEnd, EVT_PARAGRAPH_EDIT_END = wx.lib.newevent.NewCommandEvent()
class ParagraphBase(object):

    def __init__(self, project, page_id, paragraph):
        self.project = project
        self.page_id = page_id
        self.paragraph = paragraph

    def DoDragDrop(self):
        data = RliterateDataObject("paragraph", {
            "page_id": self.page_id,
            "paragraph_id": self.paragraph.id,
        })
        drag_source = wx.DropSource(self)
        drag_source.SetData(data)
        result = drag_source.DoDragDrop(wx.Drag_DefaultMove)

    def ShowContextMenu(self):
        menu = ParagraphContextMenu(
            self.project, self.page_id, self.paragraph
        )
        self.PopupMenu(menu)
        menu.Destroy()
class Editable(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.view = self.CreateView()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.view, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)
        self.view.Bind(wx.EVT_LEFT_DCLICK, self.OnParagraphEditStart)
        self.view.Bind(EVT_PARAGRAPH_EDIT_START, self.OnParagraphEditStart)

    def OnParagraphEditStart(self, event):
        self.edit = self.CreateEdit()
        self.edit.SetFocus()
        self.edit.Bind(wx.EVT_CHAR, self.OnChar)
        self.edit.Bind(EVT_PARAGRAPH_EDIT_END, self.OnParagraphEditEnd)
        self.sizer.Add(self.edit, flag=wx.EXPAND, proportion=1)
        self.sizer.Hide(self.view)
        self.GetTopLevelParent().Layout()

    def OnParagraphEditEnd(self, event):
        self.EndEdit()

    def OnChar(self, event):
        if event.KeyCode == wx.WXK_CONTROL_S:
            self.OnParagraphEditEnd(None)
        elif event.KeyCode == wx.WXK_RETURN and event.ControlDown():
            self.OnParagraphEditEnd(None)
        else:
            event.Skip()
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
class Style(object):

    def __init__(self, color, bold=None, underlined=None):
        self.color = color
        self.color_rgb = tuple([
            int(x, 16)
            for x
            in (color[1:3], color[3:5], color[5:7])
        ])
        self.bold = bold
        self.underlined = underlined

    def get_css(self):
        return "color: {}".format(self.color)

    def apply_to_wx_dc(self, dc, base_font):
        font = base_font
        if self.bold:
            font = font.Bold()
        if self.underlined:
            font = font.Underlined()
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
            "document", "layout.toc"
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
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetBackgroundColour((255, 255, 255))
        self._re_render()

    def _re_render(self):
        self.drop_points = []
        self.sizer.Clear(True)
        self._render_unhoist_button()
        self._render_page_container()
        self.Layout()
    def _render_unhoist_button(self):
        if self.project.get_hoisted_page() is not None:
            button = wx.Button(self, label="unhoist")
            button.Bind(
                wx.EVT_BUTTON,
                lambda event: self.project.set_hoisted_page(None)
            )
            self.sizer.Add(button, flag=wx.EXPAND)
    def _render_page_container(self):
        self.page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_container = CompactScrolledWindow(self)
        self.page_container.SetSizer(self.page_sizer)
        self.sizer.Add(self.page_container, flag=wx.EXPAND, proportion=1)
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
        self.project.move_page(
            page_id=dropped_page["page_id"],
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
        text = wx.StaticText(self)
        text.SetLabelText(self.page.title)
        self.sizer.Add(text, flag=wx.ALL, border=self.BORDER)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        for helper in [MouseEventHelper(self), MouseEventHelper(text)]:
            helper.OnClick = self._on_click
            helper.OnDoubleClick = self._on_double_click
            helper.OnRightClick = self._on_right_click
            helper.OnDrag = self._on_drag
    def _on_click(self):
        self.project.open_pages([self.page.id], column_index=0)

    def _on_double_click(self):
        page_ids = [self.page.id]
        for child in self.project.get_page(self.page.id).children:
            page_ids.append(child.id)
        self.project.open_pages(page_ids, column_index=0)

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
            lambda event: self.project.delete_page(self.page.id),
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
        self.SetBackgroundColour((200, 200, 200))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)
        self.columns = []
        self._re_render()

    def _re_render(self):
        self._ensure_num_columns(len(self.project.columns))
        for index, page_ids in enumerate(self.project.columns):
            self.columns[index].SetPages(self.project, page_ids)
        self.Parent.Layout()

    def _ensure_num_columns(self, num):
        while len(self.columns) > num:
            self.columns.pop(-1).Destroy()
        while len(self.columns) < num:
            self.columns.append(self._add_column())

    def _add_column(self):
        column = Column(self)
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

    def __init__(self, parent):
        CompactScrolledWindow.__init__(
            self,
            parent,
            style=wx.VSCROLL,
            size=(PAGE_BODY_WIDTH+2*CONTAINER_BORDER+PAGE_PADDING, -1)
        )
        self._page_ids = []
        self._setup_layout()

    def _setup_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def SetPages(self, project, page_ids):
        self.containers = []
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PAGE_PADDING)
        for page_id in page_ids:
            container = PageContainer(self, project, page_id)
            self.sizer.Add(
                container,
                flag=wx.RIGHT|wx.BOTTOM|wx.EXPAND,
                border=PAGE_PADDING
            )
            self.containers.append(container)
        if page_ids != self._page_ids:
            self.Scroll(0, 0)
            self._page_ids = page_ids

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
                "text": Paragraph,
                "code": Code,
                "factory": Factory,
            }[paragraph.type](self, self.project, self.page_id, paragraph))
        self.drop_points.append(PageDropPoint(
            divider=divider,
            page_id=self.page_id,
            next_paragraph_id=None
        ))
        self._render_add_button()

    def _render_paragraph(self, paragraph):
        self.sizer.Add(
            paragraph,
            flag=wx.EXPAND,
            border=PARAGRAPH_SPACE
        )
        divider = Divider(self, padding=(PARAGRAPH_SPACE-3)/2, height=3)
        self.sizer.Add(
            divider,
            flag=wx.EXPAND,
            border=PARAGRAPH_SPACE
        )
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
        return view

    def CreateEdit(self):
        edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.page.title)
        edit.Bind(wx.EVT_TEXT_ENTER, lambda _: self.EndEdit())
        return edit

    def EndEdit(self):
        self.project.edit_page(self.page.id, {"title": self.edit.Value})
class Paragraph(ParagraphBase, Editable):

    def __init__(self, parent, project, page_id, paragraph):
        ParagraphBase.__init__(self, project, page_id, paragraph)
        Editable.__init__(self, parent)

    def CreateView(self):
        view = RichTextDisplay(
            self,
            self.project,
            self.paragraph.formatted_text,
            line_height=1.2,
            max_width=PAGE_BODY_WIDTH
        )
        MouseEventHelper.bind(
            [view],
            drag=self.DoDragDrop,
            right_click=self.ShowContextMenu,
            move=self._change_cursor,
            click=self._follow_link
        )
        self.default_cursor = view.GetCursor()
        self.link_fragment = None
        return view

    def _change_cursor(self, position):
        fragment = self.view.GetFragment(position)
        if fragment is not None and fragment.token == Token.RLiterate.Link:
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            self.link_fragment = fragment
        else:
            self.SetCursor(self.default_cursor)
            self.link_fragment = None

    def _follow_link(self):
        if self.link_fragment is not None:
            webbrowser.open(self.link_fragment.extra["url"])

    def CreateEdit(self):
        edit = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE,
            value=self.paragraph.text
        )
        # Error is printed if height is too small:
        # Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size >= 0' failed in GtkScrollbar
        # Solution: Make it at least 50 heigh.
        edit.MinSize = (-1, max(50, self.view.Size[1]))
        return edit

    def EndEdit(self):
        self.project.edit_paragraph(self.paragraph.id, {"text": self.edit.Value})
class Code(ParagraphBase, Editable):

    def __init__(self, parent, project, page_id, paragraph):
        ParagraphBase.__init__(self, project, page_id, paragraph)
        Editable.__init__(self, parent)

    def CreateView(self):
        return CodeView(self, self.project, self.paragraph)

    def CreateEdit(self):
        return CodeEditor(self, self.view, self.paragraph)

    def EndEdit(self):
        self.project.edit_paragraph(self.paragraph.id, {
            "path": self.edit.path.Value.split(" / "),
            "text": self.edit.text.Value,
        })
class CodeView(wx.Panel):

    BORDER = 0
    PADDING = 5

    def __init__(self, parent, project, code_paragraph):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.Font = create_font(monospace=True)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(
            self._create_path(code_paragraph),
            flag=wx.ALL|wx.EXPAND, border=self.BORDER
        )
        self.vsizer.Add(
            self._create_code(code_paragraph),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetSizer(self.vsizer)
        self.SetBackgroundColour((243, 236, 219))

    def _create_path(self, code_paragraph):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((248, 241, 223))
        text = RichTextDisplay(
            panel,
            self.project,
            insert_between(
                Fragment(" / "),
                [Fragment(x, token=pygments.token.Token.RLiterate.Strong) for x in code_paragraph.path]
            ),
            max_width=PAGE_BODY_WIDTH-2*self.PADDING
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(text, flag=wx.ALL|wx.EXPAND, border=self.PADDING)
        panel.SetSizer(sizer)
        MouseEventHelper.bind(
            [panel, text],
            double_click=self._post_paragraph_edit_start,
            drag=self.Parent.DoDragDrop,
            right_click=self.Parent.ShowContextMenu
        )
        return panel

    def _create_code(self, code_paragraph):
        panel = wx.Panel(self)
        panel.SetBackgroundColour((253, 246, 227))
        body = RichTextDisplay(
            panel,
            self.project,
            code_paragraph.formatted_text,
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
        wx.PostEvent(self, ParagraphEditStart(0))
class CodeEditor(wx.Panel):

    BORDER = 1
    PADDING = 3

    def __init__(self, parent, view, code_paragraph):
        wx.Panel.__init__(self, parent)
        self.Font = create_font(monospace=True)
        self.view = view
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(
            self._create_path(code_paragraph),
            flag=wx.ALL|wx.EXPAND, border=self.BORDER
        )
        self.vsizer.Add(
            self._create_code(code_paragraph),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.vsizer.Add(
            self._create_save(),
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=self.BORDER
        )
        self.SetSizer(self.vsizer)

    def _create_path(self, code_paragraph):
        self.path = wx.TextCtrl(
            self,
            value=" / ".join(code_paragraph.path)
        )
        return self.path

    def _create_code(self, code_paragraph):
        self.text = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE,
            value=code_paragraph.text
        )
        # Error is printed if height is too small:
        # Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size >= 0' failed in GtkScrollbar
        # Solution: Make it at least 50 heigh.
        self.text.MinSize = (-1, max(50, self.view.Size[1]))
        return self.text

    def _create_save(self):
        button = wx.Button(
            self,
            label="Save"
        )
        self.Bind(wx.EVT_BUTTON, lambda event: self._post_paragraph_edit_end())
        return button

    def _post_paragraph_edit_end(self):
        wx.PostEvent(self, ParagraphEditEnd(0))
class Factory(ParagraphBase, wx.Panel):

    def __init__(self, parent, project, page_id, paragraph):
        ParagraphBase.__init__(self, project, page_id, paragraph)
        wx.Panel.__init__(self, parent)
        MouseEventHelper.bind(
            [self],
            drag=self.DoDragDrop,
            right_click=self.ShowContextMenu
        )
        self.SetBackgroundColour((240, 240, 240))
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer.Add(
            wx.StaticText(self, label="Factory"),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        self.vsizer.Add(
            self.hsizer,
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        text_button = wx.Button(self, label="Text")
        text_button.Bind(wx.EVT_BUTTON, self.OnTextButton)
        self.hsizer.Add(text_button, flag=wx.ALL, border=2)
        code_button = wx.Button(self, label="Code")
        code_button.Bind(wx.EVT_BUTTON, self.OnCodeButton)
        self.hsizer.Add(code_button, flag=wx.ALL, border=2)
        self.vsizer.AddSpacer(PARAGRAPH_SPACE)
        self.SetSizer(self.vsizer)

    def OnTextButton(self, event):
        self.project.edit_paragraph(self.paragraph.id, {"type": "text", "text": "Enter text here..."})

    def OnCodeButton(self, event):
        self.project.edit_paragraph(self.paragraph.id, {"type": "code", "path": [], "text": "Enter code here..."})
class ParagraphContextMenu(wx.Menu):

    def __init__(self, project, page_id, paragraph):
        wx.Menu.__init__(self)
        self.project = project
        self.page_id = page_id
        self.paragraph = paragraph
        self._create_menu()

    def _create_menu(self):
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.delete_paragraph(
                page_id=self.page_id,
                paragraph_id=self.paragraph.id
            ),
            self.Append(wx.NewId(), "Delete")
        )
        self.Bind(
            wx.EVT_MENU,
            lambda event: self.project.edit_paragraph(
                self.paragraph.id,
                {"text": edit_in_gvim(self.paragraph.text, self.paragraph.filename)}
            ),
            self.Append(wx.NewId(), "Edit in gvim")
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
        self.line.Show()
        self.hsizer.Clear(False)
        self.hsizer.Add((left_space, 1))
        self.hsizer.Add(self.line, flag=wx.EXPAND, proportion=1)
        self.Layout()

    def Hide(self):
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
        for fragment in self._newline_fragments():
            if fragment is None:
                x = 0
                y += int(round(dc.GetTextExtent("M")[1]*self.line_height))
                continue
            style = self.project.get_style(fragment.token)
            style.apply_to_wx_dc(dc, self.GetFont())
            w, h = dc.GetTextExtent(fragment.text)
            if x > 0 and x+w > self.max_width:
                x = 0
                y += int(round(dc.GetTextExtent("M")[1]*self.line_height))
            self.draw_fragments.append((fragment, style, wx.Rect(x, y, w, h)))
            max_x = max(max_x, x+w)
            max_y = max(max_y, y+h)
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
class Project(Observable):

    def __init__(self, filepath):
        Observable.__init__(self)
        self.theme = SolarizedTheme()
        self.document = Document.from_file(filepath)
        self.document.listen(self.notify_forwarder("document"))
        self.layout = Layout(".{}.layout".format(filepath))
        self.layout.listen(self.notify_forwarder("layout"))
        FileGenerator().set_document(self.document)

    def toggle_collapsed(self, *args, **kwargs):
        return self.layout.toggle_collapsed(*args, **kwargs)

    def is_collapsed(self, *args, **kwargs):
        return self.layout.is_collapsed(*args, **kwargs)

    def get_scratch_pages(self, *args, **kwargs):
        return self.layout.get_scratch_pages(*args, **kwargs)

    def set_scratch_pages(self, *args, **kwargs):
        return self.layout.set_scratch_pages(*args, **kwargs)

    @property
    def columns(self):
        return self.layout.columns

    def open_pages(self, *args, **kwargs):
        return self.layout.open_pages(*args, **kwargs)

    def get_hoisted_page(self, *args, **kwargs):
        return self.layout.get_hoisted_page(*args, **kwargs)

    def set_hoisted_page(self, *args, **kwargs):
        return self.layout.set_hoisted_page(*args, **kwargs)
    def get_page(self, *args, **kwargs):
        return self.document.get_page(*args, **kwargs)

    def add_page(self, *args, **kwargs):
        return self.document.add_page(*args, **kwargs)

    def delete_page(self, *args, **kwargs):
        return self.document.delete_page(*args, **kwargs)

    def move_page(self, *args, **kwargs):
        return self.document.move_page(*args, **kwargs)

    def edit_page(self, *args, **kwargs):
        return self.document.edit_page(*args, **kwargs)

    def add_paragraph(self, *args, **kwargs):
        return self.document.add_paragraph(*args, **kwargs)

    def move_paragraph(self, *args, **kwargs):
        return self.document.move_paragraph(*args, **kwargs)

    def delete_paragraph(self, *args, **kwargs):
        return self.document.delete_paragraph(*args, **kwargs)

    def edit_paragraph(self, *args, **kwargs):
        return self.document.edit_paragraph(*args, **kwargs)
    def get_style(self, *args, **kwargs):
        return self.theme.get_style(*args, **kwargs)
class Document(Observable):

    @classmethod
    def from_file(cls, path):
        return cls(path)

    def __init__(self, path):
        Observable.__init__(self)
        self.path = path
        self._load()
        self._cache()
        self.listen(lambda event: self._save())

    def _cache(self):
        self._pages = {}
        self._parent_pages = {}
        self._paragraphs = {}
        self._cache_page(self.root_page)

    def _cache_page(self, page, parent_page=None):
        self._pages[page["id"]] = page
        self._parent_pages[page["id"]] = parent_page
        for paragraph in page["paragraphs"]:
            self._paragraphs[paragraph["id"]] = paragraph
        for child in page["children"]:
            self._cache_page(child, page)

    def _save(self):
        write_json_to_file(self.path, self.root_page)

    def _load(self):
        self.root_page = load_json_from_file(self.path)

    def get_page(self, page_id=None):
        if page_id is None:
            page_id = self.root_page["id"]
        page_dict = self._pages.get(page_id, None)
        if page_dict is None:
            return None
        return DictPage(page_dict)

    # Page operations

    def add_page(self, title="New page", parent_id=None):
        with self.notify():
            page = {
                "id": genid(),
                "title": "New page...",
                "children": [],
                "paragraphs": [],
            }
            parent_page = self._pages[parent_id]
            parent_page["children"].append(page)
            self._pages[page["id"]] = page
            self._parent_pages[page["id"]] = parent_page

    def delete_page(self, page_id):
        with self.notify():
            page = self._pages[page_id]
            parent_page = self._parent_pages[page_id]
            index = index_with_id(parent_page["children"], page_id)
            parent_page["children"].pop(index)
            self._pages.pop(page_id)
            self._parent_pages.pop(page_id)
            for child in reversed(page["children"]):
                parent_page["children"].insert(index, child)
                self._parent_pages[child["id"]] = parent_page

    def move_page(self, page_id, parent_page_id, before_page_id):
        with self.notify():
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

    def edit_page(self, page_id, data):
        with self.notify():
            self._pages[page_id].update(data)

    # Paragraph operations

    def add_paragraph(self, page_id, before_id=None):
        with self.notify():
            paragraph = {
                "id": genid(),
                "type": "factory",
                "text":
                "factory",
            }
            self._pages[page_id]["paragraphs"].append(paragraph)
            self._paragraphs[paragraph["id"]] = paragraph

    def move_paragraph(self, source_page, source_paragraph, target_page, before_paragraph):
        with self.notify():
            if (source_page == target_page and
                source_paragraph == before_paragraph):
                return
            paragraph = self.delete_paragraph(source_page, source_paragraph)
            self._add_paragraph(target_page, paragraph, before_id=before_paragraph)

    def _add_paragraph(self, page_id, paragraph, before_id):
        paragraphs = self._pages[page_id]["paragraphs"]
        if before_id is None:
            paragraphs.append(paragraph)
        else:
            paragraphs.insert(index_with_id(paragraphs, before_id), paragraph)
        self._paragraphs[paragraph["id"]] = paragraph

    def delete_paragraph(self, page_id, paragraph_id):
        with self.notify():
            paragraphs = self._pages[page_id]["paragraphs"]
            paragraphs.pop(index_with_id(paragraphs, paragraph_id))
            return self._paragraphs.pop(paragraph_id)

    def edit_paragraph(self, paragraph_id, data):
        with self.notify():
            self._paragraphs[paragraph_id].update(data)
class DictPage(object):

    def __init__(self, page_dict):
        self._page_dict = page_dict

    @property
    def id(self):
        return self._page_dict["id"]

    @property
    def title(self):
        return self._page_dict["title"]

    @property
    def paragraphs(self):
        return [
            DictParagraph.create(paragraph_dict)
            for paragraph_dict
            in self._page_dict["paragraphs"]
        ]

    @property
    def children(self):
        return [
            DictPage(child_dict)
            for child_dict
            in self._page_dict["children"]
        ]
class DictParagraph(object):

    @staticmethod
    def create(paragraph_dict):
        return {
            "text": DictTextParagraph,
            "code": DictCodeParagraph,
        }.get(paragraph_dict["type"], DictParagraph)(paragraph_dict)

    def __init__(self, paragraph_dict):
        self._paragraph_dict = paragraph_dict

    @property
    def id(self):
        return self._paragraph_dict["id"]

    @property
    def type(self):
        return self._paragraph_dict["type"]
class DictTextParagraph(DictParagraph):

    @property
    def filename(self):
        return "paragraph.txt"

    @property
    def text(self):
        return self._paragraph_dict["text"]

    @property
    def formatted_text(self):
        fragments = []
        text = self._paragraph_dict["text"]
        partial = ""
        while text:
            result = self._get_special_fragment(text)
            if result is None:
                partial += text[0]
                text = text[1:]
            else:
                match, fragment = result
                if partial:
                    fragments.append(Fragment(partial))
                    partial = ""
                fragments.append(fragment)
                text = text[match.end(0):]
        if partial:
            fragments.append(Fragment(partial))
        return fragments

    PATTERNS = [
        (
            re.compile(r"\*\*(.+?)\*\*", flags=re.DOTALL),
            lambda match: Fragment(
                match.group(1),
                token=Token.RLiterate.Strong
            )
        ),
        (
            re.compile(r"\[(.+?)\]\((.+?)\)", flags=re.DOTALL),
            lambda match: Fragment(
                match.group(1),
                token=Token.RLiterate.Link,
                url=match.group(2)
            )
        ),
    ]

    def _get_special_fragment(self, text):
        for pattern, fn in self.PATTERNS:
            match = pattern.match(text)
            if match:
                return match, fn(match)
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
        self._workspace_scratch = ensure_key(self._workspace, "scratch", [])
        self._workspace_columns = ensure_key(self._workspace, "columns", [])
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
    def get_scratch_pages(self):
        return self._workspace_scratch[:]

    def set_scratch_pages(self, page_ids):
        self.set_pages(page_ids, column_index=0)
    @property
    def columns(self):
        if self._workspace_columns:
            return [column[:] for column in self._workspace_columns]
        else:
            return [self.get_scratch_pages()]

    def open_pages(self, page_ids, column_index=None):
        with self.notify("workspace"):
            if column_index is None:
                column_index = len(self._workspace_columns)
            self._workspace_columns[column_index:] = [page_ids[:]]
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
        Token.RLiterate.Strong:    Style(color=text, bold=True),
        Token.RLiterate.Link:      Style(color=blue, underlined=True),
    }
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
            if filepath is not None:
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
class MarkdownGenerator(object):

    def __init__(self, path):
        self.listener = Listener(lambda event: self._generate())
        self.path = path

    def set_document(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def _generate(self):
        with open(self.path, "w") as f:
            self._render_page(f, self.document.get_page())

    def _render_page(self, f, page, level=1):
        f.write("#"*level+" "+page.title+"\n\n")
        for paragraph in page.paragraphs:
            {
                "text": self._render_text,
                "code": self._render_code,
            }.get(paragraph.type, self._render_unknown)(f, paragraph)
        for child in page.children:
            self._render_page(f, child, level+1)

    def _render_text(self, f, text):
        f.write(text.text+"\n\n")

    def _render_code(self, f, code):
        f.write("`"+" / ".join(code.path)+"`:\n\n")
        f.write("```"+code.language+"\n")
        for line in code.text.splitlines():
            f.write(line+"\n")
        f.write("```"+"\n")
        f.write("\n")

    def _render_unknown(self, f, paragraph):
        f.write("Unknown type = "+paragraph.type+"\n\n")
class HTMLGenerator(object):

    def __init__(self, path):
        self.listener = Listener(lambda event: self._generate())
        self.path = path

    def set_document(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def _generate(self):
        with open(self.path, "w") as f:
            f.write(HTMLBuilder(self.document).build())


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
        if levels_left > 0:
            with self.tag("ul", newlines=False):
                for page in root_page.children:
                    with self.tag("li", newlines=False):
                        with self.tag("a", newlines=False, args={"href": "#{}".format(page.id)}):
                            self.escaped(page.title)
                            self.toc(page, levels_left - 1)

    def page(self, page, level=1):
        with self.tag("h{}".format(level)):
            if level > 1 and level <= self.toc_max_depth+1:
                with self.tag("a", args={"name": page.id}):
                    pass
            self.escaped(page.title)
        for paragraph in page.paragraphs:
            {
                "text": self.paragraph_text,
                "code": self.paragraph_code,
            }.get(paragraph.type, self.paragraph_unknown)(paragraph)
        if level == 1 and self.generate_toc:
            self.toc(page, self.toc_max_depth)
        for child in page.children:
            self.page(child, level+1)

    def paragraph_text(self, text):
        with self.tag("p"):
            for fragment in text.formatted_text:
                {
                    Token.RLiterate.Strong: self.fragment_strong,
                    Token.RLiterate.Link: self.fragment_link,
                }.get(fragment.token, self.fragment_default)(fragment)

    def fragment_strong(self, fragment):
        with self.tag("strong", newlines=False):
            self.escaped(fragment.text)

    def fragment_link(self, fragment):
        with self.tag("a", args={"href": fragment.extra["url"]}, newlines=False):
            self.escaped(fragment.text)

    def fragment_default(self, fragment):
        self.escaped(fragment.text)

    def paragraph_code(self, code):
        with self.tag("p"):
            with self.tag("code", newlines=False):
                self.escaped(" / ".join(code.path))
        with self.tag("div", args={"class": "highlight"}):
            with self.tag("pre", newlines=False):
                for fragment in code.formatted_text:
                    with self.tag(
                        "span",
                        newlines=False,
                        args={"class": STANDARD_TYPES.get(fragment.token, "")}
                    ):
                        self.escaped(fragment.text)

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
class TextDiff(object):

    def __init__(self, path):
        self.listener = Listener(lambda event: self._generate())
        self.path = path

    def set_document(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def _generate(self):
        with open(self.path, "w") as f:
            f.write(DiffBuilder(self.document).build())


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
            self._write("\n\n")
            for paragraph in page.paragraphs:
                {
                    "text": self._render_text,
                    "code": self._render_code,
                }.get(paragraph.type, self._render_unknown)(paragraph)

    def _render_text(self, text):
        self._write(text.text+"\n\n")

    def _render_code(self, code):
        self._write("`"+" / ".join(code.path)+"`:\n\n")
        for line in code.text.splitlines():
            self._write("    "+line+"\n")
        self._write("\n\n")

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
def insert_between(separator, items):
    result = []
    for i, item in enumerate(items):
        if i > 0:
            result.append(separator)
        result.append(item)
    return result
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
