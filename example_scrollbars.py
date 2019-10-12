import wx

class Frame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.container = self._create_scroll_window()
        sizer.Add(wx.Button(self, label="other"))
        sizer.Add(self.container)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_SIZE, lambda event: self._print_info("resize"))
        self._print_info("init")

    def _create_scroll_window(self):
        container = wx.ScrolledWindow(
            self,
            style=wx.HSCROLL,
            size=(200, 200)
        )
        container.SetScrollRate(1, 0)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for index in range(30):
            sizer.Add(
                wx.Button(container, label="Button {}".format(index))
            )
        container.SetSizer(sizer)
        return container

    def _print_info(self, header):
        print("{}:".format(header))
        print("  Frame size = {}".format(self.Size))
        print("  Sizer size = {}".format(self.container.GetSizer().Size))
        print("----")

app = wx.App()
frame = Frame()
frame.Show()
app.MainLoop()
