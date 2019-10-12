# This file is extracted from rliterate.rliterate.
# DO NOT EDIT MANUALLY!
import sys
import pprint

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
        if isinstance(input_object, basestring):
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

class GuiParser(_Grammar):

    def _rule_widget(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('containerType')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('z', (lambda:
                                        self._match_rule('boxType')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('as', (lambda:
                                        self._star((lambda:
                                            self._match_rule('body')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._not(self._match_any)
                                ),
                                (lambda:
                                    _SemanticAction(lambda: ([_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[([_vars.lookup('z').eval()]+[_vars.lookup('as').eval()]+[])]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_body(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('derived')
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
                                    self._match_rule('variable')
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
                                    self._match_rule('handler')
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
                                    self._match_rule('child')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_variable(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
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
                                    _SemanticAction(lambda: (['variable']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_derived(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('=')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['derived']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_box(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('boxType')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('child')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: ([_vars.lookup('x').eval()]+[_vars.lookup('xs').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_boxType(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%hbox')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'hbox')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%vbox')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'vbox')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_child(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('BoxSpace')
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['boxspace']+[_vars.lookup('x').eval()]+[]))
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
                                        self._match_rule('containerType')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('binding')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('zs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._match_rule('parameter')
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
                                                                    self._match_rule('handler')
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
                                                                    self._match_rule('sizerprop')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _vars.bind('ws', (lambda:
                                        self._match_rule('box')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['child']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[_vars.lookup('zs').eval()]+[([_vars.lookup('ws').eval()]+[])]+[]))
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
                                    self._not((lambda:
                                        self._match_rule('reserved')
                                    ))
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('binding')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('zs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._match_rule('parameter')
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
                                                                    self._match_rule('handler')
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
                                                                    self._match_rule('sizerprop')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['child']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[_vars.lookup('zs').eval()]+[([])]+[]))
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
                                    self._match_rule('for')
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('{')
                                ),
                                (lambda:
                                    _vars.bind('zs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('child')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('}')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['loop']+[_vars.lookup('x').eval()]+_vars.lookup('zs').eval()+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_binding(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('[')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['binding']+[_vars.lookup('x').eval()]+[]))
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
                                    _SemanticAction(lambda: ([]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_parameter(self):
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('=')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['parameter']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_handler(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('=')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['handler']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_sizerprop(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%border[')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(',')
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_rule('borderSide')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerBorder']+[_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%proportion[')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('expr')
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerProportion']+[_vars.lookup('x').eval()]+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%expand')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerExpand']+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%reserve_space_even_if_hidden')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerReserve']+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%align_center')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerAlignCenter']+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('%align_center_vertical')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['sizerAlignCenterVertical']+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_borderSide(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('side')
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
                                                                    self._match_rule('ws')
                                                                ),
                                                                (lambda:
                                                                    self._match_charseq('|')
                                                                ),
                                                                (lambda:
                                                                    self._match_rule('side')
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
                                    _SemanticAction(lambda: ([_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]))
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
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._or([
                                                (lambda:
                                                    (lambda _vars:
                                                        (lambda:
                                                            self._and([
                                                                (lambda:
                                                                    self._match_rule('ws')
                                                                ),
                                                                (lambda:
                                                                    self._match_charseq('.')
                                                                ),
                                                                (lambda:
                                                                    self._match_rule('expr1')
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
                                    _SemanticAction(lambda: (['get']+[_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]))
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
                                    self._match_rule('ws')
                                ),
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
                                                                self._match_any,
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
                                    _SemanticAction(lambda: (['string']+[join(
                                        _vars.lookup('xs').eval(),
                                    )]+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._or([
                                            (lambda:
                                                (lambda _vars:
                                                    (lambda:
                                                        self._and([
                                                            (lambda:
                                                                self._match_string('-')
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
                                                                _SemanticAction(lambda: '')
                                                            ),
                                                        ])
                                                    )()
                                                )(_Vars())
                                            ),
                                        ])
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('y', (lambda:
                                        self._match_range('0', '9')
                                    )())
                                ),
                                (lambda:
                                    _vars.bind('ys', (lambda:
                                        self._star((lambda:
                                            self._or([
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
                                        ))
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['int']+[int(
                                        join(
                                            ([_vars.lookup('x').eval()]+[_vars.lookup('y').eval()]+_vars.lookup('ys').eval()+[]),
                                        ),
                                    )]+[]))
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
                                    self._match_rule('ws')
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(']')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['list']+_vars.lookup('xs').eval()+[]))
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
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('(')
                                ),
                                (lambda:
                                    _vars.bind('xs', (lambda:
                                        self._star((lambda:
                                            self._match_rule('expr')
                                        ))
                                    )())
                                ),
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq(')')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['call']+[_vars.lookup('x').eval()]+_vars.lookup('xs').eval()+[]))
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
                                    _vars.bind('x', (lambda:
                                        self._match_rule('name')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: (['name']+[_vars.lookup('x').eval()]+[]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_reserved(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('containerType')
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
                                    self._match_rule('for')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_for(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    self._match_charseq('for')
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_side(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('side2')
                                    )())
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
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

    def _rule_side2(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('ALL')
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
                                    self._match_charseq('LEFT')
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
                                    self._match_charseq('RIGHT')
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
                                    self._match_charseq('TOP')
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
                                    self._match_charseq('BOTTOM')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_containerType(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('ws')
                                ),
                                (lambda:
                                    _vars.bind('x', (lambda:
                                        self._match_rule('containerType2')
                                    )())
                                ),
                                (lambda:
                                    self._not((lambda:
                                        self._match_rule('nameChar')
                                    ))
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

    def _rule_containerType2(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_charseq('frame')
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
                                    self._match_charseq('dialog')
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
                                    self._match_charseq('panel')
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
                                    self._match_charseq('scroll')
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
                                    self._match_charseq('vscroll')
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
                                    self._match_charseq('hscroll')
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
                                    self._match_rule('ws')
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
                                    self._match_rule('alpha')
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
                                    self._match_charseq('_')
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
                                    self._match_rule('alphanum')
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
                                    self._match_charseq('_')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_alpha(self):
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

    def _rule_alphanum(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_rule('alpha')
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

    def _rule_ws(self):
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
class WxGuiCodeGenerator(_Grammar):

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
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('topLevel')
                                                )())
                                            ),
                                            (lambda:
                                                _vars.bind('name', self._match_any())
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
                                        'class ',
                                        _vars.lookup('name').eval(),
                                        '(',
                                        _vars.lookup('x').eval(),
                                        '):\n',
                                        _IndentBuilder(),
                                        '\ndef _get_derived(self):\n',
                                        _IndentBuilder(),
                                        'return {\n',
                                        _IndentBuilder(),
                                        _ForkBuilder('derived'),
                                        _DedentBuilder(),
                                        '}\n',
                                        _DedentBuilder(),
                                        '\ndef _create_gui(self):\n',
                                        _IndentBuilder(),
                                        'self._root_panel = GuiFrameworkPanel(self, {})\n',
                                        'self.Sizer = wx.BoxSizer(wx.HORIZONTAL)\n',
                                        'self.Sizer.Add(self._root_panel, flag=wx.EXPAND, proportion=1)\n',
                                        'self._root_widget = GuiFrameworkWidgetInfo(self._root_panel, self)\n',
                                        'self._root_panel.SetFocus()\n',
                                        'self._child_root(self._root_widget, first=True)\n',
                                        _DedentBuilder(),
                                        '\ndef _update_gui(self):\n',
                                        _IndentBuilder(),
                                        'self._root_panel.SetFocus()\n',
                                        'self._child_root(self._root_widget)\n',
                                        _DedentBuilder(),
                                        '\ndef _child_root(self, parent, loopvar=None, first=False):\n',
                                        _IndentBuilder(),
                                        'parent.reset()\n',
                                        'handlers = []\n',
                                        _ForkBuilder('child'),
                                        'if first:\n',
                                        _IndentBuilder(),
                                        'parent.listen(handlers)\n',
                                        _DedentBuilder(),
                                        _DedentBuilder(),
                                        _ForkBuilder('methods'),
                                        _vars.lookup('y').eval(),
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
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('widget')
                                                )())
                                            ),
                                            (lambda:
                                                _vars.bind('name', self._match_any())
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
                                        'class ',
                                        _vars.lookup('name').eval(),
                                        '(',
                                        _vars.lookup('x').eval(),
                                        '):\n',
                                        _IndentBuilder(),
                                        '\ndef _get_derived(self):\n',
                                        _IndentBuilder(),
                                        'return {\n',
                                        _IndentBuilder(),
                                        _ForkBuilder('derived'),
                                        _DedentBuilder(),
                                        '}\n',
                                        _DedentBuilder(),
                                        '\ndef _create_gui(self):\n',
                                        _IndentBuilder(),
                                        'self._root_widget = GuiFrameworkWidgetInfo(self)\n',
                                        'self._child_root(self._root_widget, first=True)\n',
                                        _DedentBuilder(),
                                        '\ndef _update_gui(self):\n',
                                        _IndentBuilder(),
                                        'self._child_root(self._root_widget)\n',
                                        _DedentBuilder(),
                                        '\ndef _child_root(self, parent, loopvar=None, first=False):\n',
                                        _IndentBuilder(),
                                        'parent.reset()\n',
                                        'handlers = []\n',
                                        _ForkBuilder('child'),
                                        'if first:\n',
                                        _IndentBuilder(),
                                        'parent.listen(handlers)\n',
                                        _DedentBuilder(),
                                        _DedentBuilder(),
                                        _ForkBuilder('methods'),
                                        _vars.lookup('y').eval(),
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
                                                self._match_string('child')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._or([
                                                        (lambda:
                                                            (lambda _vars:
                                                                (lambda:
                                                                    self._and([
                                                                        (lambda:
                                                                            self._match_rule('widget')
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
                                                                            self._match_rule('ast')
                                                                        ),
                                                                    ])
                                                                )()
                                                            )(_Vars())
                                                        ),
                                                    ])
                                                )())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('binding')
                                                )())
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
                                                        (lambda:
                                                            _vars.bind('zs', (lambda:
                                                                self._star((lambda:
                                                                    self._match_rule('ast')
                                                                ))
                                                            )())
                                                        ),
                                                    ])
                                                ))
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
                                                        (lambda:
                                                            _vars.bind('ws', (lambda:
                                                                self._star((lambda:
                                                                    self._match_rule('ast')
                                                                ))
                                                            )())
                                                        ),
                                                    ])
                                                ))
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _CreateLabel('child'),
                                        _AtBuilder('child', _Builder.create([
                                            'self.',
                                            _UseLabel('child'),
                                            '(parent, loopvar)\n',
                                        ])),
                                        _AtBuilder('methods', _Builder.create([
                                            '\ndef ',
                                            _UseLabel('child'),
                                            '(self, parent, loopvar):\n',
                                            _IndentBuilder(),
                                            'handlers = []\n',
                                            'properties = {}\n',
                                            'sizer = {"flag": 0, "border": 0, "proportion": 0}\n',
                                            _ForkBuilder('child'),
                                            _DedentBuilder(),
                                            _vars.lookup('zs').eval(),
                                            _AtBuilder('child', _Builder.create([
                                                'widget = parent.add(',
                                                _vars.lookup('x').eval(),
                                                ', properties, handlers, sizer)\n',
                                                _vars.lookup('y').eval(),
                                                'parent = widget\n',
                                                'parent.reset()\n',
                                            ])),
                                            _ForkBuilder('methods'),
                                            _vars.lookup('ws').eval(),
                                        ])),
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
                                                self._match_string('loop')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                            (lambda:
                                                _vars.bind('zs', (lambda:
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
                                        _AtBuilder('child', _Builder.create([
                                            'parent.loop_start()\n',
                                            'try:\n',
                                            _IndentBuilder(),
                                            'for loopvar in ',
                                            _vars.lookup('x').eval(),
                                            ':\n',
                                            _IndentBuilder(),
                                            'pass\n',
                                        ])),
                                        _vars.lookup('zs').eval(),
                                        _AtBuilder('child', _Builder.create([
                                            _DedentBuilder(),
                                            _DedentBuilder(),
                                            'finally:\n',
                                            _IndentBuilder(),
                                            'parent.loop_end(self)\n',
                                            _DedentBuilder(),
                                        ])),
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
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('boxType')
                                                )())
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
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
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _CreateLabel('sizer'),
                                        _AtBuilder('child', _Builder.create([
                                            'parent.sizer = wx.BoxSizer(',
                                            _vars.lookup('x').eval(),
                                            ')\n',
                                        ])),
                                        _vars.lookup('ys').eval(),
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
                                                self._match_string('body')
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
                                                        (lambda:
                                                            _vars.bind('xs', (lambda:
                                                                self._star((lambda:
                                                                    self._match_rule('ast')
                                                                ))
                                                            )())
                                                        ),
                                                    ])
                                                ))
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
                                                        (lambda:
                                                            _vars.bind('zs', (lambda:
                                                                self._star((lambda:
                                                                    self._match_rule('ast')
                                                                ))
                                                            )())
                                                        ),
                                                    ])
                                                ))
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('xs').eval(),
                                        _vars.lookup('y').eval(),
                                        _vars.lookup('zs').eval(),
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
                                                self._match_string('boxspace')
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
                                        _AtBuilder('child', _Builder.create([
                                            'parent.add_space(',
                                            _vars.lookup('x').eval(),
                                            ')\n',
                                        ])),
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
                                                self._match_string('parameter')
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
                                        _AtBuilder('child', _Builder.create([
                                            'properties[',
                                            repr(
                                                _vars.lookup('x').eval(),
                                            ),
                                            '] = ',
                                            _vars.lookup('y').eval(),
                                            '\n',
                                        ])),
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
                                                self._match_string('handler')
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
                                        _AtBuilder('child', _Builder.create([
                                            'handlers.append((',
                                            repr(
                                                _vars.lookup('x').eval(),
                                            ),
                                            ', lambda event: ',
                                            _vars.lookup('y').eval(),
                                            '))\n',
                                        ])),
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
                                                self._match_string('get')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('astGetList')
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
                                                self._match_string('call')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                            (lambda:
                                                _vars.bind('y', (lambda:
                                                    self._match_rule('astList')
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
                                                self._match_string('name')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
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
                                                self._match_string('variable')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        '\n@property\n',
                                        'def ',
                                        _vars.lookup('x').eval(),
                                        '(self):\n',
                                        _IndentBuilder(),
                                        'return self.values["',
                                        _vars.lookup('x').eval(),
                                        '"]\n',
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
                                                self._match_string('derived')
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
                                        _AtBuilder('derived', _Builder.create([
                                            repr(
                                                _vars.lookup('x').eval(),
                                            ),
                                            ': ',
                                            _vars.lookup('y').eval(),
                                            ',\n',
                                        ])),
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
                                                self._match_string('string')
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
                                                self._match_string('int')
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
                                                self._match_string('list')
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
                                        '[',
                                        _vars.lookup('x').eval(),
                                        ']',
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
                                                self._match_string('sizerBorder')
                                            ),
                                            (lambda:
                                                _vars.bind('x', (lambda:
                                                    self._match_rule('ast')
                                                )())
                                            ),
                                            (lambda:
                                                self._match_list((lambda:
                                                    self._and([
                                                        (lambda:
                                                            _vars.bind('y', (lambda:
                                                                self._star((lambda:
                                                                    self._match_rule('border')
                                                                ))
                                                            )())
                                                        ),
                                                    ])
                                                ))
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["border"] = ',
                                            _vars.lookup('x').eval(),
                                            '\n',
                                            _vars.lookup('y').eval(),
                                        ])),
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
                                                self._match_string('sizerProportion')
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
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["proportion"] = ',
                                            _vars.lookup('x').eval(),
                                            '\n',
                                        ])),
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
                                                self._match_string('sizerExpand')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["flag"] |= wx.EXPAND\n',
                                        ])),
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
                                                self._match_string('sizerReserve')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["flag"] |= wx.RESERVE_SPACE_EVEN_IF_HIDDEN\n',
                                        ])),
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
                                                self._match_string('sizerAlignCenter')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["flag"] |= wx.ALIGN_CENTER\n',
                                        ])),
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
                                                self._match_string('sizerAlignCenterVertical')
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _AtBuilder('child', _Builder.create([
                                            'sizer["flag"] |= wx.ALIGN_CENTER_VERTICAL\n',
                                        ])),
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_widget(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_string('panel')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkPanel')
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
                                    self._match_string('scroll')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkScroll')
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
                                    self._match_string('vscroll')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkVScroll')
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
                                    self._match_string('hscroll')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkHScroll')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_topLevel(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_string('frame')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkFrame')
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
                                    self._match_string('dialog')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'GuiFrameworkDialog')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_border(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_string('ALL')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'sizer["flag"] |= wx.ALL\n',
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
                                    self._match_string('LEFT')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'sizer["flag"] |= wx.LEFT\n',
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
                                    self._match_string('RIGHT')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'sizer["flag"] |= wx.RIGHT\n',
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
                                    self._match_string('TOP')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'sizer["flag"] |= wx.TOP\n',
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
                                    self._match_string('BOTTOM')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'sizer["flag"] |= wx.BOTTOM\n',
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_boxType(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._match_string('hbox')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'wx.HORIZONTAL')
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
                                    self._match_string('vbox')
                                ),
                                (lambda:
                                    _SemanticAction(lambda: 'wx.VERTICAL')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astGetList(self):
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
                                    _vars.bind('y', (lambda:
                                        self._match_rule('astGetList')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                        '.',
                                        _vars.lookup('y').eval(),
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
                                    self._match_rule('ast')
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
                                    self._match_rule('astEmptyList')
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
                                    self._match_rule('astNonEmptyList')
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astEmptyList(self):
        return (lambda:
            self._or([
                (lambda:
                    (lambda _vars:
                        (lambda:
                            self._and([
                                (lambda:
                                    self._not(self._match_any)
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_astNonEmptyList(self):
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
                                    _vars.bind('y', (lambda:
                                        self._match_rule('astNonEmptyList')
                                    )())
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        _vars.lookup('x').eval(),
                                        ', ',
                                        _vars.lookup('y').eval(),
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
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

    def _rule_binding(self):
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
                                                self._match_string('binding')
                                            ),
                                            (lambda:
                                                _vars.bind('x', self._match_any())
                                            ),
                                        ])
                                    ))
                                ),
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                        'if parent.inside_loop:\n',
                                        _IndentBuilder(),
                                        'parent.add_loop_var(',
                                        repr(
                                            _vars.lookup('x').eval(),
                                        ),
                                        ', widget.widget)\n',
                                        _DedentBuilder(),
                                        'else:\n',
                                        _IndentBuilder(),
                                        'self.',
                                        _vars.lookup('x').eval(),
                                        ' = widget.widget\n',
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
                                self._match_any,
                                (lambda:
                                    _SemanticAction(lambda: _Builder.create([
                                    ]))
                                ),
                            ])
                        )()
                    )(_Vars())
                ),
            ])
        )()

join = "".join

if __name__ == "__main__":
    parser = GuiParser()
    wxcodegenerator = WxGuiCodeGenerator()
    try:
        ast = None
        ast = parser.run("widget", sys.stdin.read())
        code = wxcodegenerator.run("ast", ast)
        sys.stdout.write(code)
    except _MatchError as e:
        sys.stderr.write(pprint.pformat(ast))
        sys.stderr.write("\n")
        sys.stderr.write(e.describe())
        sys.exit(1)
