# RLiterate

RLiterate is a tool for reading and authoring documents. Documents have pages organized in a hierarchy. Pages have a title and paragraphs. Paragraphs can be of different types. The different paragraph types is what makes RLiterate documents special. Code paragraphs for example enable literate programming by allowing chunks of code to be defined and then be automatically assembled into the final source file. Text paragraphs are used for writing prose. RLiterate documents can also be exported to different formats for display in different mediums.


## A tour of RLiterate

This chapter gives an overview what RLiterate looks like.

### Main GUI

* smallest federated wiki inspired the factory and the editing workflow
* leo and smallest federated wiki inspired TOC and seeing a single page/node at a time

### Reading tool

RLiterate is a reading and thinking tool. The following features support that.

Hoisting a page in the table of contents allows you to **focus on a subset** of the document.

Openining a page and all immediate children (double click on a page in the table of contents) allows you to read a subset of the document **breath first**. It's like reading only the first paragraph in an entire book.

### Literate programming

Describe how code paragraphs enable literate programming.

## Background

Many things inspired RLiterate, but the initial thought was triggered by the paper [Active Essays on the Web](http://www.vpri.org/pdf/tr2009002_active_essays.pdf). In it they talk about embedding code in documents that the reader can interact with. They also mention [Literate programming](https://en.wikipedia.org/wiki/Literate_programming) as having a related goal.

At the time I was working on a program that I thought would be nice to express in this way. I wanted to write an article about the program and have the code for the program embedded in the article. I could have used a literate programming tool for this, but the interactive aspect of active essays made me think that a tool would be much more powerful if the document could be edited "live", similar to WYSIWYG editors. Literate programming tools I were aware of worked by editing plain text files with a special syntax for code and documentation blocks, thus lacking the interactive aspect.

### The prototype

So I decided to build a prototype to learn what such a tool might be like.


First I came up with a document model where pages were organized in a hierarchy and where each page had paragraphs that could be of different types. This idea was stolen from [Smallest Federated Wiki](https://en.wikipedia.org/wiki/Smallest_Federated_Wiki). The code paragraph would allow for literate programming. I also envisioned other paragraph types that would allow for more interaction. Perhaps one paragraph type could be [Graphviz](http://graphviz.org/) code, and when edited, a generated graph would appear instead of the code.

After coming up with a document model, I implement a GUI that would allow editing such documents. This GUI had to be first class as it would be the primary way to read and author documents.

At a certain point I had all the functionality in place for doing literate programming. Then I imported all the code into an RLiterate document (previously it was written as a single Python file) and started extracting pieces and adding prose to explain the program. As I went along I noticed features I was lacking.

### Why literate programming?

To me, the most central idea in literate programming is that we should write programs for other humans. Only secondary for the machine. I find code easier to understand if I can understand it in isolated pieces. One example where it is difficult to isolate a piece without literate programming is test code. Usually the test code is located in one file, and the implementation in another. To fully understand the piece it is useful to both read the tests and the implementation. To do this we have to find this related information in two unrelated files. I wrote about this problem in 2003 in [Related things are not kept together](http://rickardlindberg.me/writing/reflections-on-programming/2013-02-24-related-things-are-not-kept-together/). Literate programming allows us to present the test and the implementation in the same place, yet have the different pieces written to different files. The compiler might require that they are in separate files, but with literate programming, we care first about the other human that will read our code, and only second about the compiler.

Another argument for literate programming is to express the "why". Why is this code here? Timothy Daly talks about it in his talk [Literate Programming in the Large](https://www.youtube.com/watch?v=Av0PQDVTP4A). He also argues that programmers must change the mindset from wring a program to writing a book. Some more can be read here: http://axiom-developer.org/axiom-website/litprog.html.

Some more resources about literate programming:

* https://www.youtube.com/watch?v=5V1ynVyud4M
  "Eve" by Chris Granger

* http://eve-lang.com/deepdives/literate.html

* https://software-carpentry.org/blog/2011/03/literate-programming.html

### Similar tools

I stumbled across [ProjecturED](http://projectured.org/). It is similar to RLiterate in the sense that it is an editor for richer documents. Not just text. The most interesting aspect for me is that a variable name exists in one place, but can be rendered in multiple. So a rename is really simple. With RLiterate, you have to do a search and replace. But with ProjecturED you just change the name and it replicates everywhere. This is an attractive feature and is made possible by the different document model. Probably RLiterate can never support that because a completely different approach needs to be taken, but it is an interesting project to investigate further.


## Implementation

RLiterate is implemented in Python. This chapter gives a complete description of all the code.

### GUI wxPython

The main GUI is written in wxPython.

#### Main frame

The main frame lays out two widgets horizontally: the table of contents and the workspace. It also creates the project from the specified file path.

`rliterate.py / <<classes>>`:

```python
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
```

#### Table of contents

The table of contents shows the outline of the document. It allows only subtrees to be shown (hoisting) and allows subtrees to be expanded/collapsed. It also provides navigation functions to allow pages to be opened.

##### Main widget

The main table of contents widget listens for changes to a project (only events related to changes in the document and the layout of the table of contents) and then re-renders itself.

`rliterate.py / <<classes>>`:

```python
class TableOfContents(wx.Panel):
    <<TableOfContents>>
```

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
def __init__(self, parent, project):
    wx.Panel.__init__(self, parent, size=(250, -1))
    self.project_listener = Listener(
        self._re_render_from_event,
        "document", "layout.toc"
    )
    self.SetProject(project)
    <<__init__>>
    self._render()

def SetProject(self, project):
    self.project = project
    self.project_listener.set_observable(self.project)
```

This seems to be needed for some reason:

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
def _re_render_from_event(self, event):
    wx.CallAfter(self._re_render)
```

###### Rendering

The table of contents widget lays out two components in a vertical container: the unhoist button and the page container.

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
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
```

The unhoist button (only shown if a page has been hoisted):

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
def _render_unhoist_button(self):
    if self.project.get_hoisted_page() is not None:
        button = wx.Button(self, label="unhoist")
        button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.project.set_hoisted_page(None)
        )
        self.sizer.Add(button, flag=wx.EXPAND)
```

The page container is a scrolling container that contains a set of rows representing pages. Each row is appropriately intendent to create the illusion of a tree.

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
def _render_page_container(self):
    self.page_sizer = wx.BoxSizer(wx.VERTICAL)
    self.page_container = wx.ScrolledWindow(self)
    self.page_container.SetScrollRate(20, 20)
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
```

`rliterate.py / <<classes>>`:

```python
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
```

###### Dropping pages

Inside the table of contents, pages can be dragged and drop. The drag is initiated in the row widget and handled in the table of contents widget.

`rliterate.py / <<classes>> / <<TableOfContents>> / <<__init__>>`:

```python
self.SetDropTarget(TableOfContentsDropTarget(self, self.project))
```

`rliterate.py / <<classes>>`:

```python
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
```

The DropPointDropTarget requires FindClosestDropPoint to be defined on the target object. Here it is:

`rliterate.py / <<classes>> / <<TableOfContents>>`:

```python
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
```

##### Row widget

The row widget renders the page title at the appropriate indentation. If the page has children, an expand/collapse widget is also rendered to the left of the title.

`rliterate.py / <<classes>>`:

```python
class TableOfContentsRow(wx.Panel):

    def __init__(self, parent, project, page, indentation):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.page = page
        self.indentation = indentation
        self._render()

    <<TableOfContentsRow>>
```

Rendering lays out expand/collapse button (if the page has children) and the page title in a horizontal sizer:

`rliterate.py / <<classes>> / <<TableOfContentsRow>>`:

```python
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
```

Event handlers:

`rliterate.py / <<classes>> / <<TableOfContentsRow>>`:

```python
def _on_click(self):
    self.project.set_scratch_pages([self.page.id])

def _on_double_click(self):
    page_ids = [self.page.id]
    for child in self.project.get_page(self.page.id).children:
        page_ids.append(child.id)
    self.project.set_scratch_pages(page_ids)

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
```

##### Expand/Collapse widget

`rliterate.py / <<classes>>`:

```python
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
```

##### Page context menu

`rliterate.py / <<classes>>`:

```python
class PageContextMenu(wx.Menu):

    def __init__(self, project, page):
        wx.Menu.__init__(self)
        self.project = project
        self.page = page
        self._create_menu()

    def _create_menu(self):
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
```

#### Workspace

The workspace shows body content of pages in the document. It is organized in columns, and each column can show body content from multiple pages.


##### Main widget

The main workspace widget is a scrolling container containing column widgets.

`rliterate.py / <<classes>>`:

```python
class Workspace(wx.ScrolledWindow):
    <<Workspace>>
```

`rliterate.py / <<classes>> / <<Workspace>>`:

```python
def __init__(self, parent, project):
    wx.ScrolledWindow.__init__(
        self,
        parent,
        size=(int(PAGE_BODY_WIDTH*1.2), 300)
    )
    self.project_listener = Listener(
        self._re_render_from_event,
        "document",
        "layout.workspace"
    )
    self.SetProject(project)
    <<__init__>>
    self._render()

def SetProject(self, project):
    self.project = project
    self.project_listener.set_observable(self.project)
```

###### Rendering

Rendering a workspace means laying out a set of column widgets horizontally. Columns are filled with page body content.

Layout has to be called on the parent. Otherwise scrollbars don't update appropriately.

`rliterate.py / <<classes>> / <<Workspace>>`:

```python
def _render(self):
    self.SetScrollRate(20, 20)
    self.SetBackgroundColour((200, 200, 200))
    self.sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.SetSizer(self.sizer)
    self._re_render()

def _re_render(self):
    self.sizer.Clear(True)
    self.pages = []
    self.sizer.AddSpacer(PAGE_PADDING)
    self._render_pages_column(self.project.get_scratch_pages())
    self.Parent.Layout()

def _render_pages_column(self, page_ids):
    column = self._add_column()
    for page_id in page_ids:
        if self.project.get_page(page_id) is not None:
            self.pages.append(
                column.AddContainer().AddPage(self.project, page_id)
            )

def _add_column(self):
    column = Column(self)
    self.sizer.Add(column, flag=wx.RIGHT, border=PAGE_PADDING)
    return column
```

wx.CallAfter seems to be needed to correctly update scrollbars on an event notification. Resizing the window also works.

`rliterate.py / <<classes>> / <<Workspace>>`:

```python
def _re_render_from_event(self, event):
    wx.CallAfter(self._re_render)
```

###### Dropping paragraphs

Inside a workspace, paragraphs can be dragged and dropped. The drag is handled in the paragraph widget, but the drop is handled in the workspace widget.

`rliterate.py / <<classes>> / <<Workspace>> / <<__init__>>`:

```python
self.SetDropTarget(WorkspaceDropTarget(self, self.project))
```

`rliterate.py / <<classes>>`:

```python
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
```

The DropPointDropTarget requires FindClosestDropPoint to be defined on the target object. Here it is:

`rliterate.py / <<classes>> / <<Workspace>>`:

```python
def FindClosestDropPoint(self, screen_pos):
    return find_first(
        self.pages,
        lambda page: page.FindClosestDropPoint(screen_pos)
    )
```

##### Column widget

The column widget is a panel containing containers.

`rliterate.py / <<classes>>`:

```python
class Column(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._setup_layout()

    def _setup_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(PAGE_PADDING)
        self.SetSizer(self.sizer)

    def AddContainer(self):
        container = Container(self)
        self.sizer.Add(
            container,
            flag=wx.BOTTOM|wx.EXPAND,
            border=PAGE_PADDING
        )
        return container
```

##### Container widget

The container widget draws a box with border. Widgets acan then be added to the container. Typically only a single page widget is added.

`rliterate.py / <<classes>>`:

```python
class Container(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(
            self,
            parent,
            size=(PAGE_BODY_WIDTH+2*CONTAINER_BORDER, -1)
        )
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

    def AddPage(self, project, page_id):
        return self._add(Page(self.inner_container, project, page_id))

    def _add(self, widget):
        self.inner_sizer.Add(
            widget,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,
            border=CONTAINER_BORDER
        )
        return widget
```

##### Page

`rliterate.py / <<classes>>`:

```python
class Page(wx.Panel):

    def __init__(self, parent, project, page_id):
        wx.Panel.__init__(self, parent)
        self.project = project
        self.page_id = page_id
        self._render()

    <<Page>>
```

###### Rendering

`rliterate.py / <<classes>> / <<Page>>`:

```python
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
```

`rliterate.py / <<classes>>`:

```python
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
```

###### Dropping paragraphs

`rliterate.py / <<classes>> / <<Page>>`:

```python
def FindClosestDropPoint(self, screen_pos):
    client_pos = (client_x, client_y) = self.ScreenToClient(screen_pos)
    if self.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
        return min_or_none(
            self.drop_points,
            key=lambda drop_point: drop_point.y_distance_to(client_y)
        )
```

##### Title

`rliterate.py / <<classes>>`:

```python
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
            Fragment(self.page.title).word_split(),
            max_width=PAGE_BODY_WIDTH
        )
        return view

    def CreateEdit(self):
        edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.page.title)
        edit.Bind(wx.EVT_TEXT_ENTER, lambda _: self.EndEdit())
        return edit

    def EndEdit(self):
        self.project.edit_page(self.page.id, {"title": self.edit.Value})
```

##### Paragraphs

###### Text

####### Paragraph

`rliterate.py / <<classes>>`:

```python
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
            right_click=self.ShowContextMenu
        )
        return view

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
```

###### Code

####### Container widget

`rliterate.py / <<classes>>`:

```python
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
```

####### View widget

`rliterate.py / <<classes>>`:

```python
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
```

`rliterate.py / <<functions>>`:

```python
def insert_between(separator, items):
    result = []
    for i, item in enumerate(items):
        if i > 0:
            result.append(separator)
        result.append(item)
    return result
```

####### Editor widget

`rliterate.py / <<classes>>`:

```python
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
```

###### Factory

`rliterate.py / <<classes>>`:

```python
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
```

###### Common

####### Paragraph base

`rliterate.py / <<base classes>>`:

```python
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
```

####### Paragraph context menu

`rliterate.py / <<classes>>`:

```python
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
```

####### Editable

`rliterate.py / <<base classes>>`:

```python
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
```

#### Drag & drop

##### RLiterate data object

`rliterate.py / <<classes>>`:

```python
class RliterateDataObject(wx.CustomDataObject):

    def __init__(self, kind, json=None):
        wx.CustomDataObject.__init__(self, "rliterate/{}".format(kind))
        if json is not None:
            self.set_json(json)

    def set_json(self, data):
        self.SetData(json.dumps(data))

    def get_json(self):
        return json.loads(self.GetData())
```

##### Drop point drop target

A drop target that can work with windows that supports FindClosestDropPoint.

`rliterate.py / <<base classes>>`:

```python
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
```

##### Divider

`rliterate.py / <<classes>>`:

```python
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
```

#### wxPython utilities

##### Mouse event helper

`rliterate.py / <<classes>>`:

```python
class MouseEventHelper(object):

    @classmethod
    def bind(cls, windows, drag=None, click=None, right_click=None,
             double_click=None):
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

    def _on_left_dclick(self, event):
        self.OnDoubleClick()

    def _on_right_up(self, event):
        self.OnRightClick()
```

##### Rich text display

The rich text display widget displayes styled text fragments. It does so by drawing text on a DC.

`rliterate.py / <<classes>>`:

```python
class RichTextDisplay(wx.Panel):
    <<RichTextDisplay>>
```

`rliterate.py / <<classes>> / <<RichTextDisplay>>`:

```python
def __init__(self, parent, project, fragments, **kwargs):
    wx.Panel.__init__(self, parent)
    self.project = project
    self.fragments = fragments
    self.line_height = kwargs.get("line_height", 1)
    self.max_width = kwargs.get("max_width", 100)
    <<__init__>>
```

First, the text fragment positions are calculated. For that a DC is needed. But the positions need to be calculated before we can draw on the panel, so a temporary memory DC is created.

`rliterate.py / <<classes>> / <<RichTextDisplay>> / <<__init__>>`:

```python
self._set_fragments()
```

`rliterate.py / <<classes>> / <<RichTextDisplay>>`:

```python
def _set_fragments(self):
    dc = wx.MemoryDC()
    dc.SetFont(self.GetFont())
    dc.SelectObject(wx.EmptyBitmap(1, 1))
    w, h, self.fragments = self._calculate_fragments(dc)
    self.SetMinSize((w, h))

def _calculate_fragments(self, dc):
    fragments = []
    x = 0
    y = 0
    max_x, max_y = dc.GetTextExtent("M")
    for fragment in self._newline_fragments():
        if fragment.text is None:
            x = 0
            y += int(round(dc.GetTextExtent("M")[1]*self.line_height))
            continue
        style = self.project.get_style(fragment.token)
        style.apply_to_wx_dc(dc, self.GetFont())
        w, h = dc.GetTextExtent(fragment.text)
        if x > 0 and x+w > self.max_width:
            x = 0
            y += int(round(dc.GetTextExtent("M")[1]*self.line_height))
        fragments.append((fragment.text, style, x, y))
        max_x = max(max_x, x+w)
        max_y = max(max_y, y+h)
        x += w
    return (max_x, max_y, fragments)

def _newline_fragments(self):
    for fragment in self.fragments:
        if "\n" in fragment.text:
            for x in insert_between(None, fragment.text.split("\n")):
                yield Fragment(x, token=fragment.token)
        else:
            yield fragment
```

Drawing the rich text is just a matter of drawing all fragments at the pre-calculated positions:

`rliterate.py / <<classes>> / <<RichTextDisplay>> / <<__init__>>`:

```python
self.Bind(wx.EVT_PAINT, self._on_paint)
```

`rliterate.py / <<classes>> / <<RichTextDisplay>>`:

```python
def _on_paint(self, event):
    dc = wx.PaintDC(self)
    for text, style, x, y in self.fragments:
        style.apply_to_wx_dc(dc, self.GetFont())
        dc.DrawText(text, x, y)
```

#### Constants

`rliterate.py / <<constants>>`:

```python
PAGE_BODY_WIDTH = 600
PAGE_PADDING = 12
SHADOW_SIZE = 2
PARAGRAPH_SPACE = 15
CONTAINER_BORDER = PARAGRAPH_SPACE


ParagraphEditStart, EVT_PARAGRAPH_EDIT_START = wx.lib.newevent.NewCommandEvent()
ParagraphEditEnd, EVT_PARAGRAPH_EDIT_END = wx.lib.newevent.NewCommandEvent()
```

### Project

A project is a container for a few other objects:

`rliterate.py / <<classes>>`:

```python
class Project(Observable):

    def __init__(self, filepath):
        Observable.__init__(self)
        self.theme = SolarizedTheme()
        self.document = Document.from_file(filepath)
        self.document.listen(self.notify_forwarder("document"))
        self.layout = Layout(".{}.layout".format(filepath))
        self.layout.listen(self.notify_forwarder("layout"))
        FileGenerator().set_document(self.document)
        MarkdownGenerator(os.path.splitext(filepath)[0]+".markdown").set_document(self.document)
        TextDiff(os.path.splitext(filepath)[0]+".textdiff").set_document(self.document)

    <<Project>>
```

Wrapper methods for layout:

`rliterate.py / <<classes>> / <<Project>>`:

```python
def toggle_collapsed(self, *args, **kwargs):
    return self.layout.toggle_collapsed(*args, **kwargs)

def is_collapsed(self, *args, **kwargs):
    return self.layout.is_collapsed(*args, **kwargs)

def get_scratch_pages(self, *args, **kwargs):
    return self.layout.get_scratch_pages(*args, **kwargs)

def set_scratch_pages(self, *args, **kwargs):
    return self.layout.set_scratch_pages(*args, **kwargs)

def get_hoisted_page(self, *args, **kwargs):
    return self.layout.get_hoisted_page(*args, **kwargs)

def set_hoisted_page(self, *args, **kwargs):
    return self.layout.set_hoisted_page(*args, **kwargs)
```

Wrapper methods for document:

`rliterate.py / <<classes>> / <<Project>>`:

```python
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
```

Wrapper for theme:

`rliterate.py / <<classes>> / <<Project>>`:

```python
def get_style(self, *args, **kwargs):
    return self.theme.get_style(*args, **kwargs)
```

#### Document model

##### Document

`rliterate.py / <<classes>>`:

```python
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

    <<Document>>

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
```

##### Views

Views provide a read only interface to a document. It is the only way to query a document.

`rliterate.py / <<classes>> / <<Document>>`:

```python
def get_page(self, page_id=None):
    if page_id is None:
        page_id = self.root_page["id"]
    page_dict = self._pages.get(page_id, None)
    if page_dict is None:
        return None
    return DictPage(page_dict)
```

`rliterate.py / <<classes>>`:

```python
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
```

`rliterate.py / <<classes>>`:

```python
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
```

`rliterate.py / <<classes>>`:

```python
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
        while text:
            match = re.match(r"\*\*(.+?)\*\*", text, flags=re.DOTALL)
            if match:
                fragments.extend(Fragment(match.group(1), token=Token.RLiterate.Strong).word_split())
                text = text[match.end(0):]
            else:
                match = re.match(r".+?(\s+|$)", text, flags=re.DOTALL)
                fragments.append(Fragment(match.group(0)))
                text = text[match.end(0):]
        return fragments
```

`rliterate.py / <<classes>>`:

```python
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
            fragments.extend(Fragment(text, token=token).word_split())
        return fragments
```

`rliterate.py / <<classes>>`:

```python
class Fragment(object):

    def __init__(self, text, token=Token.RLiterate):
        self.text = text
        self.token = token

    def word_split(self):
        fragments = []
        text = self.text
        while text:
            match = re.match(r".+?(\s+|$)", text, flags=re.DOTALL)
            fragments.append(Fragment(text=match.group(0), token=self.token))
            text = text[match.end(0):]
        return fragments
```

#### Layouts

A layout knows the visual state of the program. It for example knows what pages are expanded/collapsed in the table of contents and what is shown in the workspace.

The layout is recorded in a JSON object that is serialized to disk as soon as something changes.

`rliterate.py / <<classes>>`:

```python
class Layout(Observable):
    <<Layout>>
```

`rliterate.py / <<classes>> / <<Layout>>`:

```python
def __init__(self, path):
    Observable.__init__(self)
    self.listen(lambda event: write_json_to_file(path, self.data))
    if os.path.exists(path):
        self.data = load_json_from_file(path)
    else:
        self.data = {}
    <<__init__>>
```

The rest of this class provides methods for reading and writing the `data` dict.

The hoisted page is stored in `toc.hoisted_page_id`:

`rliterate.py / <<classes>> / <<Layout>> / <<__init__>>`:

```python
self._toc = ensure_key(self.data, "toc", {})
```

`rliterate.py / <<classes>> / <<Layout>>`:

```python
def get_hoisted_page(self):
    return self._toc.get("hoisted_page_id", None)

def set_hoisted_page(self, page_id):
    with self.notify("toc"):
        self._toc["hoisted_page_id"] = page_id
```

The collapsed pages are stored in `toc.collapsed`:

`rliterate.py / <<classes>> / <<Layout>> / <<__init__>>`:

```python
self._toc_collapsed = ensure_key(self._toc, "collapsed", [])
```

`rliterate.py / <<classes>> / <<Layout>>`:

```python
def is_collapsed(self, page_id):
    return page_id in self._toc_collapsed

def toggle_collapsed(self, page_id):
    with self.notify("toc"):
        if page_id in self._toc_collapsed:
            self._toc_collapsed.remove(page_id)
        else:
            self._toc_collapsed.append(page_id)
```

The scratch pages are stored in `workspace.scratch`:

`rliterate.py / <<classes>> / <<Layout>> / <<__init__>>`:

```python
self._workspace = ensure_key(self.data, "workspace", {})
self._workspace_scratch = ensure_key(self._workspace, "scratch", [])
```

`rliterate.py / <<classes>> / <<Layout>>`:

```python
def get_scratch_pages(self):
    return self._workspace_scratch[:]

def set_scratch_pages(self, page_ids):
    with self.notify("workspace"):
        self._workspace_scratch[:] = page_ids
```

Finally we have a utility function for ensuring that a specific key exists in a dictionary.

`rliterate.py / <<functions>>`:

```python
def ensure_key(a_dict, key, default):
    if key not in a_dict:
        a_dict[key] = default
    return a_dict[key]
```

#### Themes

Some parts of the application can be themed. Token types from pygments denote different things that can be styled.

`rliterate.py / <<classes>>`:

```python
class BaseTheme(object):

    def get_style(self, token_type):
        if token_type in self.styles:
            return self.styles[token_type]
        return self.get_style(token_type.parent)
```

`rliterate.py / <<base classes>>`:

```python
class Style(object):

    def __init__(self, color, bold=None):
        self.color = color
        self.color_rgb = tuple([
            int(x, 16)
            for x
            in (color[1:3], color[3:5], color[5:7])
        ])
        self.bold = bold

    def apply_to_wx_dc(self, dc, base_font):
        if self.bold:
            dc.SetFont(base_font.Bold())
        else:
            dc.SetFont(base_font)
        dc.SetTextForeground(self.color_rgb)
```

Here is a theme based on solarized. Mostly stolen from https://github.com/honza/solarized-pygments/blob/master/solarized.py.

`rliterate.py / <<classes>>`:

```python
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
    }
```

### Generating output

#### Code files

`rliterate.py / <<classes>>`:

```python
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
```

#### Markdown book

`rliterate.py / <<classes>>`:

```python
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
```

#### Textual diffing

This generates a file that is suitable for textual diffing.

`rliterate.py / <<classes>>`:

```python
class TextDiff(object):

    def __init__(self, path):
        self.listener = Listener(lambda event: self._generate())
        self.path = path

    def set_document(self, document):
        self.document = document
        self.listener.set_observable(self.document)

    def _generate(self):
        with open(self.path, "w") as f:
            self.pages = []
            self._collect_pages(self.document.get_page())
            self._render_pages(f)

    def _collect_pages(self, page):
        self.pages.append(page)
        for child in page.children:
            self._collect_pages(child)

    def _render_pages(self, f):
        for page in sorted(self.pages, key=lambda page: page.id):
            f.write(page.id)
            f.write(": ")
            f.write(page.title)
            f.write("\n\n")
            for paragraph in page.paragraphs:
                {
                    "text": self._render_text,
                    "code": self._render_code,
                }.get(paragraph.type, self._render_unknown)(f, paragraph)

    def _render_text(self, f, text):
        f.write(text.text+"\n\n")

    def _render_code(self, f, code):
        f.write("`"+" / ".join(code.path)+"`:\n\n")
        for line in code.text.splitlines():
            f.write("    "+line+"\n")
        f.write("\n\n")

    def _render_unknown(self, f, paragraph):
        f.write("Unknown type = "+paragraph.type+"\n\n")
```

### Publish subscribe mechanisms

`rliterate.py / <<base classes>>`:

```python
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
```

`rliterate.py / <<functions>>`:

```python
def is_prefix(left, right):
    return left == right[:len(left)]
```

`rliterate.py / <<classes>>`:

```python
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
```

### JSON serialization mechanisms

`rliterate.py / <<functions>>`:

```python
def load_json_from_file(path):
    with open(path, "r") as f:
        return json.load(f)
```

`rliterate.py / <<functions>>`:

```python
def write_json_to_file(path, data):
    with safely_write_file(path) as f:
        json.dump(
            data, f,
            sort_keys=True, indent=0, separators=(',', ':')
        )
```

This functions tries to write safely to a file. The file will either be completely written or not modified at all. It is achieved by first writing to a temporary file and then performing a rename.

`rliterate.py / <<functions>>`:

```python
@contextlib.contextmanager
def safely_write_file(path):
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(path),
        prefix=os.path.basename(path) + ".tmp",
        delete=False
    ) as tmp:
        yield tmp
    os.rename(tmp.name, path)
```

### Functions

`rliterate.py / <<functions>>`:

```python
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
```

`rliterate.py / <<functions>>`:

```python
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
```

### Main Python file

`rliterate.py`:

```python
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

import pygments.lexers
from pygments.token import Token
import wx
import wx.lib.newevent


<<constants>>
<<base classes>>
<<classes>>
<<functions>>


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame(filepath=sys.argv[1])
    main_frame.Show()
    app.MainLoop()
```

## Things I learned

DoDragDrop must be called from within an event handler.

Font must be assigned before setting a label, otherwise size calculations will be wrong? Must investigate further.

## TODO

Random notes of what I might want to work on in the future.

* Multiple editors can be opened (only last opened is saved)
* Factory should drop right into edit mode
* Highlighting of toc rows is not always up to date
* Invalid drop targets are still shown
    * Hide dragged item?
* Code editor
    * Tab indents with tab: should indent 4 spaces?
    * Shift+Tab deletes: should dedent
* Normalize paragraph when saving
    * Split into multiple paragraphs on more than one newline
    * Remove single newlines
    * Remove paragraph if text is empty
* Missing page operations
    * Add (before, after)
* Missing paragraph operations
    * Context menu with add paragraph before/after
* File generator writes empty filename
* There is no way to control empty lines from placeholders
* There is no list paragraph type
* Save button (in code editor) is very far down if there is lots of code and only top is edited
* Not possible to go to a page with Ctrl+T
* Highlight object being dragged somehow (screenshot?)
* Make each column scrollable (like Tweetdeck)
* Save when clicking outside text field (how to do this?)
* This is really a writing tool
    * Spell checking
* Final test: rewrite rlselect (or other program) using rliterate
    1. Import all source code as is
    2. Write narrative
    3. Ensure generated files are not changed
* Highlight active page in TOC
* Right click should only be generated on up if first down
* Workspace should not be wider that a column, that creates an unnecessary scrollbar
* Literate programming treats any target programming language as an assembly language
* TOC should only expand first 3(?) levels when opening a file for the first time
* Deleting root (even hoisted root) gives error
* Reading tool: Code can either be read in chunks or the final output. And you can follow links between them.
* Undo (use immutable data types (pyrsistent?))
* Diff two rliterate documents
* Search and replace
* Highlight placeholders in code fragments
* `word_split` should put white space in separate fragment and rich text display should have `skip_leading_space` option
* Export to stand-alone html for use in blog
* Drag and drop does not work om Mac (incorrect coordinate calculations?)
* Dynamic scripting
    * Show graph paragraph based on data paragraph defined earlier on the page (or on other page)


