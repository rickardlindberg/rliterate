# RLiterate

This is a tool for literal programming.

## Implementation

### Listener

`rliterate.py / <<classes>>`:

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


### Document

`rliterate.py / <<classes>>`:

    class Document(object):
    
        @classmethod
        def from_file(cls, path):
            return cls(path)
    
        def __init__(self, path):
            self.path = path
            self.listeners = []
            self._notify_count = 0
            self._load()
            self._cache()
    
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
            with open(self.path, "w") as f:
                json.dump(self.root_page, f)
    
        def _load(self):
            with open(self.path, "r") as f:
                self.root_page = json.load(f)
    
        # PUB/SUB
    
        def listen(self, fn):
            self.listeners.append(fn)
    
        def unlisten(self, fn):
            self.listeners.remove(fn)
    
        @contextlib.contextmanager
        def notify(self):
            self._notify_count += 1
            yield
            self._notify_count -= 1
            if self._notify_count == 0:
                for fn in self.listeners:
                    fn()
                self._save()
    
        # Queries
    
        def get_page(self, page_id=None):
            if page_id is None:
                page_id = self.root_page["id"]
            return DictPage(self._pages[page_id])
    
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
                DictParagraph(paragraph_dict)
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
    
        def __init__(self, paragraph_dict):
            self._paragraph_dict = paragraph_dict
    
        @property
        def id(self):
            return self._paragraph_dict["id"]
    
        @property
        def type(self):
            return self._paragraph_dict["type"]
    
        @property
        def text(self):
            return self._paragraph_dict["text"]
    
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
        def highlighted_code(self):
            try:
                lexer = pygments.lexers.get_lexer_for_filename(
                    self.filename,
                    stripnl=False
                )
            except:
                lexer = pygments.lexers.TextLexer(stripnl=False)
            return lexer.get_tokens(self.text)


### Generating output

#### Code files

`rliterate.py / <<classes>>`:

    class FileGenerator(object):
    
        def __init__(self):
            self.listener = Listener(self._generate)
    
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


#### Markdown book

`rliterate.py / <<classes>>`:

    class MarkdownGenerator(object):
    
        def __init__(self, path):
            self.listener = Listener(self._generate)
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
            for line in code.text.splitlines():
                f.write("    "+line+"\n")
            f.write("\n\n")
    
        def _render_unknown(self, f, paragraph):
            f.write("Unknown type = "+paragraph.type+"\n\n")


### Main frame

`rliterate.py / <<classes>>`:

    class MainFrame(wx.Frame):
    
        def __init__(self, filepath):
            wx.Frame.__init__(self, None)
            document = Document.from_file(filepath)
            FileGenerator().set_document(document)
            MarkdownGenerator(filepath+".markdown").set_document(document)
            workspace = Workspace(self, document)
            toc = TableOfContents(self, workspace, document)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(toc, flag=wx.EXPAND, proportion=0)
            sizer.Add(workspace, flag=wx.EXPAND, proportion=1)
            self.SetSizer(sizer)


### Table of contents

#### Main widget

`rliterate.py / <<classes>>`:

    class TableOfContents(wx.ScrolledWindow):
        <<TableOfContents>>


`rliterate.py / <<classes>> / <<TableOfContents>>`:

    def __init__(self, parent, workspace, document):
        wx.ScrolledWindow.__init__(self, parent, size=(300, -1))
        self.SetScrollRate(20, 20)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.listener = Listener(lambda: wx.CallAfter(self.Render))
        self.SetDocument(document)
        self.SetBackgroundColour((255, 255, 255))
        self.collapsed = set()
        self.workspace = workspace
        self.Bind(EVT_TREE_TOGGLE, self.OnTreeToggle)
        self.Bind(EVT_TREE_LEFT_CLICK, self.OnTreeLeftClick)
        self.Bind(EVT_TREE_RIGHT_CLICK, self.OnTreeRightClick)
        self.Bind(EVT_TREE_DOUBLE_CLICK, self.OnTreeDoubleClick)
        <<__init__>>
    
    def FindClosestDropPoint(self, screen_pos):
        client_pos = self.ScreenToClient(screen_pos)
        if self.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
            scroll_pos = (scroll_x, scroll_y) = self.CalcUnscrolledPosition(client_pos)
            y_distances = defaultdict(list)
            for drop_point in self.drop_points:
                y_distances[drop_point.y_distance_to(scroll_y)].append(drop_point)
            if y_distances:
                return min(
                    y_distances[min(y_distances.keys())],
                    key=lambda drop_point: drop_point.x_distance_to(scroll_x)
                )
    
    def OnTreeToggle(self, event):
        if event.page_id in self.collapsed:
            self.collapsed.remove(event.page_id)
        else:
            self.collapsed.add(event.page_id)
        self.Render()
    
    def OnTreeLeftClick(self, event):
        self.workspace.OpenScratch([event.page_id])
    
    def OnTreeRightClick(self, event):
        menu = PageContextMenu(self.document, event.page_id)
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnTreeDoubleClick(self, event):
        page_ids = [event.page_id]
        for child in self.document.get_page(event.page_id).children:
            page_ids.append(child.id)
        self.workspace.OpenScratch(page_ids)
    
    def SetDocument(self, document):
        self.document = document
        self.listener.set_observable(self.document)
    
    def Render(self):
        self.Freeze()
        self.drop_points = []
        self.sizer.Clear(True)
        self.add_page(self.document.get_page())
        self.Layout()
        self.Thaw()
    
    def add_page(self, page, indentation=0):
        is_collapsed = page.id in self.collapsed
        self.sizer.Add(
            TableOfContentsRow(self, indentation, page, is_collapsed),
            flag=wx.EXPAND
        )
        divider = Divider(self, padding=0, height=2)
        self.sizer.Add(
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
                divider = self.add_page(child, indentation+1)
                self.drop_points.append(TableOfContentsDropPoint(
                    divider=divider,
                    indentation=indentation+1,
                    parent_page_id=page.id,
                    before_page_id=None if next_child is None else next_child.id
                ))
        return divider


#### Row widget

`rliterate.py / <<classes>>`:

    class TableOfContentsRow(wx.Panel):
    
        BORDER = 2
        INDENTATION_SIZE = 16
    
        def __init__(self, parent, indentation, page, is_collapsed):
            wx.Panel.__init__(self, parent)
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer.Add((indentation*self.INDENTATION_SIZE, 1))
            if page.children:
                button = TableOfContentsButton(self, page.id, is_collapsed)
                self.sizer.Add(button, flag=wx.EXPAND|wx.LEFT, border=self.BORDER)
            else:
                self.sizer.Add((TableOfContentsButton.SIZE+1+self.BORDER, 1))
            text = wx.StaticText(self, label=page.title)
            self.sizer.Add(text, flag=wx.ALL, border=self.BORDER)
            self.SetSizer(self.sizer)
            self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
            self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
            for helper in [MouseEventHelper(self), MouseEventHelper(text)]:
                helper.OnClick = self.OnClick
                helper.OnRightClick = self.OnRightClick
                helper.OnDrag = self.OnDrag
                helper.OnDoubleClick = self.OnDoubleClick
            self.original_colour = self.Parent.GetBackgroundColour()
            self.page_id = page.id
    
        def OnClick(self):
            wx.PostEvent(self, TreeLeftClick(0, page_id=self.page_id))
    
        def OnRightClick(self):
            wx.PostEvent(self, TreeRightClick(0, page_id=self.page_id))
    
        def OnDoubleClick(self):
            wx.PostEvent(self, TreeDoubleClick(0, page_id=self.page_id))
    
        def OnDrag(self):
            data = RliterateDataObject("page", {
                "page_id": self.page_id,
            })
            drag_source = wx.DropSource(self)
            drag_source.SetData(data)
            result = drag_source.DoDragDrop(wx.Drag_DefaultMove)
    
        def OnEnterWindow(self, event):
            self.SetBackgroundColour((240, 240, 240))
    
        def OnLeaveWindow(self, event):
            self.SetBackgroundColour(self.original_colour)


#### Expand/Collapse widget

`rliterate.py / <<classes>>`:

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


#### Drop point

`rliterate.py / <<classes>>`:

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


#### Drop target

`rliterate.py / <<classes>>`:

    class TableOfContentsDropTarget(DropPointDropTarget):
    
        def __init__(self, toc):
            DropPointDropTarget.__init__(self, toc, "page")
            self.toc = toc
    
        def OnDataDropped(self, dropped_page, drop_point):
            self.toc.document.move_page(
                page_id=dropped_page["page_id"],
                parent_page_id=drop_point.parent_page_id,
                before_page_id=drop_point.before_page_id
            )


`rliterate.py / <<classes>> / <<TableOfContents>> / <<__init__>>`:

    self.SetDropTarget(TableOfContentsDropTarget(self))


#### Page context menu

`rliterate.py / <<classes>>`:

    class PageContextMenu(wx.Menu):
    
        def __init__(self, document, page_id):
            wx.Menu.__init__(self)
            self.document = document
            self.page_id = page_id
            self._create_menu()
    
        def _create_menu(self):
            self.Bind(
                wx.EVT_MENU,
                lambda event: self.document.add_page(parent_id=self.page_id),
                self.Append(wx.NewId(), "Add child")
            )
            self.AppendSeparator()
            self.Bind(
                wx.EVT_MENU,
                lambda event: self.document.delete_page(page_id=self.page_id),
                self.Append(wx.NewId(), "Delete")
            )


### Workspace

A workspace is a container for editable content. Most commonly pages.

#### Main widget

`rliterate.py / <<classes>>`:

    class Workspace(wx.ScrolledWindow):
        <<Workspace>>


`rliterate.py / <<classes>> / <<Workspace>>`:

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
        <<__init__>>
    
    def FindClosestDropPoint(self, screen_pos):
        return find_first(
            self.columns,
            lambda column: column.FindClosestDropPoint(screen_pos)
        )
    
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


#### Column widget

`rliterate.py / <<classes>>`:

    class Column(wx.Panel):
    
        def __init__(self, parent, document):
            wx.Panel.__init__(self, parent, size=(PAGE_BODY_WIDTH+2*PARAGRAPH_SPACE+SHADOW_SIZE, -1))
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.AddSpacer(PAGE_PADDING)
            self.SetSizer(self.sizer)
            self.document = document
            self.pages = []
    
        def FindClosestDropPoint(self, screen_pos):
            return find_first(
                self.pages,
                lambda page: page.FindClosestDropPoint(screen_pos)
            )
    
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


#### Drop target

`rliterate.py / <<classes>>`:

    class WorkspaceDropTarget(DropPointDropTarget):
    
        def __init__(self, workspace):
            DropPointDropTarget.__init__(self, workspace, "paragraph")
            self.workspace = workspace
    
        def OnDataDropped(self, dropped_paragraph, drop_point):
            self.workspace.document.move_paragraph(
                source_page=dropped_paragraph["page_id"],
                source_paragraph=dropped_paragraph["paragraph_id"],
                target_page=drop_point.page_id,
                before_paragraph=drop_point.next_paragraph_id
            )


`rliterate.py / <<classes>> / <<Workspace>> / <<__init__>>`:

    self.SetDropTarget(WorkspaceDropTarget(self))


### Pages

#### Page container

`rliterate.py / <<classes>>`:

    class PageContainer(wx.Panel):
    
        def __init__(self, parent, document, page_id):
            wx.Panel.__init__(self, parent)
            self.page_body = Page(self, document, page_id)
            self.SetBackgroundColour((150, 150, 150))
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.page_body, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=SHADOW_SIZE)
            self.SetSizer(self.sizer)
            self.Render()
    
        def FindClosestDropPoint(self, screen_pos):
            return self.page_body.FindClosestDropPoint(screen_pos)
    
        def Render(self):
            self.page_body.Render()


#### Page

`rliterate.py / <<classes>>`:

    class Page(wx.Panel):
    
        def __init__(self, parent, document, page_id):
            wx.Panel.__init__(self, parent)
            self.document = document
            self.page_id = page_id
            self.SetBackgroundColour(wx.WHITE)
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.sizer)
    
        def FindClosestDropPoint(self, screen_pos):
            client_pos = (client_x, client_y) = self.ScreenToClient(screen_pos)
            if self.HitTest(client_pos) == wx.HT_WINDOW_INSIDE:
                return min_or_none(
                    self.drop_points,
                    key=lambda drop_point: drop_point.y_distance_to(client_y)
                )
    
        def Render(self):
            self.drop_points = []
            page = self.document.get_page(self.page_id)
            self.sizer.Clear(True)
            self.sizer.AddSpacer(PARAGRAPH_SPACE)
            divider = self.AddParagraph(Title(self, self.document, page))
            for paragraph in page.paragraphs:
                self.drop_points.append(PageDropPoint(
                    divider=divider,
                    page_id=self.page_id,
                    next_paragraph_id=paragraph.id
                ))
                divider = self.AddParagraph({
                    "text": Paragraph,
                    "code": Code,
                    "factory": Factory,
                }[paragraph.type](self, self.document, self.page_id, paragraph))
            self.drop_points.append(PageDropPoint(
                divider=divider,
                page_id=self.page_id,
                next_paragraph_id=None
            ))
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
    
        def AddParagraph(self, paragraph):
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
            return divider


#### Title

`rliterate.py / <<classes>>`:

    class Title(Editable):
    
        def __init__(self, parent, document, page):
            self.document = document
            self.page = page
            Editable.__init__(self, parent)
    
        def CreateView(self):
            self.Font = create_font(size=16)
            view = wx.StaticText(
                self,
                label=self.page.title,
                style=wx.ST_ELLIPSIZE_END
            )
            view.SetToolTip(wx.ToolTip(self.page.title))
            return view
    
        def CreateEdit(self):
            edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=self.page.title)
            edit.Bind(wx.EVT_TEXT_ENTER, lambda _: self.EndEdit())
            return edit
    
        def EndEdit(self):
            self.document.edit_page(self.page.id, {"title": self.edit.Value})


#### Page drop point

`rliterate.py / <<classes>>`:

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


### Paragraphs

#### Text

##### Paragraph

`rliterate.py / <<classes>>`:

    class Paragraph(ParagraphBase, Editable):
    
        def __init__(self, parent, document, page_id, paragraph):
            ParagraphBase.__init__(self, document, page_id, paragraph)
            Editable.__init__(self, parent)
    
        def CreateView(self):
            view = wx.StaticText(self, label=self.paragraph.text)
            view.Wrap(PAGE_BODY_WIDTH)
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
            self.document.edit_paragraph(self.paragraph.id, {"text": self.edit.Value})


#### Code

##### Container widget

`rliterate.py / <<classes>>`:

    class Code(ParagraphBase, Editable):
    
        def __init__(self, parent, document, page_id, paragraph):
            ParagraphBase.__init__(self, document, page_id, paragraph)
            Editable.__init__(self, parent)
    
        def CreateView(self):
            return CodeView(self, self.paragraph)
    
        def CreateEdit(self):
            return CodeEditor(self, self.view, self.paragraph)
    
        def EndEdit(self):
            self.document.edit_paragraph(self.paragraph.id, {
                "path": self.edit.path.Value.split(" / "),
                "text": self.edit.text.Value,
            })


##### View widget

`rliterate.py / <<classes>>`:

    class CodeView(wx.Panel):
    
        BORDER = 1
        PADDING = 5
    
        def __init__(self, parent, code_paragraph):
            wx.Panel.__init__(self, parent)
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
            text = wx.StaticText(panel, label=" / ".join(code_paragraph.path))
            text.Font = text.Font.Bold()
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
            body = CodeBody(panel, code_paragraph)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(body, flag=wx.ALL|wx.EXPAND, border=self.PADDING, proportion=1)
            panel.SetSizer(sizer)
            MouseEventHelper.bind(
                [panel, body]+body.children,
                double_click=self._post_paragraph_edit_start,
                drag=self.Parent.DoDragDrop,
                right_click=self.Parent.ShowContextMenu
            )
            return panel
    
        def _post_paragraph_edit_start(self):
            wx.PostEvent(self, ParagraphEditStart(0))
    
    
    class CodeBody(wx.ScrolledWindow):
    
        def __init__(self, parent, paragraph):
            wx.ScrolledWindow.__init__(self, parent)
            self.children = []
            sizer = wx.BoxSizer(wx.VERTICAL)
            self._add_lines(sizer, paragraph)
            self.SetSizer(sizer)
            self.SetMinSize((-1, sizer.GetMinSize()[1]))
            self.SetScrollRate(20, 20)
    
        def _add_lines(self, sizer, paragraph):
            for markup in self._split(paragraph):
                text = wx.StaticText(self, label="")
                text.SetLabelMarkup(markup)
                sizer.Add(text)
                self.children.append(text)
    
        def _split(self, paragraph):
            markup_lines = []
            for line in self._split_tokens(paragraph):
                markup_lines.append("".join([
                    "<span color='{}'>{}</span>".format(
                        self._color(token_type),
                        xml.sax.saxutils.escape(text)
                    )
                    for token_type, text in line
                ]))
            return markup_lines
    
        def _split_tokens(self, paragraph):
            lines = []
            line = []
            for token_type, text in paragraph.highlighted_code:
                parts = text.split("\n")
                line.append((token_type, parts.pop(0)))
                while parts:
                    lines.append(line)
                    line = []
                    line.append((token_type, parts.pop(0)))
            if line:
                lines.append(line)
            if lines and lines[-1] and len(lines[-1]) == 1 and len(lines[-1][0][1]) == 0:
                lines.pop(-1)
            return lines
    
        def _color(self, token_type):
            # Parts stolen from https://github.com/honza/solarized-pygments/blob/master/solarized.py
            base00  = '#657b83'
            base01  = '#586e75'
            base0   = '#839496'
            base1   = '#93a1a1'
            yellow  = '#b58900'
            orange  = '#cb4b16'
            red     = '#dc322f'
            violet  = '#6c71c4'
            blue    = '#268bd2'
            cyan    = '#2aa198'
            green   = '#859900'
            if token_type is pygments.token.Keyword:
                return green
            elif token_type is pygments.token.Keyword.Constant:
                return cyan
            elif token_type is pygments.token.Keyword.Declaration:
                return blue
            elif token_type is pygments.token.Keyword.Namespace:
                return orange
            elif token_type is pygments.token.Name.Builtin:
                return red
            elif token_type is pygments.token.Name.Builtin.Pseudo:
                return blue
            elif token_type is pygments.token.Name.Class:
                return blue
            elif token_type is pygments.token.Name.Decorator:
                return blue
            elif token_type is pygments.token.Name.Entity:
                return violet
            elif token_type is pygments.token.Name.Exception:
                return yellow
            elif token_type is pygments.token.Name.Function:
                return blue
            elif token_type is pygments.token.String:
                return cyan
            elif token_type is pygments.token.Number:
                return cyan
            elif token_type is pygments.token.Operator.Word:
                return green
            elif token_type is pygments.token.Comment:
                return base01
            else:
                return base00


##### Editor widget

`rliterate.py / <<classes>>`:

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


#### Factory

`rliterate.py / <<classes>>`:

    class Factory(ParagraphBase, wx.Panel):
    
        def __init__(self, parent, document, page_id, paragraph):
            ParagraphBase.__init__(self, document, page_id, paragraph)
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
            self.document.edit_paragraph(self.paragraph.id, {"type": "text", "text": "Enter text here..."})
    
        def OnCodeButton(self, event):
            self.document.edit_paragraph(self.paragraph.id, {"type": "code", "path": [], "text": "Enter code here..."})


#### Common

##### Paragraph base

`rliterate.py / <<base classes>>`:

    class ParagraphBase(object):
    
        def __init__(self, document, page_id, paragraph):
            self.document = document
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
                self.document, self.page_id, self.paragraph
            )
            self.PopupMenu(menu)
            menu.Destroy()


##### Paragraph context menu

`rliterate.py / <<classes>>`:

    class ParagraphContextMenu(wx.Menu):
    
        def __init__(self, document, page_id, paragraph):
            wx.Menu.__init__(self)
            self.document = document
            self.page_id = page_id
            self.paragraph = paragraph
            self._create_menu()
    
        def _create_menu(self):
            self.Bind(
                wx.EVT_MENU,
                lambda event: self.document.delete_paragraph(
                    page_id=self.page_id,
                    paragraph_id=self.paragraph.id
                ),
                self.Append(wx.NewId(), "Delete")
            )
            self.Bind(
                wx.EVT_MENU,
                lambda event: self.document.edit_paragraph(
                    self.paragraph.id,
                    {"text": edit_in_gvim(self.paragraph.text, self.paragraph.filename)}
                ),
                self.Append(wx.NewId(), "Edit in gvim")
            )


##### Editable

`rliterate.py / <<base classes>>`:

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


### Generic drag & drop

#### RLiterate data object

`rliterate.py / <<classes>>`:

    class RliterateDataObject(wx.CustomDataObject):
    
        def __init__(self, kind, json=None):
            wx.CustomDataObject.__init__(self, "rliterate/{}".format(kind))
            if json is not None:
                self.set_json(json)
    
        def set_json(self, data):
            self.SetData(json.dumps(data))
    
        def get_json(self):
            return json.loads(self.GetData())


#### Drop point drop target

A drop target that can work with windows that supports FindClosestDropPoint.

`rliterate.py / <<base classes>>`:

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


#### Divider

`rliterate.py / <<classes>>`:

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


### wxPython utilities

#### Mouse event helper

`rliterate.py / <<classes>>`:

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


### Constants

`rliterate.py / <<constants>>`:

    PAGE_BODY_WIDTH = 800
    PAGE_PADDING = 12
    SHADOW_SIZE = 2
    PARAGRAPH_SPACE = 15
    
    
    TreeToggle, EVT_TREE_TOGGLE = wx.lib.newevent.NewCommandEvent()
    TreeLeftClick, EVT_TREE_LEFT_CLICK = wx.lib.newevent.NewCommandEvent()
    TreeRightClick, EVT_TREE_RIGHT_CLICK = wx.lib.newevent.NewCommandEvent()
    TreeDoubleClick, EVT_TREE_DOUBLE_CLICK = wx.lib.newevent.NewCommandEvent()
    ParagraphEditStart, EVT_PARAGRAPH_EDIT_START = wx.lib.newevent.NewCommandEvent()
    ParagraphEditEnd, EVT_PARAGRAPH_EDIT_END = wx.lib.newevent.NewCommandEvent()


### Functions

`rliterate.py / <<functions>>`:

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


`rliterate.py / <<functions>>`:

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


### Main Python file

`rliterate.py`:

    import contextlib
    import json
    import uuid
    from collections import defaultdict
    import os
    import re
    import sys
    import tempfile
    import subprocess
    import xml.sax.saxutils
    import time
    
    import wx
    import wx.lib.newevent
    import pygments.lexers
    import pygments.token
    
    
    <<constants>>
    <<base classes>>
    <<classes>>
    <<functions>>
    
    
    if __name__ == "__main__":
        app = wx.App()
        main_frame = MainFrame(filepath=sys.argv[1])
        main_frame.Show()
        app.MainLoop()


## Notes

### Problems

* Multiple editors can be opened (only last opened is saved)
* Factory should drop right into edit mode
* Highlighting of toc rows is not always up to date
* Invalid drop targets are still shown
    * Hide dragged item?
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
* Deleted pages are not removed from workspace
* Syntax highlight code with pygments
* File generator writes empty filename
* There is no way to control empy lines from placeholders
* There is no list paragraph type
* During conversion
    * Save button is very far down if there is lots of code and only top is edited
    * Can't focus in on specific subtree of toc (hoist, unhoist?)

### Ideas

* Highlight object being dragged somehow
* Only expose custom classes from Document (Page, Paragraph, ...)
* Make each column scrollable (like Tweetdeck)
* Save when clicking outside text field (how to do this?)
* This is really a writing tool
    * Spell checking
* Final test: rewrite rlselect using rliterate
    1. Import all source code as is
    2. Write narrative
    3. Ensure generated files are not changed
* Highlight active page in TOC

### Inspiration

* https://www.youtube.com/watch?v=Av0PQDVTP4A
  Literate Programming in the Large - Timothy Daly - (Axiom/Literat clojure)
  Change the mindset from wring a program to writing a book

* https://www.youtube.com/watch?v=5V1ynVyud4M
  "Eve" by Chris Granger

* http://eve-lang.com/deepdives/literate.html

* Add factory button is stolen from fedrated wiki

* ProjecturED
  http://projectured.org/

### Things I learned

DoDragDrop must be called from within an event handler.

Font must be assigned before setting a label, otherwise size calculations will be wrong? Must investigate further.

