import contextlib
import json
import uuid

import wx


PAGE_BODY_WIDTH = 500
PAGE_PADDING = 12
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 15


def genid():
    return uuid.uuid4().hex


EXAMPLE_DOCUMENT = {
    "id": genid(),
    "title": "Test document",
    "paragraphs": [
        {
            "id": genid(),
            "type": "text",
            "text": "This is just a test document.",
        },
        {
            "id": genid(),
            "type": "text",
            "text": "... some more text ...",
        },
    ],
    "children": [
        {
            "id": genid(),
            "title": "Child 1",
            "paragraphs": [
                {
                    "id": genid(),
                    "type": "text",
                    "text": "I am the first child.",
                },
                {
                    "id": genid(),
                    "type": "text",
                    "text": "... some more text ... but this time with really a lot of text so that breaking the paragraph is necessary",
                },
            ],
            "children": [],
        },
        {
            "id": genid(),
            "title": "Child 2",
            "paragraphs": [
                {
                    "id": genid(),
                    "type": "text",
                    "text": "I am the second child.",
                },
                {
                    "id": genid(),
                    "type": "text",
                    "text": "... some more text ...",
                },
            ],
            "children": [
                {
                    "id": genid(),
                    "title": "Child 2 2",
                    "paragraphs": [
                        {
                            "id": genid(),
                            "type": "text",
                            "text": "I am the second grandchild.",
                        },
                        {
                            "id": genid(),
                            "type": "text",
                            "text": "... some more text ...",
                        },
                    ],
                    "children": [],
                },
            ],
        },
        {
            "id": genid(),
            "title": "Child 3",
            "paragraphs": [],
            "children": [],
        },
        {
            "id": genid(),
            "title": "Child 4",
            "paragraphs": [],
            "children": [],
        },
        {
            "id": genid(),
            "title": "Child 5",
            "paragraphs": [],
            "children": [],
        },
        {
            "id": genid(),
            "title": "Child 6",
            "paragraphs": [],
            "children": [],
        },
    ],
}


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
    def from_py_obj(cls, py_obj):
        return cls(py_obj)

    def __init__(self, py_obj):
        self.py_obj = py_obj
        self.listeners = []
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
        def find_page(page):
            if page["id"] == page_id:
                return {
                    "id": page["id"],
                    "title": page["title"],
                    "paragraphs": page["paragraphs"],
                }
            for child in page["children"]:
                x = find_page(child)
                if x is not None:
                    return x
            return None
        return find_page(self.py_obj)

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

        document = Document.from_py_obj(EXAMPLE_DOCUMENT)

        page_workspace = PageWorkspace(self, document)

        toc = TableOfContents(self, page_workspace, document)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(toc, flag=wx.EXPAND, proportion=0)
        sizer.Add(page_workspace, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class TableOfContents(wx.TreeCtrl):

    def __init__(self, parent, page_workspace, document):
        wx.TreeCtrl.__init__(
            self,
            parent,
            size=(200, -1),
            style=wx.TR_DEFAULT_STYLE|wx.TR_SINGLE
        )
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)
        self.page_workspace = page_workspace
        self.listener = Listener(lambda: wx.CallAfter(self.Render))
        self.SetDocument(document)
        self.allow_selection_events = True

    def SetDocument(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def Render(self):

        def add_child(parent, child):
            tree_id = self.AppendItem(parent, child["title"], data=wx.TreeItemData(child["id"]))
            for x in child["children"]:
                add_child(tree_id, x)
            postprocess(tree_id, child["id"])

        def postprocess(tree_id, item_id):
            self.Expand(tree_id)
            if item_id == selected_id:
                self.allow_selection_events = False
                self.SelectItem(tree_id)
                self.allow_selection_events = True

        selected_id = None
        if self.GetSelection().IsOk():
            selected_id = self.GetItemData(self.GetSelection()).GetData()

        self.DeleteAllItems()
        toc = self.document.get_toc()
        parent = self.AddRoot(toc["title"], data=wx.TreeItemData(toc["id"]))
        for child in toc["children"]:
            add_child(parent, child)
        postprocess(parent, toc["id"])
        if selected_id is None:
            self.page_workspace.OpenScratch([self.GetItemData(self.GetSelection()).GetData()])

    def OnTreeSelChanged(self, event):
        if self.allow_selection_events:
            self.page_workspace.OpenScratch([self.GetItemData(event.GetItem()).GetData()])

    def OnTreeItemActivated(self, event):
        root = event.GetItem()
        page_ids = []
        page_ids.append(self.GetItemData(root).GetData())
        (x, cookie) = self.GetFirstChild(root)
        while x.IsOk():
            page_ids.append(self.GetItemData(x).GetData())
            x = self.GetNextSibling(x)
        self.page_workspace.OpenScratch(page_ids)


def find_first(items, action):
    for item in items:
        result = action(item)
        if result is not None:
            return result
    return None


class RliterateDataObject(wx.CustomDataObject):

    def __init__(self, json=None):
        wx.CustomDataObject.__init__(self, "rliterate")
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
        self.rliterate_data = RliterateDataObject()
        self.DataObject = self.rliterate_data

    def OnDragOver(self, x, y, defResult):
        self._clear()
        data = self.workspace.FindParagraph(self.workspace.ClientToScreen((x, y)))
        if data is not None:
            self.data = data
            self.data["window"].SetBackgroundColour((255, 100, 0))
        return defResult

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
            self.data["window"].SetBackgroundColour((255, 255, 255))
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
        divider = wx.Panel(self, size=(-1, PARAGRAPH_SPACE))
        self.sizer.Add(
            divider,
            flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=PARAGRAPH_SPACE
        )
        self.paragraphs.append((paragraph if write_none is False else None, divider))


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
        self.down_pos = None

    def configure_drag(self, window):
        window.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        window.Bind(wx.EVT_MOTION, self._on_motion)
        window.Bind(wx.EVT_LEFT_UP, self._on_left_up)

    def _on_left_down(self, event):
        self.down_pos = event.Position

    def _on_motion(self, event):
        if self._should_drag(event.Position):
            self.down_pos = None
            data = RliterateDataObject({
                "page_id": self.page_id,
                "paragraph_id": self.paragraph["id"],
            })
            drag_source = wx.DropSource(self)
            drag_source.SetData(data)
            result = drag_source.DoDragDrop(wx.Drag_DefaultMove)

    def _should_drag(self, pos):
        if self.down_pos is not None:
            diff = self.down_pos - pos
            if abs(diff.x) > 2:
                return True
            if abs(diff.y) > 2:
                return True
        return False

    def _on_left_up(self, event):
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
