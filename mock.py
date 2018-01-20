import contextlib
import json
import uuid

import wx
import wx.lib.newevent


PAGE_BODY_WIDTH = 500
PAGE_PADDING = 12
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 15


TreeToggle, EVT_TREE_TOGGLE = wx.lib.newevent.NewCommandEvent()
TreeLeftClick, EVT_TREE_LEFT_CLICK = wx.lib.newevent.NewCommandEvent()
TreeDoubleClick, EVT_TREE_DOUBLE_CLICK = wx.lib.newevent.NewCommandEvent()


def genid():
    return uuid.uuid4().hex


class Listener(object):

    def __init__(self, fn):
        self.fn = fn
        self.observable = None

    def set_observable(self, observable):
        if self.observable is not None:
            self.observable.unlisten(self.fn)
        self.observable = observable
        self.observable.listen(self.fn)
        self.fn()


class Document(object):

    @classmethod
    def from_file(cls, path):
        return cls(path)

    def __init__(self, path):
        self.path = path
        self.listeners = []
        self._load()
        self._cache()

    def _cache(self):
        self._pages = {}
        self._paragraphs = {}
        self._cache_page(self.py_obj)

    def _cache_page(self, page):
        self._pages[page["id"]] = page
        for paragraph in page["paragraphs"]:
            self._paragraphs[paragraph["id"]] = paragraph
        for child in page["children"]:
            self._cache_page(child)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.py_obj, f)

    def _load(self):
        with open(self.path, "r") as f:
            self.py_obj = json.load(f)

    # PUB/SUB

    def listen(self, fn):
        self.listeners.append(fn)

    def unlisten(self, fn):
        self.listeners.remove(fn)

    @contextlib.contextmanager
    def notify(self):
        yield
        for fn in self.listeners:
            fn()
        self._save()

    # Queries

    def get_toc(self):
        def page_toc(page):
            return {
                "id": page["id"],
                "title": page["title"],
                "children": [page_toc(child) for child in page["children"]],
            }
        return page_toc(self.py_obj)

    def get_page(self, page_id):
        return self._pages[page_id]

    # Page operations

    def add_page(self, title="New page", parent_id=None):
        with self.notify():
            pass

    def remove_page(self, page_id):
        with self.notify():
            pass

    def move_page(self, page_id, target_spec):
        with self.notify():
            pass

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

    def move_paragraph(self, source_page, source_paragraph, target_page, target_paragraph):
        with self.notify():
            if (source_page == target_page and
                source_paragraph == target_paragraph):
                return
            paragraph = self._remove_paragraph(source_page, source_paragraph)
            self._add_paragraph(target_page, paragraph, before_id=target_paragraph)

    def _remove_paragraph(self, page_id, paragraph_id):
        paragraphs = self._pages[page_id]["paragraphs"]
        paragraphs.pop(self._p_index(paragraphs, paragraph_id))
        return self._paragraphs.pop(paragraph_id)

    def _add_paragraph(self, page_id, paragraph, before_id):
        paragraphs = self._pages[page_id]["paragraphs"]
        if before_id is None:
            paragraphs.append(paragraph)
        else:
            paragraphs.insert(self._p_index(paragraphs, before_id), paragraph)
        self._paragraphs[paragraph["id"]] = paragraph

    def _p_index(self, paragraphs, paragraph_id):
        for index, p in enumerate(paragraphs):
            if p["id"] == paragraph_id:
                return index

    def remove_paragraph(self, page_id, paragraph_id):
        with self.notify():
            pass

    def edit_paragraph(self, paragraph_id, data):
        with self.notify():
            self._paragraphs[paragraph_id].update(data)


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)

        document = Document.from_file("example.rliterate")

        page_workspace = PageWorkspace(self, document)

        toc = TableOfContents(self, page_workspace, document)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(toc, flag=wx.EXPAND, proportion=0)
        sizer.Add(page_workspace, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class TableOfContents(wx.ScrolledWindow):

    def __init__(self, parent, page_workspace, document):
        wx.ScrolledWindow.__init__(self, parent, size=(200, -1))
        self.SetScrollRate(20, 20)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.listener = Listener(lambda: wx.CallAfter(self.Render))
        self.SetDocument(document)
        self.SetBackgroundColour((255, 255, 255))
        self.collapsed = set()
        self.page_workspace = page_workspace
        self.Bind(EVT_TREE_TOGGLE, self.OnTreeToggle)
        self.Bind(EVT_TREE_LEFT_CLICK, self.OnTreeLeftClick)
        self.Bind(EVT_TREE_DOUBLE_CLICK, self.OnTreeDoubleClick)

    def OnTreeToggle(self, event):
        if event.page_id in self.collapsed:
            self.collapsed.remove(event.page_id)
        else:
            self.collapsed.add(event.page_id)
        self.Render()

    def OnTreeLeftClick(self, event):
        self.page_workspace.OpenScratch([event.page_id])

    def OnTreeDoubleClick(self, event):
        page_ids = [event.page_id]
        for child in self.document.get_page(event.page_id)["children"]:
            page_ids.append(child["id"])
        self.page_workspace.OpenScratch(page_ids)

    def SetDocument(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def Render(self):
        self.Freeze()
        self.sizer.Clear(True)
        self.add_page(self.document.get_toc())
        self.Layout()
        self.Thaw()

    def add_page(self, page, indentation=0):
        is_collapsed = page["id"] in self.collapsed
        self.sizer.Add(
            TableOfContentsRow(self, indentation, page, is_collapsed),
            flag=wx.EXPAND
        )
        if not is_collapsed:
            for child in page["children"]:
                self.add_page(child, indentation+1)


class TableOfContentsRow(wx.Panel):

    BORDER = 3

    def __init__(self, parent, indentation, page, is_collapsed):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add((indentation*25, 1))
        if page["children"]:
            button = TableOfContentsButton(self, page["id"], is_collapsed)
            self.sizer.Add(button, flag=wx.EXPAND|wx.LEFT, border=self.BORDER)
        else:
            self.sizer.Add((TableOfContentsButton.SIZE+1+self.BORDER, 1))
        text = wx.StaticText(self, label=page["title"])
        self.sizer.Add(text, flag=wx.ALL, border=self.BORDER)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)
        text.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        text.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)
        self.original_colour = self.Parent.GetBackgroundColour()
        self.page_id = page["id"]

    def OnLeftDown(self, event):
        wx.PostEvent(self, TreeLeftClick(0, page_id=self.page_id))

    def OnLeftDclick(self, event):
        wx.PostEvent(self, TreeDoubleClick(0, page_id=self.page_id))

    def OnEnterWindow(self, event):
        self.SetBackgroundColour((240, 240, 240))

    def OnLeaveWindow(self, event):
        self.SetBackgroundColour(self.original_colour)


class TableOfContentsButton(wx.Panel):

    SIZE = 16

    def __init__(self, parent, page_id, is_collapsed):
        wx.Panel.__init__(self, parent, size=(self.SIZE+1, -1))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.page_id = page_id
        self.is_hovered = False
        self.is_collapsed = is_collapsed
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def OnLeftDown(self, event):
        wx.PostEvent(self, TreeToggle(0, page_id=self.page_id))

    def OnPaint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.BLACK_BRUSH)
        render = wx.RendererNative.Get()
        (w, h) = self.Size
        render.DrawTreeItemButton(
            self,
            dc,
            (0, (h-self.SIZE)/2, self.SIZE, self.SIZE),
            flags=0 if self.is_collapsed else wx.CONTROL_EXPANDED
        )


def find_first(items, action):
    for item in items:
        result = action(item)
        if result is not None:
            return result
    return None


class RliterateDataObject(wx.CustomDataObject):

    def __init__(self, kind, json=None):
        wx.CustomDataObject.__init__(self, "rliterate/{}".format(kind))
        if json is not None:
            self.set_json(json)

    def set_json(self, data):
        self.SetData(json.dumps(data))

    def get_json(self):
        return json.loads(self.GetData())


class PageWorkspaceDropTarget(wx.DropTarget):

    def __init__(self, workspace):
        wx.DropTarget.__init__(self)
        self.workspace = workspace
        self.paragraph = None
        self.data = None
        self.rliterate_data = RliterateDataObject("paragraph")
        self.DataObject = self.rliterate_data

    def OnDragOver(self, x, y, defResult):
        self._clear()
        data = self.workspace.FindParagraph(self.workspace.ClientToScreen((x, y)))
        if data is not None and defResult == wx.DragMove:
            self.data = data
            self.data["window"].Show()
            return wx.DragMove
        return wx.DragNone

    def OnData(self, x, y, defResult):
        self._clear()
        data = self.workspace.FindParagraph(self.workspace.ClientToScreen((x, y)))
        if data is not None:
            self.GetData()
            paragraph = self.rliterate_data.get_json()
            self.workspace.document.move_paragraph(
                source_page=paragraph["page_id"],
                source_paragraph=paragraph["paragraph_id"],
                target_page=data["page_id"],
                target_paragraph=data["paragraph_id"]
            )
        return defResult

    def OnLeave(self):
        self._clear()

    def _clear(self):
        if self.data is not None:
            self.data["window"].Hide()
            self.data = None


class PageWorkspace(wx.ScrolledWindow):

    def __init__(self, parent, document):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(20, 20)
        self.SetBackgroundColour((200, 200, 200))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)
        self.listener = Listener(lambda: wx.CallAfter(self.Render))
        self.columns = []
        self.SetDocument(document)
        self.SetDropTarget(PageWorkspaceDropTarget(self))

    def FindParagraph(self, screen_pos):
        return find_first(self.columns, lambda column: column.FindParagraph(screen_pos))

    def SetDocument(self, document):
        while self.columns:
            column = self.columns.pop()
            self.sizer.Detach(column)
            column.Destroy()
        self.document = document
        self.scratch_column = self.AddColumn()
        self.listener.set_observable(self.document)
        self.GetTopLevelParent().Layout()

    def Render(self):
        for column in self.columns:
            column.Render()

    def OpenScratch(self, page_ids):
        self.scratch_column.SetPages(page_ids)
        self.GetTopLevelParent().Layout()

    def AddColumn(self):
        column = Column(self, self.document)
        self.columns.append(column)
        self.sizer.Add(column, flag=wx.RIGHT, border=PAGE_PADDING)
        return column


class Column(wx.Panel):

    def __init__(self, parent, document):
        wx.Panel.__init__(self, parent, size=(PAGE_BODY_WIDTH+2*PARAGRAPH_SPACE+SHADOW_SIZE, -1))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)
        self.document = document
        self.pages = []

    def FindParagraph(self, screen_pos):
        return find_first(self.pages, lambda page: page.FindParagraph(screen_pos))

    def Render(self):
        for page in self.pages:
            page.Render()

    def SetPages(self, page_ids):
        while self.pages:
            page = self.pages.pop()
            self.sizer.Detach(page)
            page.Destroy()
        for page_id in page_ids:
            self.AddPage(page_id)

    def AddPage(self, page_id):
        page = PageContainer(self, self.document, page_id)
        self.pages.append(page)
        self.sizer.Add(page, flag=wx.BOTTOM|wx.EXPAND, border=PAGE_PADDING)
        return page


class PageContainer(wx.Panel):

    def __init__(self, parent, document, page_id):
        wx.Panel.__init__(self, parent)
        self.page_body = Page(self, document, page_id)
        self.SetBackgroundColour((150, 150, 150))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.page_body, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=SHADOW_SIZE)
        self.SetSizer(self.sizer)
        self.Render()

    def FindParagraph(self, screen_pos):
        return self.page_body.FindParagraph(screen_pos)

    def Render(self):
        self.page_body.Render()


class Page(wx.Panel):

    def __init__(self, parent, document, page_id):
        wx.Panel.__init__(self, parent)
        self.document = document
        self.page_id = page_id
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def FindParagraph(self, screen_pos):
        client_pos = (client_x, client_y) = self.ScreenToClient(screen_pos)
        if self.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
            data = {"page_id": self.page_id}
            for paragraph, divider in self.paragraphs:
                if paragraph is not None:
                    data["paragraph_id"] = paragraph.paragraph["id"]
                    if client_y < (paragraph.Position.y + paragraph.Size[1] / 2):
                        break
                data["window"] = divider
                data["paragraph_id"] = None
            return data

    def Render(self):
        self.paragraphs = []
        page = self.document.get_page(self.page_id)
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PARAGRAPH_SPACE)
        self.AddParagraph(Title(self, self.document, page), True)
        for paragraph in page["paragraphs"]:
            self.AddParagraph({
                "text": Paragraph,
                "factory": Factory,
            }[paragraph["type"]](self, self.document, self.page_id, paragraph))
        self.CreateMenu()
        self.GetTopLevelParent().Layout()

    def CreateMenu(self):
        add_button = wx.BitmapButton(
            self,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK,
            wx.ART_BUTTON, (16, 16)),
            style=wx.NO_BORDER
        )
        add_button.Bind(wx.EVT_BUTTON, self.OnButton)
        self.sizer.Add(
            add_button,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT,
            border=PARAGRAPH_SPACE
        )

    def OnButton(self, event):
        self.document.add_paragraph(self.page_id)

    def AddParagraph(self, paragraph, write_none=False):
        self.sizer.Add(
            paragraph,
            flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=PARAGRAPH_SPACE
        )
        divider = Divider(self, padding=(PARAGRAPH_SPACE-3)/2, height=3)
        self.sizer.Add(
            divider,
            flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=PARAGRAPH_SPACE
        )
        self.paragraphs.append((paragraph if write_none is False else None, divider))


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


class Editable(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.view = self.CreateView()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.view, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)
        self.view.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)

    def OnLeftDclick(self, event):
        self.edit = self.CreateEdit()
        self.edit.SetFocus()
        self.edit.Bind(wx.EVT_CHAR, self.OnChar)
        self.sizer.Add(self.edit, flag=wx.EXPAND, proportion=1)
        self.sizer.Hide(self.view)
        self.GetTopLevelParent().Layout()

    def OnChar(self, event):
        if event.KeyCode == wx.WXK_CONTROL_S:
            self.EndEdit()
        elif event.KeyCode == wx.WXK_RETURN and event.ControlDown():
            self.EndEdit()
        else:
            event.Skip()


class ParagraphBase(object):

    def __init__(self, document, page_id, paragraph):
        self.document = document
        self.page_id = page_id
        self.paragraph = paragraph

    def configure_drag(self, window):
        self.mouse_event_helper = MouseEventHelper(window)
        self.mouse_event_helper.OnDrag = self._on_drag

    def _on_drag(self):
        data = RliterateDataObject("paragraph", {
            "page_id": self.page_id,
            "paragraph_id": self.paragraph["id"],
        })
        drag_source = wx.DropSource(self)
        drag_source.SetData(data)
        result = drag_source.DoDragDrop(wx.Drag_DefaultMove)


class MouseEventHelper(object):

    def __init__(self, window):
        self.down_pos = None
        window.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        window.Bind(wx.EVT_MOTION, self._on_motion)
        window.Bind(wx.EVT_LEFT_UP, self._on_left_up)

    def OnDrag(self):
        pass

    def OnClick(self):
        pass

    def _on_left_down(self, event):
        self.down_pos = event.Position

    def _on_motion(self, event):
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


class Paragraph(ParagraphBase, Editable):

    def __init__(self, parent, document, page_id, paragraph):
        ParagraphBase.__init__(self, document, page_id, paragraph)
        Editable.__init__(self, parent)

    def CreateView(self):
        view = wx.StaticText(self, label=self.paragraph["text"])
        view.Wrap(PAGE_BODY_WIDTH)
        self.configure_drag(view)
        return view

    def CreateEdit(self):
        edit = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE,
            value=self.paragraph["text"]
        )
        # Error is printed if height is too small:
        # Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size >= 0' failed in GtkScrollbar
        # Solution: Make it at least 50 heigh.
        edit.MinSize = (-1, max(50, self.view.Size[1]))
        return edit

    def EndEdit(self):
        self.document.edit_paragraph(self.paragraph["id"], {"text": self.edit.Value})


class Factory(ParagraphBase, wx.Panel):

    def __init__(self, parent, document, page_id, paragraph):
        ParagraphBase.__init__(self, document, page_id, paragraph)
        wx.Panel.__init__(self, parent)
        self.configure_drag(self)
        self.SetBackgroundColour((240, 240, 240))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(
            wx.StaticText(self, label="Factory"),
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        text_button = wx.Button(
            self,
            label="Text",
            style=wx.NO_BORDER
        )
        text_button.Bind(wx.EVT_BUTTON, self.OnTextButton)
        self.sizer.Add(
            text_button,
            flag=wx.TOP|wx.ALIGN_CENTER,
            border=PARAGRAPH_SPACE
        )
        self.sizer.AddSpacer(PARAGRAPH_SPACE)
        self.SetSizer(self.sizer)

    def OnTextButton(self, event):
        self.document.edit_paragraph(self.paragraph["id"], {"type": "text", "text": "Enter text here..."})


class Title(Editable):

    def __init__(self, parent, document, page):
        self.document = document
        self.page = page
        Editable.__init__(self, parent)

    def CreateView(self):
        view = wx.StaticText(
            self,
            label=self.page["title"],
            style=wx.ST_ELLIPSIZE_END
        )
        view.SetToolTip(wx.ToolTip(self.page["title"]))
        increase_font(view)
        return view

    def CreateEdit(self):
        edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.page["title"])
        edit.Bind(wx.EVT_TEXT_ENTER, lambda _: self.EndEdit())
        increase_font(edit)
        return edit

    def EndEdit(self):
        self.document.edit_page(self.page["id"], {"title": self.edit.Value})


def increase_font(control):
    # The space for this control is not calculated correctly when changing
    # the font. Setting min height explicitly seems to work.
    old_char_height = control.GetCharHeight()
    old_height = control.Size[1]
    control.Font = control.Font.Larger().Larger()
    control.MinSize = (-1, old_height + (control.GetCharHeight() - old_char_height))


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()
