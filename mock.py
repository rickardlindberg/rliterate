import contextlib
import uuid

import wx


PAGE_BODY_WIDTH = 500
PAGE_PADDING = 10
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 10


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

    # Paragraph operations

    def add_paragraph(self, page_id, before_id=None):
        with self.notify():
            pass

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
        self.listener = Listener(self.Render)
        self.SetDocument(document)
        self.allow_selection_events = False

    def SetDocument(self, document):
        self.document = document
        self.listener.set_observable(self.document)
        self.page_workspace.OpenScratch([self.GetItemData(self.GetSelection()).GetData()])

    def Render(self):

        def add_child(parent, child):
            tree_id = self.AppendItem(parent, child["title"], data=wx.TreeItemData(child["id"]))
            preprocess(tree_id, child["id"])

        def preprocess(tree_id, item_id):
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
        preprocess(parent, toc["id"])

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


class PageWorkspace(wx.ScrolledWindow):

    def __init__(self, parent, document):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(20, 20)
        self.SetBackgroundColour((200, 200, 200))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)
        self.listener = Listener(self.Render)
        self.columns = []
        self.SetDocument(document)

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

    def Render(self):
        page = self.document.get_page(self.page_id)
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PARAGRAPH_SPACE)
        self.AddParagraph(Title(self, page["title"]))
        for paragraph in page["paragraphs"]:
            self.AddParagraph(Paragraph(self, self.document, paragraph))
        self.GetTopLevelParent().Layout()

    def AddParagraph(self, paragraph):
        self.sizer.Add(
            paragraph,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,
            border=PARAGRAPH_SPACE
        )


class Paragraph(wx.Panel):

    def __init__(self, parent, document, paragraph):
        wx.Panel.__init__(self, parent)

        self.document = document
        self.paragraph = paragraph

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.view = wx.StaticText(self, label=self.paragraph["text"])
        self.view.Wrap(PAGE_BODY_WIDTH)
        self.sizer.Add(self.view, flag=wx.EXPAND, proportion=1)

        self.view.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)

    def OnLeftDclick(self, event):
        self.sizer.Detach(self.view)
        self.view.Destroy()
        del self.view

        self.edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.paragraph["text"])
        self.sizer.Add(self.edit, flag=wx.EXPAND, proportion=1)
        self.edit.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)

        self.GetTopLevelParent().Layout()

    def OnTextEnter(self, event):
        self.document.edit_paragraph(self.paragraph["id"], {"text": self.edit.Value})


class Title(wx.StaticText):

    def __init__(self, parent, title):
        wx.StaticText.__init__(
            self,
            parent,
            label=title,
            style=wx.ST_ELLIPSIZE_END
        )
        self.SetToolTip(wx.ToolTip(title))
        self.Font = self.Font.Larger().Larger()
        # The space for this control is not calculated correctly when changing
        # the font. Setting the min height explicitly seems to work.
        self.MinSize = (-1, self.GetCharHeight()) # Hack to not have to red


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()
