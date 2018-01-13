import uuid

import wx


PAGE_BODY_WIDTH = 300
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
                    "text": "... some more text ...",
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


class Document(object):

    @classmethod
    def from_py_obj(cls, py_obj):
        return cls(py_obj)

    def __init__(self, py_obj):
        self.py_obj = py_obj

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
        pass

    def remove_page(self, page_id):
        pass

    def move_page(self, page_id, target_spec):
        pass

    # Paragraph operations

    def add_paragraph(self, page_id, before_id=None):
        pass

    def remove_paragraph(self, page_id, paragraph_id):
        pass

    def edit_paragraph(self, paragraph_id, data):
        pass


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)
        MainPanel(self)


class MainPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        document = Document.from_py_obj(EXAMPLE_DOCUMENT)

        page_workspace = PageWorkspace(self, document)

        toc = TableOfContents(self, page_workspace, document)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(toc, flag=wx.EXPAND, proportion=0)
        sizer.Add(page_workspace, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

        self.Layout()


class TableOfContents(wx.TreeCtrl):

    def __init__(self, parent, page_workspace, document):
        wx.TreeCtrl.__init__(
            self,
            parent,
            size=(200, -1),
            style=wx.TR_DEFAULT_STYLE|wx.TR_SINGLE
        )
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged)
        self.page_workspace = page_workspace
        self.SetDocument(document)

    def SetDocument(self, document):
        self.document = document
        self.Render()

    def Render(self):
        def add_child(parent, child):
            self.AppendItem(parent, child["title"], data=wx.TreeItemData(child["id"]))
        self.DeleteAllItems()
        toc = self.document.get_toc()
        parent = self.AddRoot(toc["title"], data=wx.TreeItemData(toc["id"]))
        for child in toc["children"]:
            add_child(parent, child)
        self.ExpandAll()
        self.page_workspace.OpenScratch([self.GetItemData(self.GetSelection()).GetData()])

    def OnTreeSelChanged(self, event):
        self.page_workspace.OpenScratch([self.GetItemData(event.GetItem()).GetData()])


class PageWorkspace(wx.ScrolledWindow):

    def __init__(self, parent, document):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(20, 20)
        self.SetBackgroundColour((200, 200, 200))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.SetDocument(document)

    def SetDocument(self, document):
        self.document = document
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.scratch_column = self.AddColumn()

    def OpenScratch(self, page_ids):
        self.scratch_column.SetPages(page_ids)
        self.Layout()

    def AddColumn(self):
        column = Column(self, self.document)
        self.sizer.Add(column, flag=wx.RIGHT, border=PAGE_PADDING)
        return column


class Column(wx.Panel):

    def __init__(self, parent, document):
        wx.Panel.__init__(self, parent, size=(PAGE_BODY_WIDTH+2*PARAGRAPH_SPACE+SHADOW_SIZE, -1))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)
        self.document = document

    def SetPages(self, page_ids):
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PAGE_PADDING)
        for page_id in page_ids:
            self.AddPage(page_id)

    def AddPage(self, page_id):
        page = PageContainer(self, self.document, page_id)
        self.sizer.Add(page, flag=wx.BOTTOM|wx.EXPAND, border=PAGE_PADDING)
        return page


class PageContainer(wx.Panel):

    def __init__(self, parent, document, page_id):
        wx.Panel.__init__(self, parent)
        self.page_body = Page(self)
        self.SetBackgroundColour((150, 150, 150))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.page_body, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=SHADOW_SIZE)
        self.SetSizer(self.sizer)
        self.page_body.Render(document.get_page(page_id))


class Page(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def Render(self, page):
        self.sizer.Clear(True)
        self.sizer.AddSpacer(PARAGRAPH_SPACE)
        self.AddParagraph(Title(self, page["title"]))
        for paragraph in page["paragraphs"]:
            self.AddParagraph(Paragraph(self, paragraph["text"]))

    def AddParagraph(self, paragraph):
        self.sizer.Add(
            paragraph,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,
            border=PARAGRAPH_SPACE
        )


class Paragraph(wx.Panel):

    def __init__(self, parent, text):
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        text = wx.StaticText(self, label=text)
        text.Wrap(PAGE_BODY_WIDTH)

    def OnEnterWindow(self, event):
        self.SetBackgroundColour(wx.YELLOW)

    def OnLeaveWindow(self, event):
        self.SetBackgroundColour(wx.WHITE)


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


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    main_frame.Layout()
    app.MainLoop()
