<h1>RLiterate</h1>

<p>RLiterate is a tool for reading and authoring documents. Documents have pages organized in a hierarchy. Pages have a title and paragraphs. Paragraphs can be of different types. The different paragraph types is what makes RLiterate documents special. Code paragraphs for example enable literate programming by allowing chunks of code to be defined and then be automatically assembled into the final source file. Text paragraphs are used for writing prose. RLiterate documents can also be exported to different formats for display in different mediums.
</p>

<ul><li><a href="#600aa145cf474a6aa732a4c4edb5f44b">A tour of RLiterate<ul><li><a href="#7f14d9ec23c0425c89039ea68dfdac16">Main GUI<ul></ul></a></li><li><a href="#3ad55f274f724ebab8cea5d5c63d8dc0">Reading tool<ul></ul></a></li><li><a href="#6c34776183394824824be039e65de531">Literate programming<ul></ul></a></li></ul></a></li><li><a href="#95150c4f0d92428bbeef4ae5a865398d">Background<ul><li><a href="#9b46f6326dda497fabbc1ef7f5247422">The prototype<ul></ul></a></li><li><a href="#f496615acbe44223a64e1db1fc154b12">Why literate programming?<ul></ul></a></li><li><a href="#e836cd0edf4a4b66ab8dd1e5d7fbbea3">Similar tools<ul></ul></a></li></ul></a></li><li><a href="#4d689acb540d40ecb8b828701bb5bf74">Implementation<ul><li><a href="#e418766e480b41b1844c8d754b3746fc">GUI wxPython<ul><li><a href="#8ab608f28a5046548963649371cab5fe">Main frame</a></li><li><a href="#c456e147b7b745ed80697c4faeb02bcb">Table of contents</a></li><li><a href="#4dd60465575c4297a25813f0478f15f9">Workspace</a></li><li><a href="#a6e8ca0aa83d4829b15c0424be259022">Drag &amp; drop</a></li><li><a href="#5c3647a616b8495f8bebd268be84377d">wxPython utilities</a></li><li><a href="#4495f053ab2d41a2a4ec70f55e929b9f">Constants</a></li></ul></a></li><li><a href="#b376363cbd664a838d3bafb7bfae2281">Project<ul><li><a href="#276ff8047f7e46dea723c1822078ac26">Document model</a></li><li><a href="#f7f16199492c4bad80567c3a960b8bc9">Layouts</a></li><li><a href="#192db0d4b96e4162b3cf19f870ee287d">Themes</a></li></ul></a></li><li><a href="#63ff2f7abea44406922c78b7683e2dd3">Generating output<ul><li><a href="#56b835fee5b24f8a8e59156506ac6464">Code files</a></li><li><a href="#1b021eaa54da4d0282e9cbcd8b875f79">Markdown book</a></li><li><a href="#162d5b5c668d4c958c88b7d37e6f5d3e">HTML</a></li><li><a href="#427cb0d170a04b9898b5b744cd15b263">Textual diffing</a></li></ul></a></li><li><a href="#01aa28a581e84f088104c6cd600d9c1d">Publish subscribe mechanisms<ul></ul></a></li><li><a href="#b73b797520334653a235e5e6a077e573">JSON serialization mechanisms<ul></ul></a></li><li><a href="#fddc930e6caa4a38bf6e7259e6e1034a">Functions<ul></ul></a></li><li><a href="#745dcf0d093a4f179dc7fbe1dc8b7bdd">Main Python file<ul></ul></a></li></ul></a></li><li><a href="#cc36000ed12f4bfe88cefa2987fdb5cd">Things I learned<ul></ul></a></li><li><a href="#0a165f3042ee4350b9bebb61213b44c5">TODO<ul></ul></a></li></ul><h2><a name="600aa145cf474a6aa732a4c4edb5f44b"></a>

A tour of RLiterate</h2>

<p>This chapter gives an overview what RLiterate looks like.</p>

<h3><a name="7f14d9ec23c0425c89039ea68dfdac16"></a>

Main GUI</h3>

<p>* smallest federated wiki inspired the factory and the editing workflow
* leo and smallest federated wiki inspired TOC and seeing a single page/node at a time</p>

<h3><a name="3ad55f274f724ebab8cea5d5c63d8dc0"></a>

Reading tool</h3>

<p>RLiterate is a reading and thinking tool. The following features support that.</p>

<p>Hoisting a page in the table of contents allows you to <strong>focus on a subset</strong> of the document.</p>

<p>Openining a page and all immediate children (double click on a page in the table of contents) allows you to read a subset of the document <strong>breath first</strong>. It's like reading only the first paragraph in an entire book.</p>

<h3><a name="6c34776183394824824be039e65de531"></a>

Literate programming</h3>

<p>Describe how code paragraphs enable literate programming.</p>

<h2><a name="95150c4f0d92428bbeef4ae5a865398d"></a>

Background</h2>

<p>Many things inspired RLiterate, but the initial thought was triggered by the paper <a href="http://www.vpri.org/pdf/tr2009002_active_essays.pdf">Active Essays on the Web</a>. In it they talk about embedding code in documents that the reader can interact with. They also mention <a href="https://en.wikipedia.org/wiki/Literate_programming">Literate programming</a> as having a related goal.</p>

<p>At the time I was working on a program that I thought would be nice to express in this way. I wanted to write an article about the program and have the code for the program embedded in the article. I could have used a literate programming tool for this, but the interactive aspect of active essays made me think that a tool would be much more powerful if the document could be edited "live", similar to WYSIWYG editors. Literate programming tools I were aware of worked by editing plain text files with a special syntax for code and documentation blocks, thus lacking the interactive aspect.</p>

<h3><a name="9b46f6326dda497fabbc1ef7f5247422"></a>

The prototype</h3>

<p>So I decided to build a prototype to learn what such a tool might be like.
</p>

<p>First I came up with a document model where pages were organized in a hierarchy and where each page had paragraphs that could be of different types. This idea was stolen from <a href="https://en.wikipedia.org/wiki/Smallest_Federated_Wiki">Smallest Federated Wiki</a>. The code paragraph would allow for literate programming. I also envisioned other paragraph types that would allow for more interaction. Perhaps one paragraph type could be <a href="http://graphviz.org/">Graphviz</a> code, and when edited, a generated graph would appear instead of the code.</p>

<p>After coming up with a document model, I implement a GUI that would allow editing such documents. This GUI had to be first class as it would be the primary way to read and author documents.</p>

<p>At a certain point I had all the functionality in place for doing literate programming. Then I imported all the code into an RLiterate document (previously it was written as a single Python file) and started extracting pieces and adding prose to explain the program. As I went along I noticed features I was lacking.</p>

<h3><a name="f496615acbe44223a64e1db1fc154b12"></a>

Why literate programming?</h3>

<p>To me, the most central idea in literate programming is that we should write programs for other humans. Only secondary for the machine. I find code easier to understand if I can understand it in isolated pieces. One example where it is difficult to isolate a piece without literate programming is test code. Usually the test code is located in one file, and the implementation in another. To fully understand the piece it is useful to both read the tests and the implementation. To do this we have to find this related information in two unrelated files. I wrote about this problem in 2003 in <a href="http://rickardlindberg.me/writing/reflections-on-programming/2013-02-24-related-things-are-not-kept-together/">Related things are not kept together</a>. Literate programming allows us to present the test and the implementation in the same place, yet have the different pieces written to different files. The compiler might require that they are in separate files, but with literate programming, we care first about the other human that will read our code, and only second about the compiler.</p>

<p>Another argument for literate programming is to express the "why". Why is this code here? Timothy Daly talks about it in his talk <a href="https://www.youtube.com/watch?v=Av0PQDVTP4A">Literate Programming in the Large</a>. He also argues that programmers must change the mindset from wring a program to writing a book. Some more can be read here: http://axiom-developer.org/axiom-website/litprog.html.</p>

<p>Some more resources about literate programming:

* https://www.youtube.com/watch?v=5V1ynVyud4M
  "Eve" by Chris Granger

* http://eve-lang.com/deepdives/literate.html

* https://software-carpentry.org/blog/2011/03/literate-programming.html</p>

<h3><a name="e836cd0edf4a4b66ab8dd1e5d7fbbea3"></a>

Similar tools</h3>

<p>I stumbled across <a href="http://projectured.org/">ProjecturED</a>. It is similar to RLiterate in the sense that it is an editor for richer documents. Not just text. The most interesting aspect for me is that a variable name exists in one place, but can be rendered in multiple. So a rename is really simple. With RLiterate, you have to do a search and replace. But with ProjecturED you just change the name and it replicates everywhere. This is an attractive feature and is made possible by the different document model. Probably RLiterate can never support that because a completely different approach needs to be taken, but it is an interesting project to investigate further.
</p>

<h2><a name="4d689acb540d40ecb8b828701bb5bf74"></a>

Implementation</h2>

<p>RLiterate is implemented in Python. This chapter gives a complete description of all the code.</p>

<h3><a name="e418766e480b41b1844c8d754b3746fc"></a>

GUI wxPython</h3>

<p>The main GUI is written in wxPython.</p>

<h4><a name="8ab608f28a5046548963649371cab5fe"></a>

Main frame</h4>

<p>The main frame lays out two widgets horizontally: the table of contents and the workspace. It also creates the project from the specified file path.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">MainFrame</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Frame</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">filepath</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Frame</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Project</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">workspace</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Workspace</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">toc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">TableOfContents</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">toc</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">workspace</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizerAndFit</span><span class="p">(</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="c456e147b7b745ed80697c4faeb02bcb"></a>

Table of contents</h4>

<p>The table of contents shows the outline of the document. It allows only subtrees to be shown (hoisting) and allows subtrees to be expanded/collapsed. It also provides navigation functions to allow pages to be opened.</p>

<h5>Main widget</h5>

<p>The main table of contents widget listens for changes to a project (only events related to changes in the document and the layout of the table of contents) and then re-renders itself.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TableOfContents</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">TableOfContents</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="p">(</span><span class="mi">250</span><span class="p">,</span><span class=""> </span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project_listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render_from_event</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="s2">"</span><span class="s2">document</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">layout.toc</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetProject</span><span class="p">(</span><span class="n">project</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="fm">__init__</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">SetProject</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project_listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">)</span><span class="">
</span></pre></div>

<p>This seems to be needed for some reason:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_re_render_from_event</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">wx</span><span class="o">.</span><span class="n">CallAfter</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Rendering</h6>

<p>The table of contents widget lays out two components in a vertical container: the unhoist button and the page container.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_re_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Clear</span><span class="p">(</span><span class="bp">True</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_unhoist_button</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_page_container</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">Layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<p>The unhoist button (only shown if a page has been hoisted):</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_render_unhoist_button</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_hoisted_page</span><span class="p">(</span><span class="p">)</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Button</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">label</span><span class="o">=</span><span class="s2">"</span><span class="s2">unhoist</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">button</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_BUTTON</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">set_hoisted_page</span><span class="p">(</span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">button</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">)</span><span class="">
</span></pre></div>

<p>The page container is a scrolling container that contains a set of rows representing pages. Each row is appropriately intendent to create the illusion of a tree.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_render_page_container</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">page_sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">CompactScrolledWindow</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_sizer</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_hoisted_page</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_render_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">indentation</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">is_collapsed</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">is_collapsed</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">page_sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">TableOfContentsRow</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">indentation</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Divider</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="p">,</span><span class=""> </span><span class="n">padding</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="n">height</span><span class="o">=</span><span class="mi">2</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">page_sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="n">is_collapsed</span><span class=""> </span><span class="ow">or</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">)</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">before_page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">    </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">before_page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="o">.</span><span class="n">id</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">TableOfContentsDropPoint</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">divider</span><span class="o">=</span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">indentation</span><span class="o">=</span><span class="n">indentation</span><span class="o">+</span><span class="mi">1</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">parent_page_id</span><span class="o">=</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">before_page_id</span><span class="o">=</span><span class="n">before_page_id</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="n">is_collapsed</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class="p">,</span><span class=""> </span><span class="n">next_child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">pairs</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_page</span><span class="p">(</span><span class="n">child</span><span class="p">,</span><span class=""> </span><span class="n">indentation</span><span class="o">+</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">TableOfContentsDropPoint</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">divider</span><span class="o">=</span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">indentation</span><span class="o">=</span><span class="n">indentation</span><span class="o">+</span><span class="mi">1</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">parent_page_id</span><span class="o">=</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">before_page_id</span><span class="o">=</span><span class="bp">None</span><span class=""> </span><span class="k">if</span><span class=""> </span><span class="n">next_child</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class=""> </span><span class="k">else</span><span class=""> </span><span class="n">next_child</span><span class="o">.</span><span class="n">id</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">divider</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TableOfContentsDropPoint</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">divider</span><span class="p">,</span><span class=""> </span><span class="n">indentation</span><span class="p">,</span><span class=""> </span><span class="n">parent_page_id</span><span class="p">,</span><span class=""> </span><span class="n">before_page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">divider</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">indentation</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">indentation</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">parent_page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">parent_page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">before_page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">before_page_id</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">x_distance_to</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">left_padding</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">TableOfContentsButton</span><span class="o">.</span><span class="n">SIZE</span><span class="o">+</span><span class="mi">1</span><span class="o">+</span><span class="n">TableOfContentsRow</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="n">span_x_center</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">left_padding</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="n">TableOfContentsRow</span><span class="o">.</span><span class="n">INDENTATION_SIZE</span><span class=""> </span><span class="o">*</span><span class=""> </span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">indentation</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="mf">1.5</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="nb">abs</span><span class="p">(</span><span class="n">span_x_center</span><span class=""> </span><span class="o">-</span><span class=""> </span><span class="n">x</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">y_distance_to</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="nb">abs</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Position</span><span class="o">.</span><span class="n">y</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Size</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="o">/</span><span class="mi">2</span><span class=""> </span><span class="o">-</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Show</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Show</span><span class="p">(</span><span class="nb">sum</span><span class="p">(</span><span class="p">[</span><span class="">
</span><span class="">            </span><span class="n">TableOfContentsRow</span><span class="o">.</span><span class="n">BORDER</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">TableOfContentsButton</span><span class="o">.</span><span class="n">SIZE</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="mi">1</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">indentation</span><span class="o">*</span><span class="n">TableOfContentsRow</span><span class="o">.</span><span class="n">INDENTATION_SIZE</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">]</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Hide</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Dropping pages</h6>

<p>Inside the table of contents, pages can be dragged and drop. The drag is initiated in the row widget and handled in the table of contents widget.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">SetDropTarget</span><span class="p">(</span><span class="n">TableOfContentsDropTarget</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TableOfContentsDropTarget</span><span class="p">(</span><span class="n">DropPointDropTarget</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">toc</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">DropPointDropTarget</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">toc</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">page</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnDataDropped</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">dropped_page</span><span class="p">,</span><span class=""> </span><span class="n">drop_point</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">move_page</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">page_id</span><span class="o">=</span><span class="n">dropped_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">page_id</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">parent_page_id</span><span class="o">=</span><span class="n">drop_point</span><span class="o">.</span><span class="n">parent_page_id</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">before_page_id</span><span class="o">=</span><span class="n">drop_point</span><span class="o">.</span><span class="n">before_page_id</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<p>The DropPointDropTarget requires FindClosestDropPoint to be defined on the target object. Here it is:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContents&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">FindClosestDropPoint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">screen_pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">client_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="o">.</span><span class="n">ScreenToClient</span><span class="p">(</span><span class="n">screen_pos</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="o">.</span><span class="n">HitTest</span><span class="p">(</span><span class="n">client_pos</span><span class="p">)</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">HT_WINDOW_INSIDE</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">scroll_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">(</span><span class="n">scroll_x</span><span class="p">,</span><span class=""> </span><span class="n">scroll_y</span><span class="p">)</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_container</span><span class="o">.</span><span class="n">CalcUnscrolledPosition</span><span class="p">(</span><span class="n">client_pos</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">y_distances</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">drop_point</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">y_distances</span><span class="p">[</span><span class="n">drop_point</span><span class="o">.</span><span class="n">y_distance_to</span><span class="p">(</span><span class="n">scroll_y</span><span class="p">)</span><span class="p">]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">drop_point</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">y_distances</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="nb">min</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">y_distances</span><span class="p">[</span><span class="nb">min</span><span class="p">(</span><span class="n">y_distances</span><span class="o">.</span><span class="n">keys</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">key</span><span class="o">=</span><span class="k">lambda</span><span class=""> </span><span class="n">drop_point</span><span class="p">:</span><span class=""> </span><span class="n">drop_point</span><span class="o">.</span><span class="n">x_distance_to</span><span class="p">(</span><span class="n">scroll_x</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Row widget</h5>

<p>The row widget renders the page title at the appropriate indentation. If the page has children, an expand/collapse widget is also rendered to the left of the title.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TableOfContentsRow</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">indentation</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">indentation</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">indentation</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">TableOfContentsRow</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p>Rendering lays out expand/collapse button (if the page has children) and the page title in a horizontal sizer:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContentsRow&gt;&gt;</code></p>

<div class="highlight"><pre><span class="n">BORDER</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">2</span><span class="">
</span><span class="n">INDENTATION_SIZE</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">16</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">indentation</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">INDENTATION_SIZE</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">TableOfContentsButton</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">button</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">LEFT</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="p">(</span><span class="n">TableOfContentsButton</span><span class="o">.</span><span class="n">SIZE</span><span class="o">+</span><span class="mi">1</span><span class="o">+</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">StaticText</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">text</span><span class="o">.</span><span class="n">SetLabelText</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_ENTER_WINDOW</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_enter_window</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEAVE_WINDOW</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_leave_window</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">helper</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="p">[</span><span class="n">MouseEventHelper</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">MouseEventHelper</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="p">]</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">helper</span><span class="o">.</span><span class="n">OnClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_click</span><span class="">
</span><span class="">        </span><span class="n">helper</span><span class="o">.</span><span class="n">OnDoubleClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_double_click</span><span class="">
</span><span class="">        </span><span class="n">helper</span><span class="o">.</span><span class="n">OnRightClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_right_click</span><span class="">
</span><span class="">        </span><span class="n">helper</span><span class="o">.</span><span class="n">OnDrag</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_drag</span><span class="">
</span></pre></div>

<p>Event handlers:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;TableOfContentsRow&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_on_click</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_double_click</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">page_ids</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">page_ids</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">child</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="n">page_ids</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_right_click</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">menu</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">PageContextMenu</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">PopupMenu</span><span class="p">(</span><span class="n">menu</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">menu</span><span class="o">.</span><span class="n">Destroy</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_drag</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">data</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RliterateDataObject</span><span class="p">(</span><span class="s2">"</span><span class="s2">page</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">        </span><span class="s2">"</span><span class="s2">page_id</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class="">
</span><span class="">    </span><span class="p">}</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">drag_source</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">DropSource</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">drag_source</span><span class="o">.</span><span class="n">SetData</span><span class="p">(</span><span class="n">data</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">result</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">drag_source</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Drag_DefaultMove</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_enter_window</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">240</span><span class="p">,</span><span class=""> </span><span class="mi">240</span><span class="p">,</span><span class=""> </span><span class="mi">240</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_leave_window</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Expand/Collapse widget</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TableOfContentsButton</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">SIZE</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">16</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">SIZE</span><span class="o">+</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_PAINT</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnPaint</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEFT_DOWN</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnLeftDown</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetCursor</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">StockCursor</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">CURSOR_HAND</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnLeftDown</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">toggle_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnPaint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">dc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">GCDC</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">PaintDC</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">dc</span><span class="o">.</span><span class="n">SetBrush</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">BLACK_BRUSH</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">render</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">RendererNative</span><span class="o">.</span><span class="n">Get</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">(</span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class="p">)</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">Size</span><span class="">
</span><span class="">        </span><span class="n">render</span><span class="o">.</span><span class="n">DrawTreeItemButton</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">dc</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="p">(</span><span class="n">h</span><span class="o">-</span><span class="bp">self</span><span class="o">.</span><span class="n">SIZE</span><span class="p">)</span><span class="o">/</span><span class="mi">2</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">SIZE</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">SIZE</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flags</span><span class="o">=</span><span class="mi">0</span><span class=""> </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">is_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class=""> </span><span class="k">else</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">CONTROL_EXPANDED</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Page context menu</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">PageContextMenu</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Menu</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Menu</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">child_ids</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">]</span><span class="o">+</span><span class="p">[</span><span class="n">child</span><span class="o">.</span><span class="n">id</span><span class=""> </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_menu</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_menu</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Open</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">]</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Open append</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">child_ids</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Open with children</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">child_ids</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Open with children append</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">AppendSeparator</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">add_page</span><span class="p">(</span><span class="n">parent_id</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Add child</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">AppendSeparator</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">set_hoisted_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Hoist</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">AppendSeparator</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">delete_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Delete</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="4dd60465575c4297a25813f0478f15f9"></a>

Workspace</h4>

<p>The workspace shows pages in the document. It is organized in columns, and each column can show multiple pages. The pages can also be edited from the workspace.</p>

<h5>Main widget</h5>

<p>The main workspace widget is a horizontal scrolling container containing column widgets.</p>

<p>The workspace is re-rendered whenever relevant parts of the project changes.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Workspace</span><span class="p">(</span><span class="n">CompactScrolledWindow</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">Workspace</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Workspace&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">CompactScrolledWindow</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">HSCROLL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project_listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render_from_event</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="s2">"</span><span class="s2">document</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="s2">"</span><span class="s2">layout.workspace</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetProject</span><span class="p">(</span><span class="n">project</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="fm">__init__</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">SetProject</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project_listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Rendering</h6>

<p>Rendering a workspace means laying out a set of column widgets horizontally. Columns are filled with page containers.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Workspace&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">200</span><span class="p">,</span><span class=""> </span><span class="mi">200</span><span class="p">,</span><span class=""> </span><span class="mi">200</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">AddSpacer</span><span class="p">(</span><span class="n">PAGE_PADDING</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_re_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_ensure_num_columns</span><span class="p">(</span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">columns</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">index</span><span class="p">,</span><span class=""> </span><span class="n">page_ids</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="nb">enumerate</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">columns</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="p">[</span><span class="n">index</span><span class="p">]</span><span class="o">.</span><span class="n">SetPages</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_ids</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">Parent</span><span class="o">.</span><span class="n">Layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_ensure_num_columns</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">num</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">while</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="p">)</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="n">num</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="o">.</span><span class="n">Destroy</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">while</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="p">)</span><span class=""> </span><span class="o">&lt;</span><span class=""> </span><span class="n">num</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_add_column</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_add_column</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">column</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Column</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">column</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">column</span><span class="">
</span></pre></div>

<p>`Layout` is called on the parent. Otherwise scrollbars don't seem to update appropriately.</p>

<p>On removing widgets <a href="https://stackoverflow.com/a/41064558">Removing a widget from its wxPython parent</a>:</p>

<p>Widgets will remove themselves from the sizer when they are destroyed, so yes, it is redundant. Also, widgets will remove themselves from the parent's child list, so calling RemoveChild is also redundant. IOW, the call to window.Destroy() will be sufficient to remove the widget and its resources, and to do the necessary clean-ups in the parent and the sizer.</p>

<p>wx.CallAfter seems to be needed to correctly update scrollbars on an event notification. Resizing the window also works.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Workspace&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_re_render_from_event</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">wx</span><span class="o">.</span><span class="n">CallAfter</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_re_render</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Dropping paragraphs</h6>

<p>Inside a workspace, paragraphs can be dragged and dropped. The drag is handled in the paragraph widget, but the drop is handled in the workspace widget.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Workspace&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">SetDropTarget</span><span class="p">(</span><span class="n">WorkspaceDropTarget</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">WorkspaceDropTarget</span><span class="p">(</span><span class="n">DropPointDropTarget</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">workspace</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">DropPointDropTarget</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">workspace</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">paragraph</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnDataDropped</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">dropped_paragraph</span><span class="p">,</span><span class=""> </span><span class="n">drop_point</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">move_paragraph</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">source_page</span><span class="o">=</span><span class="n">dropped_paragraph</span><span class="p">[</span><span class="s2">"</span><span class="s2">page_id</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">source_paragraph</span><span class="o">=</span><span class="n">dropped_paragraph</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraph_id</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">target_page</span><span class="o">=</span><span class="n">drop_point</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">before_paragraph</span><span class="o">=</span><span class="n">drop_point</span><span class="o">.</span><span class="n">next_paragraph_id</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<p>The DropPointDropTarget requires FindClosestDropPoint to be defined on the target object. Here it is:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Workspace&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">FindClosestDropPoint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">screen_pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">find_first</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">columns</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="k">lambda</span><span class=""> </span><span class="n">column</span><span class="p">:</span><span class=""> </span><span class="n">column</span><span class="o">.</span><span class="n">FindClosestDropPoint</span><span class="p">(</span><span class="n">screen_pos</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Column widget</h5>

<p>The column widget is a vertical scrolling container containing page containers.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Column</span><span class="p">(</span><span class="n">CompactScrolledWindow</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">CompactScrolledWindow</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">parent</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">VSCROLL</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">size</span><span class="o">=</span><span class="p">(</span><span class="n">PAGE_BODY_WIDTH</span><span class="o">+</span><span class="mi">2</span><span class="o">*</span><span class="n">CONTAINER_BORDER</span><span class="o">+</span><span class="n">PAGE_PADDING</span><span class="p">,</span><span class=""> </span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_ids</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_setup_layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_setup_layout</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">SetPages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_ids</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">containers</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Clear</span><span class="p">(</span><span class="bp">True</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">AddSpacer</span><span class="p">(</span><span class="n">PAGE_PADDING</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">page_id</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page_ids</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">container</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">PageContainer</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">container</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">border</span><span class="o">=</span><span class="n">PAGE_PADDING</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">containers</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">container</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">page_ids</span><span class=""> </span><span class="o">!=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_ids</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Scroll</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_ids</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_ids</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">FindClosestDropPoint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">screen_pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">find_first</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">containers</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">container</span><span class="p">:</span><span class=""> </span><span class="n">container</span><span class="o">.</span><span class="n">FindClosestDropPoint</span><span class="p">(</span><span class="n">screen_pos</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Page container widget</h5>

<p>The page container widget draws a box with border. Inside the box a page widget is rendered.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">PageContainer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">150</span><span class="p">,</span><span class=""> </span><span class="mi">150</span><span class="p">,</span><span class=""> </span><span class="mi">150</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_container</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_container</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">255</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_container</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">inner_sizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_container</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">border</span><span class="o">=</span><span class="n">SHADOW_SIZE</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_sizer</span><span class="o">.</span><span class="n">AddSpacer</span><span class="p">(</span><span class="n">CONTAINER_BORDER</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">inner_container</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">inner_sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">LEFT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">border</span><span class="o">=</span><span class="n">CONTAINER_BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">FindClosestDropPoint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">screen_pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">FindClosestDropPoint</span><span class="p">(</span><span class="n">screen_pos</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Page</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Page</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">Page</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<h6>Rendering</h6>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Page&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_paragraph</span><span class="p">(</span><span class="n">Title</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">paragraphs</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">PageDropPoint</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">divider</span><span class="o">=</span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">page_id</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">next_paragraph_id</span><span class="o">=</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_paragraph</span><span class="p">(</span><span class="p">{</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">Paragraph</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">Code</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">factory</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">Factory</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">}</span><span class="p">[</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="p">]</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">PageDropPoint</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">divider</span><span class="o">=</span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">page_id</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">next_paragraph_id</span><span class="o">=</span><span class="bp">None</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_add_button</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_render_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">paragraph</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">border</span><span class="o">=</span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Divider</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">padding</span><span class="o">=</span><span class="p">(</span><span class="n">PARAGRAPH_SPACE</span><span class="o">-</span><span class="mi">3</span><span class="p">)</span><span class="o">/</span><span class="mi">2</span><span class="p">,</span><span class=""> </span><span class="n">height</span><span class="o">=</span><span class="mi">3</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">divider</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">border</span><span class="o">=</span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">divider</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_render_add_button</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">add_button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BitmapButton</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">bitmap</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ArtProvider</span><span class="o">.</span><span class="n">GetBitmap</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">ART_ADD_BOOKMARK</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">ART_BUTTON</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">(</span><span class="mi">16</span><span class="p">,</span><span class=""> </span><span class="mi">16</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">NO_BORDER</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">add_button</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_BUTTON</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_add_button</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">add_button</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TOP</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">ALIGN_RIGHT</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">border</span><span class="o">=</span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_on_add_button</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">add_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">PageDropPoint</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">divider</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">next_paragraph_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">divider</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">next_paragraph_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">next_paragraph_id</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">y_distance_to</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="nb">abs</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Position</span><span class="o">.</span><span class="n">y</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Size</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="o">/</span><span class="mi">2</span><span class=""> </span><span class="o">-</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Show</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Show</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Hide</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">divider</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Dropping paragraphs</h6>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Page&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">FindClosestDropPoint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">screen_pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">client_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">(</span><span class="n">client_x</span><span class="p">,</span><span class=""> </span><span class="n">client_y</span><span class="p">)</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">ScreenToClient</span><span class="p">(</span><span class="n">screen_pos</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">HitTest</span><span class="p">(</span><span class="n">client_pos</span><span class="p">)</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">HT_WINDOW_INSIDE</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">min_or_none</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">drop_points</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">key</span><span class="o">=</span><span class="k">lambda</span><span class=""> </span><span class="n">drop_point</span><span class="p">:</span><span class=""> </span><span class="n">drop_point</span><span class="o">.</span><span class="n">y_distance_to</span><span class="p">(</span><span class="n">client_y</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Title</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Title</span><span class="p">(</span><span class="n">Editable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">        </span><span class="n">Editable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateView</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">create_font</span><span class="p">(</span><span class="n">size</span><span class="o">=</span><span class="mi">16</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">view</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RichTextDisplay</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">[</span><span class="n">Fragment</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">max_width</span><span class="o">=</span><span class="n">PAGE_BODY_WIDTH</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">view</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">edit</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">TextCtrl</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TE_PROCESS_ENTER</span><span class="p">,</span><span class=""> </span><span class="n">value</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">edit</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_TEXT_ENTER</span><span class="p">,</span><span class=""> </span><span class="k">lambda</span><span class=""> </span><span class="n">_</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">EndEdit</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">edit</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">EndEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="s2">"</span><span class="s2">title</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">Value</span><span class="p">}</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Paragraphs</h5>

<h6>Text</h6>

<h7>Paragraph</h7>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Paragraph</span><span class="p">(</span><span class="n">ParagraphBase</span><span class="p">,</span><span class=""> </span><span class="n">Editable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">ParagraphBase</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">Editable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateView</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">view</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RichTextDisplay</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">formatted_text</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">line_height</span><span class="o">=</span><span class="mf">1.2</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">max_width</span><span class="o">=</span><span class="n">PAGE_BODY_WIDTH</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">MouseEventHelper</span><span class="o">.</span><span class="n">bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="p">[</span><span class="n">view</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">drag</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">right_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">ShowContextMenu</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">move</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">_change_cursor</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">_follow_link</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">default_cursor</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">view</span><span class="o">.</span><span class="n">GetCursor</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">link_fragment</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">view</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_change_cursor</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">position</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">fragment</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="o">.</span><span class="n">GetFragment</span><span class="p">(</span><span class="n">position</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">fragment</span><span class="o">.</span><span class="n">token</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Link</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">SetCursor</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">StockCursor</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">CURSOR_HAND</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">link_fragment</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">fragment</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">SetCursor</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">default_cursor</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">link_fragment</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_follow_link</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">link_fragment</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">webbrowser</span><span class="o">.</span><span class="n">open</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">link_fragment</span><span class="o">.</span><span class="n">extra</span><span class="p">[</span><span class="s2">"</span><span class="s2">url</span><span class="s2">"</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">edit</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">TextCtrl</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TE_MULTILINE</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">value</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">text</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="c1"># Error is printed if height is too small:</span><span class="">
</span><span class="">        </span><span class="c1"># Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size &gt;= 0' failed in GtkScrollbar</span><span class="">
</span><span class="">        </span><span class="c1"># Solution: Make it at least 50 heigh.</span><span class="">
</span><span class="">        </span><span class="n">edit</span><span class="o">.</span><span class="n">MinSize</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">(</span><span class="o">-</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="nb">max</span><span class="p">(</span><span class="mi">50</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="o">.</span><span class="n">Size</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">edit</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">EndEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">Value</span><span class="p">}</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Code</h6>

<h7>Container widget</h7>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Code</span><span class="p">(</span><span class="n">ParagraphBase</span><span class="p">,</span><span class=""> </span><span class="n">Editable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">ParagraphBase</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">Editable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateView</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">CodeView</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">CreateEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">CodeEditor</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">EndEdit</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">path</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">Value</span><span class="o">.</span><span class="n">split</span><span class="p">(</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">Value</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">}</span><span class="p">)</span><span class="">
</span></pre></div>

<h7>View widget</h7>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">CodeView</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">BORDER</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">    </span><span class="n">PADDING</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">5</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">create_font</span><span class="p">(</span><span class="n">monospace</span><span class="o">=</span><span class="bp">True</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_path</span><span class="p">(</span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_code</span><span class="p">(</span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">LEFT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">243</span><span class="p">,</span><span class=""> </span><span class="mi">236</span><span class="p">,</span><span class=""> </span><span class="mi">219</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_path</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">248</span><span class="p">,</span><span class=""> </span><span class="mi">241</span><span class="p">,</span><span class=""> </span><span class="mi">223</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RichTextDisplay</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">panel</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">insert_between</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">Fragment</span><span class="p">(</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="p">[</span><span class="n">Fragment</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">token</span><span class="o">=</span><span class="n">pygments</span><span class="o">.</span><span class="n">token</span><span class="o">.</span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Strong</span><span class="p">)</span><span class=""> </span><span class="k">for</span><span class=""> </span><span class="n">x</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">code_paragraph</span><span class="o">.</span><span class="n">path</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">max_width</span><span class="o">=</span><span class="n">PAGE_BODY_WIDTH</span><span class="o">-</span><span class="mi">2</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">PADDING</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">PADDING</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">MouseEventHelper</span><span class="o">.</span><span class="n">bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="p">[</span><span class="n">panel</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">double_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">_post_paragraph_edit_start</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">drag</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">Parent</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">right_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">Parent</span><span class="o">.</span><span class="n">ShowContextMenu</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">panel</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_code</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">253</span><span class="p">,</span><span class=""> </span><span class="mi">246</span><span class="p">,</span><span class=""> </span><span class="mi">227</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">body</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RichTextDisplay</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">panel</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">code_paragraph</span><span class="o">.</span><span class="n">formatted_text</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">max_width</span><span class="o">=</span><span class="n">PAGE_BODY_WIDTH</span><span class="o">-</span><span class="mi">2</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">PADDING</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">body</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">PADDING</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">panel</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">MouseEventHelper</span><span class="o">.</span><span class="n">bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="p">[</span><span class="n">panel</span><span class="p">,</span><span class=""> </span><span class="n">body</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">double_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">_post_paragraph_edit_start</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">drag</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">Parent</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">right_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">Parent</span><span class="o">.</span><span class="n">ShowContextMenu</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">panel</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_post_paragraph_edit_start</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">PostEvent</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">ParagraphEditStart</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">insert_between</span><span class="p">(</span><span class="n">separator</span><span class="p">,</span><span class=""> </span><span class="n">items</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">result</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">i</span><span class="p">,</span><span class=""> </span><span class="n">item</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="nb">enumerate</span><span class="p">(</span><span class="n">items</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">i</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">result</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">separator</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">result</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">item</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">result</span><span class="">
</span></pre></div>

<h7>Editor widget</h7>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">CodeEditor</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">BORDER</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">1</span><span class="">
</span><span class="">    </span><span class="n">PADDING</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">3</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">view</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">create_font</span><span class="p">(</span><span class="n">monospace</span><span class="o">=</span><span class="bp">True</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">view</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_path</span><span class="p">(</span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_code</span><span class="p">(</span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">LEFT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_save</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">LEFT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">BOTTOM</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RIGHT</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">BORDER</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_path</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">TextCtrl</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">value</span><span class="o">=</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">code_paragraph</span><span class="o">.</span><span class="n">path</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_code</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">code_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">TextCtrl</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">style</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TE_MULTILINE</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">value</span><span class="o">=</span><span class="n">code_paragraph</span><span class="o">.</span><span class="n">text</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="c1"># Error is printed if height is too small:</span><span class="">
</span><span class="">        </span><span class="c1"># Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size &gt;= 0' failed in GtkScrollbar</span><span class="">
</span><span class="">        </span><span class="c1"># Solution: Make it at least 50 heigh.</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">MinSize</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">(</span><span class="o">-</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="nb">max</span><span class="p">(</span><span class="mi">50</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="o">.</span><span class="n">Size</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_save</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Button</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">label</span><span class="o">=</span><span class="s2">"</span><span class="s2">Save</span><span class="s2">"</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_BUTTON</span><span class="p">,</span><span class=""> </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_post_paragraph_edit_end</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">button</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_post_paragraph_edit_end</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">PostEvent</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">ParagraphEditEnd</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Factory</h6>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Factory</span><span class="p">(</span><span class="n">ParagraphBase</span><span class="p">,</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">ParagraphBase</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">MouseEventHelper</span><span class="o">.</span><span class="n">bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="p">[</span><span class="bp">self</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">drag</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">right_click</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">ShowContextMenu</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">240</span><span class="p">,</span><span class=""> </span><span class="mi">240</span><span class="p">,</span><span class=""> </span><span class="mi">240</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">StaticText</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">label</span><span class="o">=</span><span class="s2">"</span><span class="s2">Factory</span><span class="s2">"</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TOP</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">ALIGN_CENTER</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">border</span><span class="o">=</span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">TOP</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">ALIGN_CENTER</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">border</span><span class="o">=</span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">text_button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Button</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">label</span><span class="o">=</span><span class="s2">"</span><span class="s2">Text</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">text_button</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_BUTTON</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnTextButton</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">text_button</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="mi">2</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">code_button</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Button</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">label</span><span class="o">=</span><span class="s2">"</span><span class="s2">Code</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">code_button</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_BUTTON</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnCodeButton</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="n">code_button</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">ALL</span><span class="p">,</span><span class=""> </span><span class="n">border</span><span class="o">=</span><span class="mi">2</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">AddSpacer</span><span class="p">(</span><span class="n">PARAGRAPH_SPACE</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnTextButton</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="s2">"</span><span class="s2">type</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">Enter text here...</span><span class="s2">"</span><span class="p">}</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnCodeButton</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="s2">"</span><span class="s2">type</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">path</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">Enter code here...</span><span class="s2">"</span><span class="p">}</span><span class="p">)</span><span class="">
</span></pre></div>

<h6>Common</h6>

<h7>Paragraph base</h7>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">ParagraphBase</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">DoDragDrop</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">data</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RliterateDataObject</span><span class="p">(</span><span class="s2">"</span><span class="s2">paragraph</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">page_id</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">paragraph_id</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">}</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">drag_source</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">DropSource</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">drag_source</span><span class="o">.</span><span class="n">SetData</span><span class="p">(</span><span class="n">data</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">result</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">drag_source</span><span class="o">.</span><span class="n">DoDragDrop</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Drag_DefaultMove</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">ShowContextMenu</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">menu</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ParagraphContextMenu</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">PopupMenu</span><span class="p">(</span><span class="n">menu</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">menu</span><span class="o">.</span><span class="n">Destroy</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h7>Paragraph context menu</h7>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">ParagraphContextMenu</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Menu</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Menu</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_create_menu</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_create_menu</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">delete_paragraph</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">page_id</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">page_id</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">paragraph_id</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Delete</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MENU</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">id</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="p">{</span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">edit_in_gvim</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph</span><span class="o">.</span><span class="n">filename</span><span class="p">)</span><span class="p">}</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">Append</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">NewId</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">Edit in gvim</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<h7>Editable</h7>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Editable</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">CreateView</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEFT_DCLICK</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnParagraphEditStart</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">EVT_PARAGRAPH_EDIT_START</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnParagraphEditStart</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnParagraphEditStart</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">CreateEdit</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">SetFocus</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_CHAR</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnChar</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">EVT_PARAGRAPH_EDIT_END</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">OnParagraphEditEnd</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">edit</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">sizer</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">view</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">GetTopLevelParent</span><span class="p">(</span><span class="p">)</span><span class="o">.</span><span class="n">Layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnParagraphEditEnd</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">EndEdit</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnChar</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">KeyCode</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">WXK_CONTROL_S</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnParagraphEditEnd</span><span class="p">(</span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">elif</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">KeyCode</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">WXK_RETURN</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">ControlDown</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnParagraphEditEnd</span><span class="p">(</span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">event</span><span class="o">.</span><span class="n">Skip</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="a6e8ca0aa83d4829b15c0424be259022"></a>

Drag &amp; drop</h4>

<h5>RLiterate data object</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">RliterateDataObject</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">CustomDataObject</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">kind</span><span class="p">,</span><span class=""> </span><span class="n">json</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">CustomDataObject</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">rliterate/{}</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">kind</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">json</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">set_json</span><span class="p">(</span><span class="n">json</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_json</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">data</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetData</span><span class="p">(</span><span class="n">json</span><span class="o">.</span><span class="n">dumps</span><span class="p">(</span><span class="n">data</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">get_json</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">json</span><span class="o">.</span><span class="n">loads</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">GetData</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Drop point drop target</h5>

<p>A drop target that can work with windows that supports FindClosestDropPoint.</p>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">DropPointDropTarget</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">DropTarget</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">window</span><span class="p">,</span><span class=""> </span><span class="n">kind</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">DropTarget</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">window</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">window</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">last_drop_point</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">rliterate_data</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">RliterateDataObject</span><span class="p">(</span><span class="n">kind</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">DataObject</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">rliterate_data</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnDragOver</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">defResult</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_hide_last_drop_point</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">drop_point</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_find_closest_drop_point</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">drop_point</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">defResult</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">DragMove</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">drop_point</span><span class="o">.</span><span class="n">Show</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">last_drop_point</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">drop_point</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">DragMove</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">DragNone</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnData</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">defResult</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_hide_last_drop_point</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">drop_point</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_find_closest_drop_point</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">drop_point</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">GetData</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnDataDropped</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">rliterate_data</span><span class="o">.</span><span class="n">get_json</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">drop_point</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">defResult</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnLeave</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_hide_last_drop_point</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_find_closest_drop_point</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">window</span><span class="o">.</span><span class="n">FindClosestDropPoint</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">window</span><span class="o">.</span><span class="n">ClientToScreen</span><span class="p">(</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_hide_last_drop_point</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">last_drop_point</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">last_drop_point</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">last_drop_point</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span></pre></div>

<h5>Divider</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Divider</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">padding</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="n">height</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="p">(</span><span class="o">-</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="n">height</span><span class="o">+</span><span class="mi">2</span><span class="o">*</span><span class="n">padding</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="p">(</span><span class="o">-</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="n">height</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class="o">.</span><span class="n">SetBackgroundColour</span><span class="p">(</span><span class="p">(</span><span class="mi">255</span><span class="p">,</span><span class=""> </span><span class="mi">100</span><span class="p">,</span><span class=""> </span><span class="mi">0</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">HORIZONTAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">BoxSizer</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">VERTICAL</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">AddStretchSpacer</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="o">|</span><span class="n">wx</span><span class="o">.</span><span class="n">RESERVE_SPACE_EVEN_IF_HIDDEN</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="o">.</span><span class="n">AddStretchSpacer</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">SetSizer</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">vsizer</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Show</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">left_space</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class="o">.</span><span class="n">Show</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="o">.</span><span class="n">Clear</span><span class="p">(</span><span class="bp">False</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="p">(</span><span class="n">left_space</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">hsizer</span><span class="o">.</span><span class="n">Add</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class="p">,</span><span class=""> </span><span class="n">flag</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">EXPAND</span><span class="p">,</span><span class=""> </span><span class="n">proportion</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">Hide</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">line</span><span class="o">.</span><span class="n">Hide</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Layout</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="5c3647a616b8495f8bebd268be84377d"></a>

wxPython utilities</h4>

<h5>Mouse event helper</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">MouseEventHelper</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@classmethod</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">bind</span><span class="p">(</span><span class="bp">cls</span><span class="p">,</span><span class=""> </span><span class="n">windows</span><span class="p">,</span><span class=""> </span><span class="n">drag</span><span class="o">=</span><span class="bp">None</span><span class="p">,</span><span class=""> </span><span class="n">click</span><span class="o">=</span><span class="bp">None</span><span class="p">,</span><span class=""> </span><span class="n">right_click</span><span class="o">=</span><span class="bp">None</span><span class="p">,</span><span class="">
</span><span class="">             </span><span class="n">double_click</span><span class="o">=</span><span class="bp">None</span><span class="p">,</span><span class=""> </span><span class="n">move</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">window</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">windows</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">mouse_event_helper</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">cls</span><span class="p">(</span><span class="n">window</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">drag</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">mouse_event_helper</span><span class="o">.</span><span class="n">OnDrag</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">drag</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">click</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">mouse_event_helper</span><span class="o">.</span><span class="n">OnClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">click</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">right_click</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">mouse_event_helper</span><span class="o">.</span><span class="n">OnRightClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">right_click</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">double_click</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">mouse_event_helper</span><span class="o">.</span><span class="n">OnDoubleClick</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">double_click</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">move</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">mouse_event_helper</span><span class="o">.</span><span class="n">OnMove</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">move</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">window</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">        </span><span class="n">window</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEFT_DOWN</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_left_down</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">window</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MOTION</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_motion</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">window</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEFT_UP</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_left_up</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">window</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_LEFT_DCLICK</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_left_dclick</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">window</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_RIGHT_UP</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_right_up</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnDrag</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">pass</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnClick</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">pass</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnRightClick</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">pass</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnDoubleClick</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">pass</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">OnMove</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">position</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">pass</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_left_down</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">Position</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_motion</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnMove</span><span class="p">(</span><span class="n">event</span><span class="o">.</span><span class="n">Position</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_should_drag</span><span class="p">(</span><span class="n">event</span><span class="o">.</span><span class="n">Position</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnDrag</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_should_drag</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">pos</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">diff</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="o">-</span><span class=""> </span><span class="n">pos</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="nb">abs</span><span class="p">(</span><span class="n">diff</span><span class="o">.</span><span class="n">x</span><span class="p">)</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">2</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class=""> </span><span class="bp">True</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="nb">abs</span><span class="p">(</span><span class="n">diff</span><span class="o">.</span><span class="n">y</span><span class="p">)</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">2</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class=""> </span><span class="bp">True</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">False</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_left_up</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">OnClick</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">down_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_left_dclick</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">OnDoubleClick</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_right_up</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">OnRightClick</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Rich text display</h5>

<p>The rich text display widget displayes styled text fragments. It does so by drawing text on a DC.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">RichTextDisplay</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">RichTextDisplay</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">project</span><span class="p">,</span><span class=""> </span><span class="n">fragments</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">wx</span><span class="o">.</span><span class="n">Panel</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">project</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">fragments</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">fragments</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">line_height</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">kwargs</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">"</span><span class="s2">line_height</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">max_width</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">kwargs</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">"</span><span class="s2">max_width</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="mi">100</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="fm">__init__</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p>First, the text fragment positions are calculated. For that a DC is needed. But the positions need to be calculated before we can draw on the panel, so a temporary memory DC is created.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">_set_fragments</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_set_fragments</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">dc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">MemoryDC</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">dc</span><span class="o">.</span><span class="n">SetFont</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">GetFont</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">dc</span><span class="o">.</span><span class="n">SelectObject</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EmptyBitmap</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_calculate_fragments</span><span class="p">(</span><span class="n">dc</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">SetMinSize</span><span class="p">(</span><span class="p">(</span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_calculate_fragments</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">dc</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">draw_fragments</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="n">x</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">    </span><span class="n">y</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">    </span><span class="n">max_x</span><span class="p">,</span><span class=""> </span><span class="n">max_y</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">dc</span><span class="o">.</span><span class="n">GetTextExtent</span><span class="p">(</span><span class="s2">"</span><span class="s2">M</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_newline_fragments</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">x</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">            </span><span class="n">y</span><span class=""> </span><span class="o">+</span><span class="o">=</span><span class=""> </span><span class="nb">int</span><span class="p">(</span><span class="nb">round</span><span class="p">(</span><span class="n">dc</span><span class="o">.</span><span class="n">GetTextExtent</span><span class="p">(</span><span class="s2">"</span><span class="s2">M</span><span class="s2">"</span><span class="p">)</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">line_height</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">continue</span><span class="">
</span><span class="">        </span><span class="n">style</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">project</span><span class="o">.</span><span class="n">get_style</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">token</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">style</span><span class="o">.</span><span class="n">apply_to_wx_dc</span><span class="p">(</span><span class="n">dc</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">GetFont</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">dc</span><span class="o">.</span><span class="n">GetTextExtent</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">x</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">0</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">x</span><span class="o">+</span><span class="n">w</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">max_width</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">x</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">            </span><span class="n">y</span><span class=""> </span><span class="o">+</span><span class="o">=</span><span class=""> </span><span class="nb">int</span><span class="p">(</span><span class="nb">round</span><span class="p">(</span><span class="n">dc</span><span class="o">.</span><span class="n">GetTextExtent</span><span class="p">(</span><span class="s2">"</span><span class="s2">M</span><span class="s2">"</span><span class="p">)</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">line_height</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">draw_fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="p">(</span><span class="n">fragment</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="p">,</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Rect</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class="p">)</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">max_x</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="nb">max</span><span class="p">(</span><span class="n">max_x</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="o">+</span><span class="n">w</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">max_y</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="nb">max</span><span class="p">(</span><span class="n">max_y</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="o">+</span><span class="n">h</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">x</span><span class=""> </span><span class="o">+</span><span class="o">=</span><span class=""> </span><span class="n">w</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="p">(</span><span class="n">max_x</span><span class="p">,</span><span class=""> </span><span class="n">max_y</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">_newline_fragments</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">fragments</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">x</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">insert_between</span><span class="p">(</span><span class="bp">None</span><span class="p">,</span><span class=""> </span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">split</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">if</span><span class=""> </span><span class="n">x</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">yield</span><span class=""> </span><span class="n">x</span><span class="">
</span><span class="">                </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">for</span><span class=""> </span><span class="n">subfragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">Fragment</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">token</span><span class="o">=</span><span class="n">fragment</span><span class="o">.</span><span class="n">token</span><span class="p">)</span><span class="o">.</span><span class="n">word_split</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                        </span><span class="k">yield</span><span class=""> </span><span class="n">subfragment</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">subfragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">fragment</span><span class="o">.</span><span class="n">word_split</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">yield</span><span class=""> </span><span class="n">subfragment</span><span class="">
</span></pre></div>

<p>Drawing the rich text is just a matter of drawing all fragments at the pre-calculated positions:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_PAINT</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_paint</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">_on_paint</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">dc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">PaintDC</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="p">,</span><span class=""> </span><span class="n">box</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">draw_fragments</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">style</span><span class="o">.</span><span class="n">apply_to_wx_dc</span><span class="p">(</span><span class="n">dc</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">GetFont</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">dc</span><span class="o">.</span><span class="n">DrawText</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">box</span><span class="o">.</span><span class="n">X</span><span class="p">,</span><span class=""> </span><span class="n">box</span><span class="o">.</span><span class="n">Y</span><span class="p">)</span><span class="">
</span></pre></div>

<p>Some mouse move action:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;RichTextDisplay&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">GetFragment</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">position</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="p">,</span><span class=""> </span><span class="n">box</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">draw_fragments</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">box</span><span class="o">.</span><span class="n">Contains</span><span class="p">(</span><span class="n">position</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="n">fragment</span><span class="">
</span></pre></div>

<h5>Scrolling containers</h5>

<p>The default scrolling window gives extra space. See https://stackoverflow.com/a/22817659. This custom control sovles this problem.</p>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">CompactScrolledWindow</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">ScrolledWindow</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">MIN_WIDTH</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">200</span><span class="">
</span><span class="">    </span><span class="n">MIN_HEIGHT</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">200</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="n">wx</span><span class="o">.</span><span class="n">DefaultSize</span><span class="p">,</span><span class=""> </span><span class="n">step</span><span class="o">=</span><span class="mi">100</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="n">h</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">size</span><span class="">
</span><span class="">        </span><span class="n">size</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">(</span><span class="nb">max</span><span class="p">(</span><span class="n">w</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">MIN_WIDTH</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="nb">max</span><span class="p">(</span><span class="n">h</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">MIN_HEIGHT</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">ScrolledWindow</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">parent</span><span class="p">,</span><span class=""> </span><span class="n">style</span><span class="o">=</span><span class="n">style</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="n">size</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Size</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">size</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">style</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">HSCROLL</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">SetScrollRate</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos_hscroll</span><span class="">
</span><span class="">        </span><span class="k">elif</span><span class=""> </span><span class="n">style</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">VSCROLL</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">SetScrollRate</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos_vscroll</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">SetScrollRate</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos_vscroll</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">step</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">step</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Bind</span><span class="p">(</span><span class="n">wx</span><span class="o">.</span><span class="n">EVT_MOUSEWHEEL</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_on_mousewheel</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_on_mousewheel</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">GetViewStart</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">delta</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">GetWheelRotation</span><span class="p">(</span><span class="p">)</span><span class=""> </span><span class="o">/</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">GetWheelDelta</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">Scroll</span><span class="p">(</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">_calc_scroll_pos</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">delta</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_calc_scroll_pos_hscroll</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">delta</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">(</span><span class="n">x</span><span class="o">+</span><span class="n">delta</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">step</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_calc_scroll_pos_vscroll</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="p">,</span><span class=""> </span><span class="n">delta</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="n">y</span><span class="o">-</span><span class="n">delta</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">step</span><span class="p">)</span><span class="">
</span></pre></div>

<p>The minimum size is set to prevent the following error:</p>

<p>(rliterate.py:23983): Gtk-CRITICAL **: gtk_box_gadget_distribute: assertion 'size &gt;= 0' failed in GtkScrollbar</p>

<h4><a name="4495f053ab2d41a2a4ec70f55e929b9f"></a>

Constants</h4>

<p><code>rliterate.py / &lt;&lt;constants&gt;&gt;</code></p>

<div class="highlight"><pre><span class="n">PAGE_BODY_WIDTH</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">600</span><span class="">
</span><span class="n">PAGE_PADDING</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">13</span><span class="">
</span><span class="n">SHADOW_SIZE</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">2</span><span class="">
</span><span class="n">PARAGRAPH_SPACE</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">15</span><span class="">
</span><span class="n">CONTAINER_BORDER</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">PARAGRAPH_SPACE</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="n">ParagraphEditStart</span><span class="p">,</span><span class=""> </span><span class="n">EVT_PARAGRAPH_EDIT_START</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">lib</span><span class="o">.</span><span class="n">newevent</span><span class="o">.</span><span class="n">NewCommandEvent</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="n">ParagraphEditEnd</span><span class="p">,</span><span class=""> </span><span class="n">EVT_PARAGRAPH_EDIT_END</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">lib</span><span class="o">.</span><span class="n">newevent</span><span class="o">.</span><span class="n">NewCommandEvent</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h3><a name="b376363cbd664a838d3bafb7bfae2281"></a>

Project</h3>

<p>A project is a container for a few other objects:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Project</span><span class="p">(</span><span class="n">Observable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">filepath</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">Observable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">theme</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">SolarizedTheme</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Document</span><span class="o">.</span><span class="n">from_file</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">listen</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">notify_forwarder</span><span class="p">(</span><span class="s2">"</span><span class="s2">document</span><span class="s2">"</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Layout</span><span class="p">(</span><span class="s2">"</span><span class="s2">.{}.layout</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">listen</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">notify_forwarder</span><span class="p">(</span><span class="s2">"</span><span class="s2">layout</span><span class="s2">"</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">FileGenerator</span><span class="p">(</span><span class="p">)</span><span class="o">.</span><span class="n">set_document</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">MarkdownGenerator</span><span class="p">(</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">splitext</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="o">+</span><span class="s2">"</span><span class="s2">.markdown</span><span class="s2">"</span><span class="p">)</span><span class="o">.</span><span class="n">set_document</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">HTMLGenerator</span><span class="p">(</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">splitext</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="o">+</span><span class="s2">"</span><span class="s2">.html</span><span class="s2">"</span><span class="p">)</span><span class="o">.</span><span class="n">set_document</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">TextDiff</span><span class="p">(</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">splitext</span><span class="p">(</span><span class="n">filepath</span><span class="p">)</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="o">+</span><span class="s2">"</span><span class="s2">.textdiff</span><span class="s2">"</span><span class="p">)</span><span class="o">.</span><span class="n">set_document</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">Project</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p>Wrapper methods for layout:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Project&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">toggle_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">toggle_collapsed</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">is_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">is_collapsed</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">get_scratch_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">get_scratch_pages</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">set_scratch_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">set_scratch_pages</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="nd">@property</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">columns</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">columns</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">open_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">open_pages</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">get_hoisted_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">get_hoisted_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">set_hoisted_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">layout</span><span class="o">.</span><span class="n">set_hoisted_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span></pre></div>

<p>Wrapper methods for document:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Project&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">get_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">add_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">add_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">delete_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">delete_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">move_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">move_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">edit_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">edit_page</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">add_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">add_paragraph</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">move_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">move_paragraph</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">delete_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">delete_paragraph</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">edit_paragraph</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span></pre></div>

<p>Wrapper for theme:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Project&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">get_style</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">theme</span><span class="o">.</span><span class="n">get_style</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">kwargs</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="276ff8047f7e46dea723c1822078ac26"></a>

Document model</h4>

<h5>Document</h5>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Document</span><span class="p">(</span><span class="n">Observable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@classmethod</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">from_file</span><span class="p">(</span><span class="bp">cls</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">cls</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">Observable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">path</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_load</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_cache</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listen</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_save</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_cache</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_cache_page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">root_page</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_cache_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">parent_page</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">parent_page</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">]</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class="p">[</span><span class="n">paragraph</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_cache_page</span><span class="p">(</span><span class="n">child</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_save</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">write_json_to_file</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">root_page</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_load</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">root_page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">load_json_from_file</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">Document</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="c1"># Page operations</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">add_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">title</span><span class="o">=</span><span class="s2">"</span><span class="s2">New page</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">parent_id</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">genid</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">title</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">New page...</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">}</span><span class="">
</span><span class="">            </span><span class="n">parent_page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">parent_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">parent_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">parent_page</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">delete_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">parent_page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">index</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">index_with_id</span><span class="p">(</span><span class="n">parent_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">parent_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">index</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="nb">reversed</span><span class="p">(</span><span class="n">page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">parent_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="n">index</span><span class="p">,</span><span class=""> </span><span class="n">child</span><span class="p">)</span><span class="">
</span><span class="">                </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">child</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">parent_page</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">move_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">parent_page_id</span><span class="p">,</span><span class=""> </span><span class="n">before_page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">page_id</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">before_page_id</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class="">
</span><span class="">            </span><span class="n">parent</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">parent_page_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="k">while</span><span class=""> </span><span class="n">parent</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">if</span><span class=""> </span><span class="n">parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">page_id</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">return</span><span class="">
</span><span class="">                </span><span class="n">parent</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">parent</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">page</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">index_with_id</span><span class="p">(</span><span class="n">parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">new_parent</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">parent_page_id</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_parent_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">new_parent</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">before_page_id</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">new_parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">new_parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="">
</span><span class="">                    </span><span class="n">index_with_id</span><span class="p">(</span><span class="n">new_parent</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">before_page_id</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                    </span><span class="n">page</span><span class="">
</span><span class="">                </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">edit_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">data</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="o">.</span><span class="n">update</span><span class="p">(</span><span class="n">data</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="c1"># Paragraph operations</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">add_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">before_id</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">paragraph</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">genid</span><span class="p">(</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">type</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">factory</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">factory</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">}</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class="p">[</span><span class="n">paragraph</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">move_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">source_page</span><span class="p">,</span><span class=""> </span><span class="n">source_paragraph</span><span class="p">,</span><span class=""> </span><span class="n">target_page</span><span class="p">,</span><span class=""> </span><span class="n">before_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="p">(</span><span class="n">source_page</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">target_page</span><span class=""> </span><span class="ow">and</span><span class="">
</span><span class="">                </span><span class="n">source_paragraph</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">before_paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class="">
</span><span class="">            </span><span class="n">paragraph</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">delete_paragraph</span><span class="p">(</span><span class="n">source_page</span><span class="p">,</span><span class=""> </span><span class="n">source_paragraph</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_add_paragraph</span><span class="p">(</span><span class="n">target_page</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">,</span><span class=""> </span><span class="n">before_id</span><span class="o">=</span><span class="n">before_paragraph</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_add_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">,</span><span class=""> </span><span class="n">before_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">paragraphs</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">before_id</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">paragraphs</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">paragraphs</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="n">index_with_id</span><span class="p">(</span><span class="n">paragraphs</span><span class="p">,</span><span class=""> </span><span class="n">before_id</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class="p">[</span><span class="n">paragraph</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">delete_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="n">paragraph_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">paragraphs</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="p">[</span><span class="n">page_id</span><span class="p">]</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="n">paragraphs</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">index_with_id</span><span class="p">(</span><span class="n">paragraphs</span><span class="p">,</span><span class=""> </span><span class="n">paragraph_id</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">paragraph_id</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">edit_paragraph</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">paragraph_id</span><span class="p">,</span><span class=""> </span><span class="n">data</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraphs</span><span class="p">[</span><span class="n">paragraph_id</span><span class="p">]</span><span class="o">.</span><span class="n">update</span><span class="p">(</span><span class="n">data</span><span class="p">)</span><span class="">
</span></pre></div>

<h5>Views</h5>

<p>Views provide a read only interface to a document. It is the only way to query a document.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Document&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">get_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="n">page_id</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">page_id</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">root_page</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="n">page_dict</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_pages</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">page_id</span><span class="p">,</span><span class=""> </span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="n">page_dict</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">DictPage</span><span class="p">(</span><span class="n">page_dict</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">DictPage</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_dict</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_dict</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_dict</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">id</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">title</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">title</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">paragraphs</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">[</span><span class="">
</span><span class="">            </span><span class="n">DictParagraph</span><span class="o">.</span><span class="n">create</span><span class="p">(</span><span class="n">paragraph_dict</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">paragraph_dict</span><span class="">
</span><span class="">            </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">paragraphs</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">children</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">[</span><span class="">
</span><span class="">            </span><span class="n">DictPage</span><span class="p">(</span><span class="n">child_dict</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">child_dict</span><span class="">
</span><span class="">            </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_page_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">children</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="p">]</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">DictParagraph</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@staticmethod</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">create</span><span class="p">(</span><span class="n">paragraph_dict</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">DictTextParagraph</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">DictCodeParagraph</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">}</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">type</span><span class="s2">"</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">DictParagraph</span><span class="p">)</span><span class="p">(</span><span class="n">paragraph_dict</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">paragraph_dict</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">paragraph_dict</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">id</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">type</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">type</span><span class="s2">"</span><span class="p">]</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">DictTextParagraph</span><span class="p">(</span><span class="n">DictParagraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">filename</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="s2">"</span><span class="s2">paragraph.txt</span><span class="s2">"</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">text</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">formatted_text</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">fragments</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="n">partial</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="">
</span><span class="">        </span><span class="k">while</span><span class=""> </span><span class="n">text</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">result</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_get_special_fragment</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">result</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">partial</span><span class=""> </span><span class="o">+</span><span class="o">=</span><span class=""> </span><span class="n">text</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="">
</span><span class="">                </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">text</span><span class="p">[</span><span class="mi">1</span><span class="p">:</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="n">match</span><span class="p">,</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">result</span><span class="">
</span><span class="">                </span><span class="k">if</span><span class=""> </span><span class="n">partial</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="n">fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">Fragment</span><span class="p">(</span><span class="n">partial</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">                    </span><span class="n">partial</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="">
</span><span class="">                </span><span class="n">fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">fragment</span><span class="p">)</span><span class="">
</span><span class="">                </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">text</span><span class="p">[</span><span class="n">match</span><span class="o">.</span><span class="n">end</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="p">:</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">partial</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">Fragment</span><span class="p">(</span><span class="n">partial</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">fragments</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">PATTERNS</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="">
</span><span class="">        </span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">re</span><span class="o">.</span><span class="n">compile</span><span class="p">(</span><span class="sa">r</span><span class="s2">"</span><span class="s2">\</span><span class="s2">*</span><span class="s2">\</span><span class="s2">*(.+?)</span><span class="s2">\</span><span class="s2">*</span><span class="s2">\</span><span class="s2">*</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">flags</span><span class="o">=</span><span class="n">re</span><span class="o">.</span><span class="n">DOTALL</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">match</span><span class="p">:</span><span class=""> </span><span class="n">Fragment</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">token</span><span class="o">=</span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Strong</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">re</span><span class="o">.</span><span class="n">compile</span><span class="p">(</span><span class="sa">r</span><span class="s2">"</span><span class="s2">\</span><span class="s2">[(.+?)</span><span class="s2">\</span><span class="s2">]</span><span class="s2">\</span><span class="s2">((.+?)</span><span class="s2">\</span><span class="s2">)</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">flags</span><span class="o">=</span><span class="n">re</span><span class="o">.</span><span class="n">DOTALL</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="k">lambda</span><span class=""> </span><span class="n">match</span><span class="p">:</span><span class=""> </span><span class="n">Fragment</span><span class="p">(</span><span class="">
</span><span class="">                </span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">token</span><span class="o">=</span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Link</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="n">url</span><span class="o">=</span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">2</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">    </span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_get_special_fragment</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">pattern</span><span class="p">,</span><span class=""> </span><span class="n">fn</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">PATTERNS</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">match</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">pattern</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">match</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class=""> </span><span class="n">match</span><span class="p">,</span><span class=""> </span><span class="n">fn</span><span class="p">(</span><span class="n">match</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">DictCodeParagraph</span><span class="p">(</span><span class="n">DictParagraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">text</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">formatted_text</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">try</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">lexer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_get_lexer</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">except</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">lexer</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">pygments</span><span class="o">.</span><span class="n">lexers</span><span class="o">.</span><span class="n">TextLexer</span><span class="p">(</span><span class="n">stripnl</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_tokens_to_fragments</span><span class="p">(</span><span class="n">lexer</span><span class="o">.</span><span class="n">get_tokens</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">path</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="nb">tuple</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_paragraph_dict</span><span class="p">[</span><span class="s2">"</span><span class="s2">path</span><span class="s2">"</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">filename</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">last_part</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">part</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">part</span><span class="o">.</span><span class="n">startswith</span><span class="p">(</span><span class="s2">"</span><span class="s2">&lt;&lt;</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">break</span><span class="">
</span><span class="">            </span><span class="n">last_part</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">part</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">last_part</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@property</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">language</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">try</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_get_lexer</span><span class="p">(</span><span class="p">)</span><span class="o">.</span><span class="n">aliases</span><span class="p">[</span><span class="p">:</span><span class="mi">1</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">except</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_get_lexer</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">pygments</span><span class="o">.</span><span class="n">lexers</span><span class="o">.</span><span class="n">get_lexer_for_filename</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">filename</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">stripnl</span><span class="o">=</span><span class="bp">False</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_tokens_to_fragments</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">tokens</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">fragments</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">token</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">tokens</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">Fragment</span><span class="p">(</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">token</span><span class="o">=</span><span class="n">token</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">fragments</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Fragment</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">token</span><span class="o">=</span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">extra</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">text</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">token</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">token</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">extra</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">extra</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">word_split</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">fragments</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">text</span><span class="">
</span><span class="">        </span><span class="k">while</span><span class=""> </span><span class="n">text</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">match</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="sa">r</span><span class="s2">"</span><span class="s2">.+?(</span><span class="s2">\</span><span class="s2">s+|$)</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">flags</span><span class="o">=</span><span class="n">re</span><span class="o">.</span><span class="n">DOTALL</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">fragments</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">Fragment</span><span class="p">(</span><span class="n">text</span><span class="o">=</span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">token</span><span class="o">=</span><span class="bp">self</span><span class="o">.</span><span class="n">token</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">extra</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">text</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">text</span><span class="p">[</span><span class="n">match</span><span class="o">.</span><span class="n">end</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="p">:</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">fragments</span><span class="">
</span></pre></div>

<h4><a name="f7f16199492c4bad80567c3a960b8bc9"></a>

Layouts</h4>

<p>A layout knows the visual state of the program. It for example knows what pages are expanded/collapsed in the table of contents and what is shown in the workspace.</p>

<p>The layout is recorded in a JSON object that is serialized to disk as soon as something changes.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Layout</span><span class="p">(</span><span class="n">Observable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="n">Layout</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">Observable</span><span class="o">.</span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">listen</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="n">write_json_to_file</span><span class="p">(</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">exists</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">load_json_from_file</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="">
</span><span class="">    </span><span class="o">&lt;&lt;</span><span class="fm">__init__</span><span class="o">&gt;&gt;</span><span class="">
</span></pre></div>

<p>The rest of this class provides methods for reading and writing the `data` dict.</p>

<p>The hoisted page is stored in `toc.hoisted_page_id`:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">_toc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ensure_key</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">toc</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">get_hoisted_page</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">"</span><span class="s2">hoisted_page_id</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="bp">None</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">set_hoisted_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="s2">"</span><span class="s2">toc</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc</span><span class="p">[</span><span class="s2">"</span><span class="s2">hoisted_page_id</span><span class="s2">"</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">page_id</span><span class="">
</span></pre></div>

<p>The collapsed pages are stored in `toc.collapsed`:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">_toc_collapsed</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ensure_key</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_toc</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">collapsed</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">is_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">page_id</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc_collapsed</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">toggle_collapsed</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="s2">"</span><span class="s2">toc</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">page_id</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc_collapsed</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc_collapsed</span><span class="o">.</span><span class="n">remove</span><span class="p">(</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_toc_collapsed</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">page_id</span><span class="p">)</span><span class="">
</span></pre></div>

<p>The scratch pages are stored in `workspace.scratch`:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">_workspace</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ensure_key</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">data</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">workspace</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">{</span><span class="p">}</span><span class="p">)</span><span class="">
</span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_scratch</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ensure_key</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">scratch</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">get_scratch_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_scratch</span><span class="p">[</span><span class="p">:</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">set_scratch_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_ids</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="bp">self</span><span class="o">.</span><span class="n">set_pages</span><span class="p">(</span><span class="n">page_ids</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="mi">0</span><span class="p">)</span><span class="">
</span></pre></div>

<p>The pages displayed in the columns in the workspace are stored in `workspace.columns`:</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt; / &lt;&lt;__init__&gt;&gt;</code></p>

<div class="highlight"><pre><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_columns</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">ensure_key</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">columns</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt; / &lt;&lt;Layout&gt;&gt;</code></p>

<div class="highlight"><pre><span class="nd">@property</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">columns</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_columns</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">[</span><span class="n">column</span><span class="p">[</span><span class="p">:</span><span class="p">]</span><span class=""> </span><span class="k">for</span><span class=""> </span><span class="n">column</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_columns</span><span class="p">]</span><span class="">
</span><span class="">    </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">get_scratch_pages</span><span class="p">(</span><span class="p">)</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">open_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page_ids</span><span class="p">,</span><span class=""> </span><span class="n">column_index</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">notify</span><span class="p">(</span><span class="s2">"</span><span class="s2">workspace</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">column_index</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">column_index</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_columns</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_workspace_columns</span><span class="p">[</span><span class="n">column_index</span><span class="p">:</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="n">page_ids</span><span class="p">[</span><span class="p">:</span><span class="p">]</span><span class="p">]</span><span class="">
</span></pre></div>

<p>Finally we have a utility function for ensuring that a specific key exists in a dictionary.</p>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">ensure_key</span><span class="p">(</span><span class="n">a_dict</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="p">,</span><span class=""> </span><span class="n">default</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="n">key</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">a_dict</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">a_dict</span><span class="p">[</span><span class="n">key</span><span class="p">]</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">default</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">a_dict</span><span class="p">[</span><span class="n">key</span><span class="p">]</span><span class="">
</span></pre></div>

<h4><a name="192db0d4b96e4162b3cf19f870ee287d"></a>

Themes</h4>

<p>Some parts of the application can be themed. Token types from pygments denote different things that can be styled.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">BaseTheme</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">get_style</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">token_type</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">token_type</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">styles</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">styles</span><span class="p">[</span><span class="n">token_type</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">get_style</span><span class="p">(</span><span class="n">token_type</span><span class="o">.</span><span class="n">parent</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Style</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">color</span><span class="p">,</span><span class=""> </span><span class="n">bold</span><span class="o">=</span><span class="bp">None</span><span class="p">,</span><span class=""> </span><span class="n">underlined</span><span class="o">=</span><span class="bp">None</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">color</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">color</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">color_rgb</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="nb">tuple</span><span class="p">(</span><span class="p">[</span><span class="">
</span><span class="">            </span><span class="nb">int</span><span class="p">(</span><span class="n">x</span><span class="p">,</span><span class=""> </span><span class="mi">16</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">x</span><span class="">
</span><span class="">            </span><span class="ow">in</span><span class=""> </span><span class="p">(</span><span class="n">color</span><span class="p">[</span><span class="mi">1</span><span class="p">:</span><span class="mi">3</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">color</span><span class="p">[</span><span class="mi">3</span><span class="p">:</span><span class="mi">5</span><span class="p">]</span><span class="p">,</span><span class=""> </span><span class="n">color</span><span class="p">[</span><span class="mi">5</span><span class="p">:</span><span class="mi">7</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">bold</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">bold</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">underlined</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">underlined</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">get_css</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="s2">"</span><span class="s2">color: {}</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">color</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">apply_to_wx_dc</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">dc</span><span class="p">,</span><span class=""> </span><span class="n">base_font</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">base_font</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">bold</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">font</span><span class="o">.</span><span class="n">Bold</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">underlined</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">font</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">font</span><span class="o">.</span><span class="n">Underlined</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">dc</span><span class="o">.</span><span class="n">SetFont</span><span class="p">(</span><span class="n">font</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">dc</span><span class="o">.</span><span class="n">SetTextForeground</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">color_rgb</span><span class="p">)</span><span class="">
</span></pre></div>

<p>Here is a theme based on solarized. Mostly stolen from https://github.com/honza/solarized-pygments/blob/master/solarized.py.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">SolarizedTheme</span><span class="p">(</span><span class="n">BaseTheme</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">base03</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#002b36</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base02</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#073642</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base01</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#586e75</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base00</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#657b83</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base0</span><span class="">   </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#839496</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base1</span><span class="">   </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#93a1a1</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base2</span><span class="">   </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#eee8d5</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">base3</span><span class="">   </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#fdf6e3</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">yellow</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#b58900</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">orange</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#cb4b16</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">red</span><span class="">     </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#dc322f</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">magenta</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#d33682</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">violet</span><span class="">  </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#6c71c4</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">blue</span><span class="">    </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#268bd2</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">cyan</span><span class="">    </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#2aa198</span><span class="s2">"</span><span class="">
</span><span class="">    </span><span class="n">green</span><span class="">   </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#859900</span><span class="s2">"</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">text</span><span class="">    </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">#2e3436</span><span class="s2">"</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="n">styles</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">{</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="p">:</span><span class="">                     </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">base00</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Keyword</span><span class="p">:</span><span class="">             </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">green</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Keyword</span><span class="o">.</span><span class="n">Constant</span><span class="p">:</span><span class="">    </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">cyan</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Keyword</span><span class="o">.</span><span class="n">Declaration</span><span class="p">:</span><span class=""> </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Keyword</span><span class="o">.</span><span class="n">Namespace</span><span class="p">:</span><span class="">   </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">orange</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Builtin</span><span class="p">:</span><span class="">        </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">red</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Builtin</span><span class="o">.</span><span class="n">Pseudo</span><span class="p">:</span><span class=""> </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Class</span><span class="p">:</span><span class="">          </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Decorator</span><span class="p">:</span><span class="">      </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Entity</span><span class="p">:</span><span class="">         </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">violet</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Exception</span><span class="p">:</span><span class="">      </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">yellow</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Name</span><span class="o">.</span><span class="n">Function</span><span class="p">:</span><span class="">       </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">String</span><span class="p">:</span><span class="">              </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">cyan</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Number</span><span class="p">:</span><span class="">              </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">cyan</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Operator</span><span class="o">.</span><span class="n">Word</span><span class="p">:</span><span class="">       </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">green</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">Comment</span><span class="p">:</span><span class="">             </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">base1</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="p">:</span><span class="">           </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">text</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Strong</span><span class="p">:</span><span class="">    </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">bold</span><span class="o">=</span><span class="bp">True</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Link</span><span class="p">:</span><span class="">      </span><span class="n">Style</span><span class="p">(</span><span class="n">color</span><span class="o">=</span><span class="n">blue</span><span class="p">,</span><span class=""> </span><span class="n">underlined</span><span class="o">=</span><span class="bp">True</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">    </span><span class="p">}</span><span class="">
</span></pre></div>

<h3><a name="63ff2f7abea44406922c78b7683e2dd3"></a>

Generating output</h3>

<h4><a name="56b835fee5b24f8a8e59156506ac6464"></a>

Code files</h4>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">FileGenerator</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_generate</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_document</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">document</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">document</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_generate</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_parts</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_collect_parts</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_generate_files</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_collect_parts</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">paragraphs</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">for</span><span class=""> </span><span class="n">line</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">paragraph</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">splitlines</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="bp">self</span><span class="o">.</span><span class="n">_parts</span><span class="p">[</span><span class="n">paragraph</span><span class="o">.</span><span class="n">path</span><span class="p">]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">line</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_collect_parts</span><span class="p">(</span><span class="n">child</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_generate_files</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">key</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_parts</span><span class="o">.</span><span class="n">keys</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">filepath</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_get_filepath</span><span class="p">(</span><span class="n">key</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">filepath</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">with</span><span class=""> </span><span class="nb">open</span><span class="p">(</span><span class="n">filepath</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">w</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="p">,</span><span class=""> </span><span class="n">prefix</span><span class="o">=</span><span class="s2">"</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">line</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_parts</span><span class="p">[</span><span class="n">key</span><span class="p">]</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">match</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="sa">r</span><span class="s2">"</span><span class="s2">^(</span><span class="s2">\</span><span class="s2">s*)(&lt;&lt;.*&gt;&gt;)</span><span class="s2">\</span><span class="s2">s*$</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">line</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">match</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="bp">self</span><span class="o">.</span><span class="n">_render</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="p">(</span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">2</span><span class="p">)</span><span class="p">,</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">prefix</span><span class="o">=</span><span class="n">prefix</span><span class="o">+</span><span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">else</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">if</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="n">line</span><span class="p">)</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">prefix</span><span class="p">)</span><span class="">
</span><span class="">                    </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">line</span><span class="p">)</span><span class="">
</span><span class="">                </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_get_filepath</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="n">key</span><span class="p">)</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">part</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">key</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">part</span><span class="o">.</span><span class="n">startswith</span><span class="p">(</span><span class="s2">"</span><span class="s2">&lt;&lt;</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">part</span><span class="o">.</span><span class="n">endswith</span><span class="p">(</span><span class="s2">"</span><span class="s2">&gt;&gt;</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="o">*</span><span class="n">key</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="1b021eaa54da4d0282e9cbcd8b875f79"></a>

Markdown book</h4>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">MarkdownGenerator</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_generate</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">path</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_document</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">document</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">document</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_generate</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="nb">open</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">w</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_page</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">level</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">#</span><span class="s2">"</span><span class="o">*</span><span class="n">level</span><span class="o">+</span><span class="s2">"</span><span class="s2"> </span><span class="s2">"</span><span class="o">+</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">paragraphs</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="p">{</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_text</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_code</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">}</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_unknown</span><span class="p">)</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_page</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">child</span><span class="p">,</span><span class=""> </span><span class="n">level</span><span class="o">+</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_text</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">text</span><span class="o">.</span><span class="n">text</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_code</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">code</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">`</span><span class="s2">"</span><span class="o">+</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">code</span><span class="o">.</span><span class="n">path</span><span class="p">)</span><span class="o">+</span><span class="s2">"</span><span class="s2">`:</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">```</span><span class="s2">"</span><span class="o">+</span><span class="n">code</span><span class="o">.</span><span class="n">language</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">line</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">code</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">splitlines</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">line</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">```</span><span class="s2">"</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_unknown</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">Unknown type = </span><span class="s2">"</span><span class="o">+</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="162d5b5c668d4c958c88b7d37e6f5d3e"></a>

HTML</h4>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">HTMLGenerator</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_generate</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">path</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_document</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">document</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">document</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_generate</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="nb">open</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">w</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">HTMLBuilder</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="o">.</span><span class="n">build</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">class</span><span class=""> </span><span class="nc">HTMLBuilder</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">document</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="o">*</span><span class="n">options</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">document</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">parts</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">generate_toc</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">options</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">"</span><span class="s2">generate_toc</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="bp">True</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">toc_max_depth</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">options</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">"</span><span class="s2">toc_max_depth</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="mi">3</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">build</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">parts</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">toc</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">root_page</span><span class="p">,</span><span class=""> </span><span class="n">levels_left</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">levels_left</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">ul</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">for</span><span class=""> </span><span class="n">page</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">root_page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">li</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">a</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">,</span><span class=""> </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="s2">"</span><span class="s2">href</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">#{}</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="p">}</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                            </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="">
</span><span class="">                            </span><span class="bp">self</span><span class="o">.</span><span class="n">toc</span><span class="p">(</span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">levels_left</span><span class=""> </span><span class="o">-</span><span class=""> </span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">page</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="n">level</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">h{}</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">level</span><span class="p">)</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">level</span><span class=""> </span><span class="o">&gt;</span><span class=""> </span><span class="mi">1</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="n">level</span><span class=""> </span><span class="o">&lt;</span><span class="o">=</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">toc_max_depth</span><span class="o">+</span><span class="mi">1</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">a</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="s2">"</span><span class="s2">name</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">}</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">pass</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">paragraphs</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="p">{</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph_text</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph_code</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="p">}</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">paragraph_unknown</span><span class="p">)</span><span class="p">(</span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">level</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="mi">1</span><span class=""> </span><span class="ow">and</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">generate_toc</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">toc</span><span class="p">(</span><span class="n">page</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">toc_max_depth</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">page</span><span class="p">(</span><span class="n">child</span><span class="p">,</span><span class=""> </span><span class="n">level</span><span class="o">+</span><span class="mi">1</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">paragraph_text</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">p</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">text</span><span class="o">.</span><span class="n">formatted_text</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="p">{</span><span class="">
</span><span class="">                    </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Strong</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">fragment_strong</span><span class="p">,</span><span class="">
</span><span class="">                    </span><span class="n">Token</span><span class="o">.</span><span class="n">RLiterate</span><span class="o">.</span><span class="n">Link</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">fragment_link</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="p">}</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">token</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">fragment_default</span><span class="p">)</span><span class="p">(</span><span class="n">fragment</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">fragment_strong</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fragment</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">strong</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">fragment_link</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fragment</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">a</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="s2">"</span><span class="s2">href</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">fragment</span><span class="o">.</span><span class="n">extra</span><span class="p">[</span><span class="s2">"</span><span class="s2">url</span><span class="s2">"</span><span class="p">]</span><span class="p">}</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">fragment_default</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fragment</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">paragraph_code</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">code</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">p</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">code</span><span class="o">.</span><span class="n">path</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">div</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="s2">"</span><span class="s2">class</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="s2">"</span><span class="s2">highlight</span><span class="s2">"</span><span class="p">}</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">pre</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">for</span><span class=""> </span><span class="n">fragment</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">code</span><span class="o">.</span><span class="n">formatted_text</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="">
</span><span class="">                        </span><span class="s2">"</span><span class="s2">span</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">                        </span><span class="n">newlines</span><span class="o">=</span><span class="bp">False</span><span class="p">,</span><span class="">
</span><span class="">                        </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="s2">"</span><span class="s2">class</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="n">STANDARD_TYPES</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">token</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="p">)</span><span class="p">}</span><span class="">
</span><span class="">                    </span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                        </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="n">fragment</span><span class="o">.</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">paragraph_unknown</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">tag</span><span class="p">(</span><span class="s2">"</span><span class="s2">p</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">escaped</span><span class="p">(</span><span class="s2">"</span><span class="s2">Unknown paragraph...</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@contextlib.contextmanager</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">tag</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">tag</span><span class="p">,</span><span class=""> </span><span class="n">newlines</span><span class="o">=</span><span class="bp">True</span><span class="p">,</span><span class=""> </span><span class="n">args</span><span class="o">=</span><span class="p">{</span><span class="p">}</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">args_string</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2">"</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">args</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">args_string</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="s2">"</span><span class="s2"> </span><span class="s2">"</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="s2">"</span><span class="s2"> </span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="s2">"</span><span class="s2">{}=</span><span class="se">\"</span><span class="s2">{}</span><span class="se">\"</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">k</span><span class="p">,</span><span class=""> </span><span class="n">v</span><span class="p">)</span><span class=""> </span><span class="k">for</span><span class=""> </span><span class="n">k</span><span class="p">,</span><span class=""> </span><span class="n">v</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">args</span><span class="o">.</span><span class="n">items</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">raw</span><span class="p">(</span><span class="s2">"</span><span class="s2">&lt;{}{}&gt;</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">tag</span><span class="p">,</span><span class=""> </span><span class="n">args_string</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">yield</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">raw</span><span class="p">(</span><span class="s2">"</span><span class="s2">&lt;/{}&gt;</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">tag</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">newlines</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">raw</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">raw</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">escaped</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">xml</span><span class="o">.</span><span class="n">sax</span><span class="o">.</span><span class="n">saxutils</span><span class="o">.</span><span class="n">escape</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="p">)</span><span class="">
</span></pre></div>

<h4><a name="427cb0d170a04b9898b5b744cd15b263"></a>

Textual diffing</h4>

<p>This generates a file that is suitable for textual diffing.</p>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">TextDiff</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">Listener</span><span class="p">(</span><span class="k">lambda</span><span class=""> </span><span class="n">event</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_generate</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">path</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_document</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">document</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">document</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">listener</span><span class="o">.</span><span class="n">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_generate</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">with</span><span class=""> </span><span class="nb">open</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">w</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">pages</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_collect_pages</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">document</span><span class="o">.</span><span class="n">get_page</span><span class="p">(</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_pages</span><span class="p">(</span><span class="n">f</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_collect_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">page</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">pages</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">page</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">child</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">children</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_collect_pages</span><span class="p">(</span><span class="n">child</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_pages</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">page</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="nb">sorted</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">pages</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="o">=</span><span class="k">lambda</span><span class=""> </span><span class="n">page</span><span class="p">:</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">id</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">: </span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">page</span><span class="o">.</span><span class="n">title</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">paragraph</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">page</span><span class="o">.</span><span class="n">paragraphs</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="p">{</span><span class="">
</span><span class="">                    </span><span class="s2">"</span><span class="s2">text</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_text</span><span class="p">,</span><span class="">
</span><span class="">                    </span><span class="s2">"</span><span class="s2">code</span><span class="s2">"</span><span class="p">:</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_code</span><span class="p">,</span><span class="">
</span><span class="">                </span><span class="p">}</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="p">,</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_render_unknown</span><span class="p">)</span><span class="p">(</span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_text</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">text</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">text</span><span class="o">.</span><span class="n">text</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_code</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">code</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">`</span><span class="s2">"</span><span class="o">+</span><span class="s2">"</span><span class="s2"> / </span><span class="s2">"</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">code</span><span class="o">.</span><span class="n">path</span><span class="p">)</span><span class="o">+</span><span class="s2">"</span><span class="s2">`:</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">line</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">code</span><span class="o">.</span><span class="n">text</span><span class="o">.</span><span class="n">splitlines</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">    </span><span class="s2">"</span><span class="o">+</span><span class="n">line</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_render_unknown</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class=""> </span><span class="n">paragraph</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="s2">"</span><span class="s2">Unknown type = </span><span class="s2">"</span><span class="o">+</span><span class="n">paragraph</span><span class="o">.</span><span class="n">type</span><span class="o">+</span><span class="s2">"</span><span class="se">\n</span><span class="se">\n</span><span class="s2">"</span><span class="p">)</span><span class="">
</span></pre></div>

<h3><a name="01aa28a581e84f088104c6cd600d9c1d"></a>

Publish subscribe mechanisms</h3>

<p><code>rliterate.py / &lt;&lt;base classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Observable</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify_count</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="mi">0</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_listeners</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="p">[</span><span class="p">]</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">listen</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">events</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_listeners</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="p">(</span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="n">events</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">unlisten</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">events</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_listeners</span><span class="o">.</span><span class="n">remove</span><span class="p">(</span><span class="p">(</span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="n">events</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="nd">@contextlib.contextmanager</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">notify</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="o">=</span><span class="s2">"</span><span class="s2">"</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify_count</span><span class=""> </span><span class="o">+</span><span class="o">=</span><span class=""> </span><span class="mi">1</span><span class="">
</span><span class="">        </span><span class="k">try</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">yield</span><span class="">
</span><span class="">        </span><span class="k">finally</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify_count</span><span class=""> </span><span class="o">-</span><span class="o">=</span><span class=""> </span><span class="mi">1</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify</span><span class="p">(</span><span class="n">event</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">notify_forwarder</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">prefix</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">def</span><span class=""> </span><span class="nf">forwarder</span><span class="p">(</span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify</span><span class="p">(</span><span class="s2">"</span><span class="s2">{}.{}</span><span class="s2">"</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">prefix</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">forwarder</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_notify</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_notify_count</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">for</span><span class=""> </span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="n">fn_events</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_listeners</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">_is_match</span><span class="p">(</span><span class="n">fn_events</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                    </span><span class="n">fn</span><span class="p">(</span><span class="n">event</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">_is_match</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fn_events</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="nb">len</span><span class="p">(</span><span class="n">fn_events</span><span class="p">)</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="mi">0</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="bp">True</span><span class="">
</span><span class="">        </span><span class="k">for</span><span class=""> </span><span class="n">fn_event</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">fn_events</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">if</span><span class=""> </span><span class="n">is_prefix</span><span class="p">(</span><span class="n">fn_event</span><span class="o">.</span><span class="n">split</span><span class="p">(</span><span class="s2">"</span><span class="s2">.</span><span class="s2">"</span><span class="p">)</span><span class="p">,</span><span class=""> </span><span class="n">event</span><span class="o">.</span><span class="n">split</span><span class="p">(</span><span class="s2">"</span><span class="s2">.</span><span class="s2">"</span><span class="p">)</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">                </span><span class="k">return</span><span class=""> </span><span class="bp">True</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">False</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">is_prefix</span><span class="p">(</span><span class="n">left</span><span class="p">,</span><span class=""> </span><span class="n">right</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">left</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">right</span><span class="p">[</span><span class="p">:</span><span class="nb">len</span><span class="p">(</span><span class="n">left</span><span class="p">)</span><span class="p">]</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;classes&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">class</span><span class=""> </span><span class="nc">Listener</span><span class="p">(</span><span class="nb">object</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="fm">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="n">events</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">fn</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">fn</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">events</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">events</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">observable</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">
</span><span class="">    </span><span class="k">def</span><span class=""> </span><span class="nf">set_observable</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class=""> </span><span class="n">observable</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="bp">self</span><span class="o">.</span><span class="n">observable</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="bp">self</span><span class="o">.</span><span class="n">observable</span><span class="o">.</span><span class="n">unlisten</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">events</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">observable</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">observable</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">observable</span><span class="o">.</span><span class="n">listen</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">fn</span><span class="p">,</span><span class=""> </span><span class="o">*</span><span class="bp">self</span><span class="o">.</span><span class="n">events</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="bp">self</span><span class="o">.</span><span class="n">fn</span><span class="p">(</span><span class="s2">"</span><span class="s2">"</span><span class="p">)</span><span class="">
</span></pre></div>

<h3><a name="b73b797520334653a235e5e6a077e573"></a>

JSON serialization mechanisms</h3>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">load_json_from_file</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="nb">open</span><span class="p">(</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">r</span><span class="s2">"</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">json</span><span class="o">.</span><span class="n">load</span><span class="p">(</span><span class="n">f</span><span class="p">)</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">write_json_to_file</span><span class="p">(</span><span class="n">path</span><span class="p">,</span><span class=""> </span><span class="n">data</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="n">safely_write_file</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">json</span><span class="o">.</span><span class="n">dump</span><span class="p">(</span><span class="">
</span><span class="">            </span><span class="n">data</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="p">,</span><span class="">
</span><span class="">            </span><span class="n">sort_keys</span><span class="o">=</span><span class="bp">True</span><span class="p">,</span><span class=""> </span><span class="n">indent</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span><span class=""> </span><span class="n">separators</span><span class="o">=</span><span class="p">(</span><span class="s1">'</span><span class="s1">,</span><span class="s1">'</span><span class="p">,</span><span class=""> </span><span class="s1">'</span><span class="s1">:</span><span class="s1">'</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="p">)</span><span class="">
</span></pre></div>

<p>This functions tries to write safely to a file. The file will either be completely written or not modified at all. It is achieved by first writing to a temporary file and then performing a rename.</p>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="nd">@contextlib.contextmanager</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">safely_write_file</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="n">tempfile</span><span class="o">.</span><span class="n">NamedTemporaryFile</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="nb">dir</span><span class="o">=</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">dirname</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">prefix</span><span class="o">=</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">basename</span><span class="p">(</span><span class="n">path</span><span class="p">)</span><span class=""> </span><span class="o">+</span><span class=""> </span><span class="s2">"</span><span class="s2">.tmp</span><span class="s2">"</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">delete</span><span class="o">=</span><span class="bp">False</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">tmp</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">yield</span><span class=""> </span><span class="n">tmp</span><span class="">
</span><span class="">    </span><span class="n">os</span><span class="o">.</span><span class="n">rename</span><span class="p">(</span><span class="n">tmp</span><span class="o">.</span><span class="n">name</span><span class="p">,</span><span class=""> </span><span class="n">path</span><span class="p">)</span><span class="">
</span></pre></div>

<h3><a name="fddc930e6caa4a38bf6e7259e6e1034a"></a>

Functions</h3>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">genid</span><span class="p">(</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">uuid</span><span class="o">.</span><span class="n">uuid4</span><span class="p">(</span><span class="p">)</span><span class="o">.</span><span class="n">hex</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">create_font</span><span class="p">(</span><span class="n">monospace</span><span class="o">=</span><span class="bp">False</span><span class="p">,</span><span class=""> </span><span class="n">size</span><span class="o">=</span><span class="mi">10</span><span class="p">,</span><span class=""> </span><span class="n">bold</span><span class="o">=</span><span class="bp">False</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">Font</span><span class="p">(</span><span class="">
</span><span class="">        </span><span class="n">size</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">FONTFAMILY_TELETYPE</span><span class=""> </span><span class="k">if</span><span class=""> </span><span class="n">monospace</span><span class=""> </span><span class="k">else</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">FONTFAMILY_DEFAULT</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">FONTSTYLE_NORMAL</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="n">wx</span><span class="o">.</span><span class="n">FONTWEIGHT_BOLD</span><span class=""> </span><span class="k">if</span><span class=""> </span><span class="n">bold</span><span class=""> </span><span class="k">else</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">FONTWEIGHT_NORMAL</span><span class="p">,</span><span class="">
</span><span class="">        </span><span class="bp">False</span><span class="">
</span><span class="">    </span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">find_first</span><span class="p">(</span><span class="n">items</span><span class="p">,</span><span class=""> </span><span class="n">action</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">item</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="n">items</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">result</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">action</span><span class="p">(</span><span class="n">item</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">result</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="n">result</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">pairs</span><span class="p">(</span><span class="n">items</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="nb">zip</span><span class="p">(</span><span class="n">items</span><span class="p">,</span><span class=""> </span><span class="n">items</span><span class="p">[</span><span class="mi">1</span><span class="p">:</span><span class="p">]</span><span class="o">+</span><span class="p">[</span><span class="bp">None</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">min_or_none</span><span class="p">(</span><span class="n">items</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">if</span><span class=""> </span><span class="ow">not</span><span class=""> </span><span class="n">items</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="bp">None</span><span class="">
</span><span class="">    </span><span class="k">return</span><span class=""> </span><span class="nb">min</span><span class="p">(</span><span class="n">items</span><span class="p">,</span><span class=""> </span><span class="n">key</span><span class="o">=</span><span class="n">key</span><span class="p">)</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">def</span><span class=""> </span><span class="nf">index_with_id</span><span class="p">(</span><span class="n">items</span><span class="p">,</span><span class=""> </span><span class="n">item_id</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">for</span><span class=""> </span><span class="n">index</span><span class="p">,</span><span class=""> </span><span class="n">item</span><span class=""> </span><span class="ow">in</span><span class=""> </span><span class="nb">enumerate</span><span class="p">(</span><span class="n">items</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="k">if</span><span class=""> </span><span class="n">item</span><span class="p">[</span><span class="s2">"</span><span class="s2">id</span><span class="s2">"</span><span class="p">]</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="n">item_id</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="k">return</span><span class=""> </span><span class="n">index</span><span class="">
</span></pre></div>

<p><code>rliterate.py / &lt;&lt;functions&gt;&gt;</code></p>

<div class="highlight"><pre><span class="k">def</span><span class=""> </span><span class="nf">edit_in_gvim</span><span class="p">(</span><span class="n">text</span><span class="p">,</span><span class=""> </span><span class="n">filename</span><span class="p">)</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="k">with</span><span class=""> </span><span class="n">tempfile</span><span class="o">.</span><span class="n">NamedTemporaryFile</span><span class="p">(</span><span class="n">suffix</span><span class="o">=</span><span class="s2">"</span><span class="s2">-rliterate-external-</span><span class="s2">"</span><span class="o">+</span><span class="n">filename</span><span class="p">)</span><span class=""> </span><span class="k">as</span><span class=""> </span><span class="n">f</span><span class="p">:</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">text</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">flush</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">p</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">subprocess</span><span class="o">.</span><span class="n">Popen</span><span class="p">(</span><span class="p">[</span><span class="s2">"</span><span class="s2">gvim</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="s2">"</span><span class="s2">--nofork</span><span class="s2">"</span><span class="p">,</span><span class=""> </span><span class="n">f</span><span class="o">.</span><span class="n">name</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">while</span><span class=""> </span><span class="n">p</span><span class="o">.</span><span class="n">poll</span><span class="p">(</span><span class="p">)</span><span class=""> </span><span class="ow">is</span><span class=""> </span><span class="bp">None</span><span class="p">:</span><span class="">
</span><span class="">            </span><span class="n">wx</span><span class="o">.</span><span class="n">Yield</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">            </span><span class="n">time</span><span class="o">.</span><span class="n">sleep</span><span class="p">(</span><span class="mf">0.1</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="n">f</span><span class="o">.</span><span class="n">seek</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span><span class="">
</span><span class="">        </span><span class="k">return</span><span class=""> </span><span class="n">f</span><span class="o">.</span><span class="n">read</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h3><a name="745dcf0d093a4f179dc7fbe1dc8b7bdd"></a>

Main Python file</h3>

<p><code>rliterate.py</code></p>

<div class="highlight"><pre><span class="kn">from</span><span class=""> </span><span class="nn">collections</span><span class=""> </span><span class="kn">import</span><span class=""> </span><span class="n">defaultdict</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">contextlib</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">json</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">os</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">re</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">subprocess</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">sys</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">tempfile</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">time</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">uuid</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">webbrowser</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">xml.sax.saxutils</span><span class="">
</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">pygments.lexers</span><span class="">
</span><span class="kn">from</span><span class=""> </span><span class="nn">pygments.token</span><span class=""> </span><span class="kn">import</span><span class=""> </span><span class="n">Token</span><span class="p">,</span><span class=""> </span><span class="n">STANDARD_TYPES</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">wx</span><span class="">
</span><span class="kn">import</span><span class=""> </span><span class="nn">wx.lib.newevent</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="o">&lt;&lt;</span><span class="n">constants</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="o">&lt;&lt;</span><span class="n">base</span><span class=""> </span><span class="n">classes</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="o">&lt;&lt;</span><span class="n">classes</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="o">&lt;&lt;</span><span class="n">functions</span><span class="o">&gt;&gt;</span><span class="">
</span><span class="">
</span><span class="">
</span><span class="k">if</span><span class=""> </span><span class="vm">__name__</span><span class=""> </span><span class="o">==</span><span class=""> </span><span class="s2">"</span><span class="s2">__main__</span><span class="s2">"</span><span class="p">:</span><span class="">
</span><span class="">    </span><span class="n">app</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">wx</span><span class="o">.</span><span class="n">App</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">main_frame</span><span class=""> </span><span class="o">=</span><span class=""> </span><span class="n">MainFrame</span><span class="p">(</span><span class="n">filepath</span><span class="o">=</span><span class="n">sys</span><span class="o">.</span><span class="n">argv</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">main_frame</span><span class="o">.</span><span class="n">Show</span><span class="p">(</span><span class="p">)</span><span class="">
</span><span class="">    </span><span class="n">app</span><span class="o">.</span><span class="n">MainLoop</span><span class="p">(</span><span class="p">)</span><span class="">
</span></pre></div>

<h2><a name="cc36000ed12f4bfe88cefa2987fdb5cd"></a>

Things I learned</h2>

<p>DoDragDrop must be called from within an event handler.</p>

<p>Font must be assigned before setting a label, otherwise size calculations will be wrong? Must investigate further.</p>

<h2><a name="0a165f3042ee4350b9bebb61213b44c5"></a>

TODO</h2>

<p>Random notes of what I might want to work on in the future.</p>

<p>* Multiple editors can be opened (only last opened is saved)
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
* Editors: highlight the word/fragment that is double clicked
* Paragraph editor has comment: extract comment to prose</p>

