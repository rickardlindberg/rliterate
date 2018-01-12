import wx


PAGE_BODY_WIDTH = 300
PAGE_PADDING = 10
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 10


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)
        columns = Columns(self)
        columns.AddColumn()
        columns.AddColumn()
        columns.AddColumn()


class Columns(wx.ScrolledWindow):

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetBackgroundColour((200, 200, 200))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)

    def AddColumn(self):
        column = Column(self)
        page1 = column.AddPage()
        page1.AddParagraph("page 1 p 1 this is this is this is this is this is this is this is this is")
        page1.AddParagraph("page 1 p 2")
        page2 = column.AddPage()
        page2.AddParagraph("page 2 p 1")
        page2.AddParagraph("page 2 p 2")
        self.sizer.Add(column, flag=wx.RIGHT, border=PAGE_PADDING)
        return column


class Column(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(PAGE_BODY_WIDTH+2*PARAGRAPH_SPACE+SHADOW_SIZE, -1))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)

    def AddPage(self):
        page = Page(self)
        self.sizer.Add(page, flag=wx.BOTTOM|wx.EXPAND, border=PAGE_PADDING)
        return page


class Page(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.inner_panel = wx.Panel(self)
        self.inner_panel.SetBackgroundColour(wx.WHITE)
        self.inner_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer.AddSpacer(PARAGRAPH_SPACE)
        self.inner_panel.SetSizer(self.inner_sizer)
        self.SetBackgroundColour((150, 150, 150))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.inner_panel, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=SHADOW_SIZE)
        self.SetSizer(self.sizer)

    def AddParagraph(self, text):
        self.inner_sizer.Add(Paragraph(self.inner_panel, text), flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=PARAGRAPH_SPACE)


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


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    main_frame.Layout()
    app.MainLoop()
