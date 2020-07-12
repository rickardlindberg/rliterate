import sys

SUPPORT = 'class _Grammar(object):\n\n    def _or(self, matchers):\n        original_stream = self._stream\n        for matcher in matchers:\n            try:\n                return matcher()\n            except _MatchError:\n                self._stream = original_stream\n        original_stream.fail("no choice matched")\n\n    def _and(self, matchers):\n        result = None\n        for matcher in matchers:\n            result = matcher()\n        return result\n\n    def _star(self, matcher):\n        result = []\n        while True:\n            original_stream = self._stream\n            try:\n                result.append(matcher())\n            except _MatchError:\n                self._stream = original_stream\n                return _SemanticAction(lambda: [x.eval() for x in result])\n\n    def _not(self, matcher):\n        original_stream = self._stream\n        try:\n            matcher()\n        except _MatchError:\n            return _SemanticAction(lambda: None)\n        else:\n            original_stream.fail("match found")\n        finally:\n            self._stream = original_stream\n\n    def _match_rule(self, rule_name):\n        key = (rule_name, self._stream.position())\n        if key in self._memo:\n            result, _, self._stream = self._memo[key]\n        else:\n            start = self._stream\n            result = getattr(self, "_rule_{}".format(rule_name))()\n            end = self._stream\n            self._memo[key] = (result, start, end)\n        return result\n\n    def _match_range(self, start, end):\n        original_stream = self._stream\n        next_objext, self._stream = self._stream.next()\n        if next_objext >= start and next_objext <= end:\n            return _SemanticAction(lambda: next_objext)\n        else:\n            original_stream.fail(\n                "expected range {!r}-{!r} but found {!r}".format(start, end, next_objext)\n            )\n\n    def _match_string(self, string):\n        original_stream = self._stream\n        next_object, self._stream = self._stream.next()\n        if next_object == string:\n            return _SemanticAction(lambda: string)\n        else:\n            original_stream.fail(\n                "expected {!r} but found {!r}".format(string, next_object)\n            )\n\n    def _match_charseq(self, charseq):\n        for char in charseq:\n            original_stream = self._stream\n            next_object, self._stream = self._stream.next()\n            if next_object != char:\n                original_stream.fail(\n                    "expected {!r} but found {!r}".format(char, next_object)\n                )\n        return _SemanticAction(lambda: charseq)\n\n    def _match_any(self):\n        next_object, self._stream = self._stream.next()\n        return _SemanticAction(lambda: next_object)\n\n    def _match_list(self, matcher):\n        original_stream = self._stream\n        next_object, next_stream = self._stream.next()\n        if isinstance(next_object, list):\n            self._stream = self._stream.nested(next_object)\n            matcher()\n            if self._stream.is_at_end():\n                self._stream = next_stream\n                return _SemanticAction(lambda: next_object)\n        original_stream.fail("list match failed")\n\n    def run(self, rule_name, input_object):\n        self._memo = _Memo()\n        self._stream = _Stream.from_object(self._memo, input_object)\n        result = self._match_rule(rule_name).eval()\n        if isinstance(result, _Builder):\n            return result.build_string()\n        else:\n            return result\n\nclass _Vars(dict):\n\n    def bind(self, name, value):\n        self[name] = value\n        return value\n\n    def lookup(self, name):\n        return self[name]\n\nclass _SemanticAction(object):\n\n    def __init__(self, fn):\n        self.fn = fn\n\n    def eval(self):\n        return self.fn()\n\nclass _Builder(object):\n\n    def __init__(self):\n        self.parent = None\n        self.labels = {}\n\n    def lookup(self, name):\n        if name in self.labels:\n            return self.labels[name]\n        elif self.parent is None:\n            raise Exception("{!r} not found".format(name))\n        else:\n            return self.parent.lookup(name)\n\n    def build_string(self):\n        output = _Output()\n        self.write(output)\n        return output.value\n\n    @classmethod\n    def create(self, item):\n        if isinstance(item, _Builder):\n            return item\n        elif isinstance(item, list):\n            return _ListBuilder([_Builder.create(x) for x in item])\n        else:\n            return _AtomBuilder(item)\n\nclass _Output(object):\n\n    def __init__(self, parent=None, indentation=0):\n        self.label_counter = 0\n        self.parts = []\n        self.forks = {}\n        self.parent = parent\n        self.indentation = indentation\n\n    def new_label(self, name):\n        if self.parent is None:\n            label = "_{}{}".format(name, self.label_counter)\n            self.label_counter += 1\n            return label\n        else:\n            return self.parent.new_label(name)\n\n    @property\n    def value(self):\n        return "".join(str(x) for x in self.parts)\n\n    def __str__(self):\n        return self.value\n\n    def fork(self, name):\n        output = _Output(self, self.indentation)\n        self.forks[name] = output\n        self.parts.append(output)\n\n    def get(self, name):\n        if name in self.forks:\n            return self.forks[name]\n        elif self.parent is None:\n            raise Exception("{!r} not found".format(name))\n        else:\n            return self.parent.get(name)\n\n    def write(self, value):\n        for ch in value:\n            if (not self.parts or self.parts[-1] == "\\n" or isinstance(self.parts[-1], _Output)) and ch != "\\n":\n                self.parts.append("    "*self.indentation)\n            self.parts.append(ch)\n\nclass _ListBuilder(_Builder):\n\n    def __init__(self, builders):\n        _Builder.__init__(self)\n        self.builders = builders\n        for builder in self.builders:\n            builder.parent = self\n\n    def write(self, output):\n        for builder in self.builders:\n            builder.write(output)\n\nclass _AtomBuilder(_Builder):\n\n    def __init__(self, atom):\n        _Builder.__init__(self)\n        self.atom = atom\n\n    def write(self, output):\n        output.write(str(self.atom))\n\nclass _CreateLabel(_Builder):\n\n    def __init__(self, name):\n        _Builder.__init__(self)\n        self.name = name\n\n    def write(self, output):\n        self.parent.labels[self.name] = output.new_label(self.name)\n\nclass _UseLabel(_Builder):\n\n    def __init__(self, name):\n        _Builder.__init__(self)\n        self.name = name\n\n    def write(self, output):\n        output.write(self.lookup(self.name))\n\nclass _ForkBuilder(_Builder):\n\n    def __init__(self, name):\n        _Builder.__init__(self)\n        self.name = name\n\n    def write(self, output):\n        output.fork(self.name)\n\nclass _AtBuilder(_Builder):\n\n    def __init__(self, name, builder):\n        _Builder.__init__(self)\n        self.name = name\n        self.builder = builder\n        self.builder.parent = self\n\n    def write(self, output):\n        self.builder.write(output.get(self.name))\n\nclass _IndentBuilder(_Builder):\n\n    def write(self, output):\n        output.indentation += 1\n\nclass _DedentBuilder(_Builder):\n\n    def write(self, output):\n        output.indentation -= 1\n\nclass _Memo(dict):\n\n    def __init__(self):\n        dict.__init__(self)\n        self._latest_stream = _ObjectStream(self, [], position=-1)\n        self._latest_message = ""\n\n    def describe(self):\n        items = []\n        for (rule_name, _), (_, start, end) in self.items():\n            if end > start:\n                items.append((rule_name, start, end))\n        items.sort(key=lambda item: (item[2].position(), item[1].position()))\n        message = []\n        for item in items:\n            message.append("matched {: <20} {} -> {}\\n".format(*item))\n        message.append("\\n")\n        message.append("ERROR: {}: {}\\n".format(\n            self._latest_stream,\n            self._latest_message\n        ))\n        return "".join(message)\n\n    def fail(self, stream, message):\n        if stream.position() >= self._latest_stream.position():\n            self._latest_stream = stream\n            self._latest_message = message\n        raise _MatchError(self)\n\nclass _MatchError(Exception):\n\n    def __init__(self, memo):\n        Exception.__init__(self)\n        self._memo = memo\n\n    def describe(self):\n        return self._memo.describe()\n\nclass _Stream(object):\n\n    @classmethod\n    def from_object(cls, memo, input_object):\n        if isinstance(input_object, str):\n            return _CharStream(memo, list(input_object))\n        else:\n            return _ObjectStream(memo, [input_object])\n\n    def __init__(self, memo, objects):\n        self._memo = memo\n        self._objects = objects\n\n    def fail(self, message):\n        self._memo.fail(self, message)\n\n    def next(self):\n        if self.is_at_end():\n            self.fail("not eof")\n        next_object = self._objects[0]\n        return (\n            next_object,\n            self._advance(next_object, self._objects[1:]),\n        )\n\n    def is_at_end(self):\n        return len(self._objects) == 0\n\nclass _CharStream(_Stream):\n\n    def __init__(self, memo, objects, line=1, column=1):\n        _Stream.__init__(self, memo, objects)\n        self._line = line\n        self._column = column\n\n    def position(self):\n        return (self._line, self._column)\n\n    def _advance(self, next_object, objects):\n        if next_object == "\\n":\n            return _CharStream(self._memo, objects, self._line+1, 1)\n        else:\n            return _CharStream(self._memo, objects, self._line, self._column+1)\n\n    def __str__(self):\n        return "L{:03d}:C{:03d}".format(self._line, self._column)\n\nclass _ObjectStream(_Stream):\n\n    def __init__(self, memo, objects, parent=(), position=0):\n        _Stream.__init__(self, memo, objects)\n        self._parent = parent\n        self._position = position\n\n    def position(self):\n        return self._parent + (self._position,)\n\n    def nested(self, input_object):\n        return _ObjectStream(self._memo, input_object, self._parent+(self._position,))\n\n    def _advance(self, next_object, objects):\n        return _ObjectStream(self._memo, objects, self._parent, self._position+1)\n\n    def __str__(self):\n        return "[{}]".format(", ".join(str(x) for x in self.position()))\n'

class _Grammar(object):

    def _or(self, matchers):
        original_stream = self._stream
        for matcher in matchers:
            try:
                return matcher()
            except _MatchError:
                self._stream = original_stream
        original_stream.fail("no choice matched")

    def _and(self, matchers):
        result = None
        for matcher in matchers:
            result = matcher()
        return result

    def _star(self, matcher):
        result = []
        while True:
            original_stream = self._stream
            try:
                result.append(matcher())
            except _MatchError:
                self._stream = original_stream
                return _SemanticAction(lambda: [x.eval() for x in result])

    def _not(self, matcher):
        original_stream = self._stream
        try:
            matcher()
        except _MatchError:
            return _SemanticAction(lambda: None)
        else:
            original_stream.fail("match found")
        finally:
            self._stream = original_stream

    def _match_rule(self, rule_name):
        key = (rule_name, self._stream.position())
        if key in self._memo:
            result, _, self._stream = self._memo[key]
        else:
            start = self._stream
            result = getattr(self, "_rule_{}".format(rule_name))()
            end = self._stream
            self._memo[key] = (result, start, end)
        return result

    def _match_range(self, start, end):
        original_stream = self._stream
        next_objext, self._stream = self._stream.next()
        if next_objext >= start and next_objext <= end:
            return _SemanticAction(lambda: next_objext)
        else:
            original_stream.fail(
                "expected range {!r}-{!r} but found {!r}".format(start, end, next_objext)
            )

    def _match_string(self, string):
        original_stream = self._stream
        next_object, self._stream = self._stream.next()
        if next_object == string:
            return _SemanticAction(lambda: string)
        else:
            original_stream.fail(
                "expected {!r} but found {!r}".format(string, next_object)
            )

    def _match_charseq(self, charseq):
        for char in charseq:
            original_stream = self._stream
            next_object, self._stream = self._stream.next()
            if next_object != char:
                original_stream.fail(
                    "expected {!r} but found {!r}".format(char, next_object)
                )
        return _SemanticAction(lambda: charseq)

    def _match_any(self):
        next_object, self._stream = self._stream.next()
        return _SemanticAction(lambda: next_object)

    def _match_list(self, matcher):
        original_stream = self._stream
        next_object, next_stream = self._stream.next()
        if isinstance(next_object, list):
            self._stream = self._stream.nested(next_object)
            matcher()
            if self._stream.is_at_end():
                self._stream = next_stream
                return _SemanticAction(lambda: next_object)
        original_stream.fail("list match failed")

    def run(self, rule_name, input_object):
        self._memo = _Memo()
        self._stream = _Stream.from_object(self._memo, input_object)
        result = self._match_rule(rule_name).eval()
        if isinstance(result, _Builder):
            return result.build_string()
        else:
            return result

class _Vars(dict):

    def bind(self, name, value):
        self[name] = value
        return value

    def lookup(self, name):
        return self[name]

class _SemanticAction(object):

    def __init__(self, fn):
        self.fn = fn

    def eval(self):
        return self.fn()

class _Builder(object):

    def __init__(self):
        self.parent = None
        self.labels = {}

    def lookup(self, name):
        if name in self.labels:
            return self.labels[name]
        elif self.parent is None:
            raise Exception("{!r} not found".format(name))
        else:
            return self.parent.lookup(name)

    def build_string(self):
        output = _Output()
        self.write(output)
        return output.value

    @classmethod
    def create(self, item):
        if isinstance(item, _Builder):
            return item
        elif isinstance(item, list):
            return _ListBuilder([_Builder.create(x) for x in item])
        else:
            return _AtomBuilder(item)

class _Output(object):

    def __init__(self, parent=None, indentation=0):
        self.label_counter = 0
        self.parts = []
        self.forks = {}
        self.parent = parent
        self.indentation = indentation

    def new_label(self, name):
        if self.parent is None:
            label = "_{}{}".format(name, self.label_counter)
            self.label_counter += 1
            return label
        else:
            return self.parent.new_label(name)

    @property
    def value(self):
        return "".join(str(x) for x in self.parts)

    def __str__(self):
        return self.value

    def fork(self, name):
        output = _Output(self, self.indentation)
        self.forks[name] = output
        self.parts.append(output)

    def get(self, name):
        if name in self.forks:
            return self.forks[name]
        elif self.parent is None:
            raise Exception("{!r} not found".format(name))
        else:
            return self.parent.get(name)

    def write(self, value):
        for ch in value:
            if (not self.parts or self.parts[-1] == "\n" or isinstance(self.parts[-1], _Output)) and ch != "\n":
                self.parts.append("    "*self.indentation)
            self.parts.append(ch)

class _ListBuilder(_Builder):

    def __init__(self, builders):
        _Builder.__init__(self)
        self.builders = builders
        for builder in self.builders:
            builder.parent = self

    def write(self, output):
        for builder in self.builders:
            builder.write(output)

class _AtomBuilder(_Builder):

    def __init__(self, atom):
        _Builder.__init__(self)
        self.atom = atom

    def write(self, output):
        output.write(str(self.atom))

class _CreateLabel(_Builder):

    def __init__(self, name):
        _Builder.__init__(self)
        self.name = name

    def write(self, output):
        self.parent.labels[self.name] = output.new_label(self.name)

class _UseLabel(_Builder):

    def __init__(self, name):
        _Builder.__init__(self)
        self.name = name

    def write(self, output):
        output.write(self.lookup(self.name))

class _ForkBuilder(_Builder):

    def __init__(self, name):
        _Builder.__init__(self)
        self.name = name

    def write(self, output):
        output.fork(self.name)

class _AtBuilder(_Builder):

    def __init__(self, name, builder):
        _Builder.__init__(self)
        self.name = name
        self.builder = builder
        self.builder.parent = self

    def write(self, output):
        self.builder.write(output.get(self.name))

class _IndentBuilder(_Builder):

    def write(self, output):
        output.indentation += 1

class _DedentBuilder(_Builder):

    def write(self, output):
        output.indentation -= 1

class _Memo(dict):

    def __init__(self):
        dict.__init__(self)
        self._latest_stream = _ObjectStream(self, [], position=-1)
        self._latest_message = ""

    def describe(self):
        items = []
        for (rule_name, _), (_, start, end) in self.items():
            if end > start:
                items.append((rule_name, start, end))
        items.sort(key=lambda item: (item[2].position(), item[1].position()))
        message = []
        for item in items:
            message.append("matched {: <20} {} -> {}\n".format(*item))
        message.append("\n")
        message.append("ERROR: {}: {}\n".format(
            self._latest_stream,
            self._latest_message
        ))
        return "".join(message)

    def fail(self, stream, message):
        if stream.position() >= self._latest_stream.position():
            self._latest_stream = stream
            self._latest_message = message
        raise _MatchError(self)

class _MatchError(Exception):

    def __init__(self, memo):
        Exception.__init__(self)
        self._memo = memo

    def describe(self):
        return self._memo.describe()

class _Stream(object):

    @classmethod
    def from_object(cls, memo, input_object):
        if isinstance(input_object, str):
            return _CharStream(memo, list(input_object))
        else:
            return _ObjectStream(memo, [input_object])

    def __init__(self, memo, objects):
        self._memo = memo
        self._objects = objects

    def fail(self, message):
        self._memo.fail(self, message)

    def next(self):
        if self.is_at_end():
            self.fail("not eof")
        next_object = self._objects[0]
        return (
            next_object,
            self._advance(next_object, self._objects[1:]),
        )

    def is_at_end(self):
        return len(self._objects) == 0

class _CharStream(_Stream):

    def __init__(self, memo, objects, line=1, column=1):
        _Stream.__init__(self, memo, objects)
        self._line = line
        self._column = column

    def position(self):
        return (self._line, self._column)

    def _advance(self, next_object, objects):
        if next_object == "\n":
            return _CharStream(self._memo, objects, self._line+1, 1)
        else:
            return _CharStream(self._memo, objects, self._line, self._column+1)

    def __str__(self):
        return "L{:03d}:C{:03d}".format(self._line, self._column)

class _ObjectStream(_Stream):

    def __init__(self, memo, objects, parent=(), position=0):
        _Stream.__init__(self, memo, objects)
        self._parent = parent
        self._position = position

    def position(self):
        return self._parent + (self._position,)

    def nested(self, input_object):
        return _ObjectStream(self._memo, input_object, self._parent+(self._position,))

    def _advance(self, next_object, objects):
        return _ObjectStream(self._memo, objects, self._parent, self._position+1)

    def __str__(self):
        return "[{}]".format(", ".join(str(x) for x in self.position()))

class Parser(_Grammar):

    def _rule_grammar(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('ys', (lambda:
                                        self._star((lambda:
                                            self._match_rule('rule')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Grammar']+[_vars.lookup('x').eval()]+_vars.lookup('ys').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_rule(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('=')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('choice')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Rule']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_choice(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._or([
                                        (lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._match_rule('space')
                                                                ),
                                                                (lambda:
                                                                    self._match_charseq('|')
                                                                ),
                                                            ])
                                                        )()
                                                    )(_Vars())
                                                ),
                                            ])
                                        ),
                                        (lambda:
                                            self._and([
                                            ])
                                        ),
                                    ])
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('sequence')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._match_rule('space')
                                                                ),
                                                                (lambda:
                                                                    self._match_charseq('|')
                                                                ),
                                                                (lambda:
                                                                    self._match_rule('sequence')
                                                                ),
                                                            ])
                                                        )()
                                                    )(_Vars())
                                                ),
                                            ])
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Or']+[_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_sequence(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('expr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Scope']+[(['And']+[_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[])]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_expr(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr1')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq(':')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Bind']+[_vars.lookup('y').eval()]+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('expr1')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_expr1(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr2')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('*')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Star']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr2')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('?')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Or']+[_vars.lookup('x').eval()]+[(['And']+[])]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('!')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr2')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Not']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('expr2')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_expr2(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('->')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('hostExpr')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['SemanticAction']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._or([
                                            (lambda:
                                                (lambda _vars:
                                                    (lambda:
                                                        self._and([
                                                            (lambda:
                                                                self._match_rule('space')
                                                            ),
                                                            (lambda:
                                                                self._match_charseq('=')
                                                            ),
                                                        ])
                                                    )()
                                                )(_Vars())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchRule']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('char')
                                    )())
                                ),
                                (lambda:
                                    self._match_charseq('-')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('char')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchRange']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('string')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchString']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('charseq')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchCharseq']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('.')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchAny']+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('choice')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _vars.lookup('x').eval())
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('[')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('expr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['MatchList']+[(['And']+_vars.lookup('xs').eval()+[])]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_hostExpr(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('string')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['String']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('[')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('hostExprListItem')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['List']+_vars.lookup('xs').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('buildExpr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Builder']+_vars.lookup('xs').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('ys', (lambda:
                                        self._star((lambda:
                                            self._match_rule('hostExpr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['FnCall']+[_vars.lookup('x').eval()]+_vars.lookup('ys').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['VarLookup']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_hostExprListItem(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('~')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('hostExpr')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['ListItemSplice']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('hostExpr')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_buildExpr(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('#')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['Fork']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('%%')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['CreateLabel']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('%')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['UseLabel']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('@')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('buildExpr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['At']+[_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('>')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['IndentBuilder']+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    self._match_charseq('<')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['DedentBuilder']+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('hostExpr')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_string(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('"')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._not((lambda:
                                                                        self._match_charseq('"')
                                                                    ))
                                                                ),
                                                                (lambda:
                                                                    self._match_rule('innerChar')
                                                                ),
                                                            ])
                                                        )()
                                                    )(_Vars())
                                                ),
                                            ])
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_charseq('"')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: join(
                                        _vars.lookup('xs').eval(),
                                    ))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_charseq(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq("'")
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._not((lambda:
                                                                        self._match_charseq("'")
                                                                    ))
                                                                ),
                                                                (lambda:
                                                                    self._match_rule('innerChar')
                                                                ),
                                                            ])
                                                        )()
                                                    )(_Vars())
                                                ),
                                            ])
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_charseq("'")
                                ),
                                (lambda:
                                    _SemanticAction(lambda: join(
                                        _vars.lookup('xs').eval(),
                                    ))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_char(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq("'")
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_charseq("'")
                                    ))
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('innerChar')
                                    )())
                                ),
                                (lambda:
                                    self._match_charseq("'")
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _vars.lookup('x').eval())
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_innerChar(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('\\')
                                ),
                                (lambda:
                                    self._match_rule('escape')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                self._match_any,
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_escape(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('\\')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: '\\')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq("'")
                                ),
                                (lambda:
                                    _SemanticAction(lambda: "'")
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('"')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: '"')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('n')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: '\n')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_name(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('space')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('nameStart')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('nameChar')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: join(
                                        ([_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]),
                                    ))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_nameStart(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_range('a', 'z')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_range('A', 'Z')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_nameChar(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_range('a', 'z')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_range('A', 'Z')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_range('0', '9')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_space(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._star((lambda:
                                        self._or([
                                            (lambda:
                                                (lambda _vars:
                                                    (lambda:
                                                        self._and([
                                                            (lambda:
                                                                self._match_charseq(' ')
                                                            ),
                                                        ])
                                                    )()
                                                )(_Vars())
                                            ),
                                            (lambda:
                                                (lambda _vars:
                                                    (lambda:
                                                        self._and([
                                                            (lambda:
                                                                self._match_charseq('\n')
                                                            ),
                                                        ])
                                                    )()
                                                )(_Vars())
                                            ),
                                        ])
                                    ))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

class CodeGenerator(_Grammar):

    def _rule_ast(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Grammar')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('ys', (lambda:
                                                    self._star((lambda:
                                                        self._match_rule('ast')
                                                    ))
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'class ',
                                        _vars.lookup('x').eval(),
                                        '(_Grammar):\n',
                                        _IndentBuilder(),
                                        _vars.lookup('ys').eval(),
                                        _DedentBuilder(),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Rule')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '\ndef _rule_',
                                        _vars.lookup('x').eval(),
                                        '(self):\n',
                                        _IndentBuilder(),
                                        'return ',
                                        _vars.lookup('y').eval(),
                                        '()\n',
                                        _DedentBuilder(),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchAny')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_any',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('String')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('List')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('astList')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Builder')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('astItems')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_Builder.create([',
                                        _vars.lookup('x').eval(),
                                        '])',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('At')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('astItems')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_AtBuilder(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ', _Builder.create([',
                                        _vars.lookup('y').eval(),
                                        ']))',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Fork')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_ForkBuilder(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('CreateLabel')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_CreateLabel(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('UseLabel')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_UseLabel(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('IndentBuilder')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_IndentBuilder()',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('DedentBuilder')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_DedentBuilder()',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('FnCall')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('astItems')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                        '(',
                                        _vars.lookup('y').eval(),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('VarLookup')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_vars.lookup(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ').eval()',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('astFnBody')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '(lambda:\n',
                                        _IndentBuilder(),
                                        _vars.lookup('x').eval(),
                                        _DedentBuilder(),
                                        '\n)',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astFnBody(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Or')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('astItems')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._or([',
                                        _vars.lookup('x').eval(),
                                        '])',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Scope')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '(lambda _vars:\n',
                                        _IndentBuilder(),
                                        _vars.lookup('x').eval(),
                                        _DedentBuilder(),
                                        '()\n)(_Vars())',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('And')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('astItems')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._and([',
                                        _vars.lookup('x').eval(),
                                        '])',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Bind')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_vars.bind(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ', ',
                                        _vars.lookup('y').eval(),
                                        '())',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Star')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._star(',
                                        _vars.lookup('x').eval(),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('Not')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._not(',
                                        _vars.lookup('x').eval(),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('SemanticAction')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '_SemanticAction(lambda: ',
                                        _vars.lookup('x').eval(),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchRule')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_rule(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchRange')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                            (lambda:
                                                _vars.bind('y', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_range(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ', ',
                                        repr(
                                            _vars.lookup('y').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchString')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_string(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchCharseq')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_charseq(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('MatchList')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'self._match_list(',
                                        _vars.lookup('x').eval(),
                                        ')',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astItems(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('astItem')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '\n',
                                        _IndentBuilder(),
                                        _vars.lookup('xs').eval(),
                                        _DedentBuilder(),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astItem(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('ast')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                        ',\n',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astList(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('astListItem')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '(',
                                        _vars.lookup('xs').eval(),
                                        '[])',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astListItem(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_list((lambda:
                                        self._and([
                                            (lambda:
                                                self._match_string('ListItemSplice')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                        '+',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('ast')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '[',
                                        _vars.lookup('x').eval(),
                                        ']+',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

join = "".join

def compile_grammar(grammar):
    parser = Parser()
    code_generator = CodeGenerator()
    return code_generator.run("ast", parser.run("grammar", grammar))

if __name__ == "__main__":
    if "--support" in sys.argv:
        sys.stdout.write(SUPPORT)
    else:
        try:
            sys.stdout.write(compile_grammar(sys.stdin.read()))
        except _MatchError as e:
            sys.stderr.write(e.describe())
            sys.exit(1)
