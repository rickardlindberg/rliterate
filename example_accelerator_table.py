import wx

class Frame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)

        a_id = wx.NewId()
        b_id = wx.NewId()

        entries = [wx.AcceleratorEntry() for i in xrange(2)]

        entries[0].Set(wx.ACCEL_CTRL, ord('A'), a_id)
        entries[1].Set(wx.ACCEL_CTRL, ord('B'), b_id)

        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        self.Bind(wx.EVT_MENU, self._a_event, id=a_id)
        self.Bind(wx.EVT_MENU, self._b_event, id=b_id)

        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollRate(10, 10)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._populate()
        self.panel.SetSizer(self.sizer)

    def _populate(self):
        self.sizer.Clear(True)
        for index in range(10):
            self.sizer.Add(wx.TextCtrl(self.panel, value="label {}".format(index)))
        self.panel.SetFocus()

    def _a_event(self, event):
        print("a")
        self._populate()
        self.panel.Layout()

    def _b_event(self, event):
        print("b")

app = wx.App()
frame = Frame()
frame.Show()
app.MainLoop()
