import re
from collections import defaultdict
from pathlib import Path

import lark

from pysmx_stubgen.symbols import (
    _import,
    IncludeFile,
    lazy_string,
    Methodmap,
    mod_handles,
    Native,
    ParamInfo,
    SPEnum, Typedef,
)

__all__ = []

GRAMMAR_DIR = Path(__file__).parent / 'grammar'


def load_grammar(grammar_name: str | Path, **options) -> lark.Lark:
    if isinstance(grammar_name, str):
        grammar_path = GRAMMAR_DIR / grammar_name
    else:
        grammar_path = grammar_name

    grammar = grammar_path.read_text()
    return lark.Lark(grammar, import_paths=[str(GRAMMAR_DIR)], **options)


param_parser = load_grammar('sourcepawn.lark', start='param_list')
enum_parser = load_grammar('sourcepawn.lark', start='enum_items')
methodmap_method_parser = load_grammar('sourcepawn.lark', start='methodmap_method')
function_decl_parser = load_grammar('sourcepawn.lark', start='function_decl')


class BaseTransformer(lark.Transformer):
    def symbol(self, token):
        return str(token[0])

    type = builtin_type = identifier = symbol

    def string_literal(self, children):
        string_token = children[0]
        return string_token[1:-1]

    def integer_literal(self, children):
        return int(children[0])

    def float_literal(self, children):
        return float(children[0])

    def array_literal(self, children):
        return children

    def shift_left(self, children):
        return children[0] << children[1]

    def shift_right(self, children):
        return children[0] >> children[1]

    def inclusive_or_expr(self, children):
        if not all(isinstance(c, int) for c in children):
            return f'{children[0]} | {children[1]}'
        return children[0] | children[1]

    def ellipsis(self, children):
        return ...

    def and_(self, children):
        return '&'


class ParamTransformer(BaseTransformer):
    def start(self, children):
        if children:
            return children[0]
        else:
            return []

    def param_list(self, children):
        if isinstance(children, ParamInfo):
            return [children]
        return children

    def param_decl_new(self, children):
        i = 0
        is_const = False
        is_ref = False
        is_varargs = False

        if children[i].data == 'const':
            is_const = True
            i += 1

        type_, dims = children[i].children
        i += 1
        type_ = str(type_)

        if children[i] == '&':
            is_ref = True
            i += 1

        if children[i] is ...:
            name = '...'
            is_varargs = True
        else:
            name = str(children[i])
            i += 1
            if children[i] and isinstance(children[i], list):
                dims = children[i]
                i += 1

        param = ParamInfo(
            name=name,
            base_type=type_,
            dims=dims,
            is_const=is_const,
            is_ref=is_ref,
            is_varargs=is_varargs,
        )
        return param

    def type_dims(self, children):
        return [None] * len(children)

    def old_dims(self, children):
        if children:
            return [child or None for child in children]


class EnumTransformer(BaseTransformer):
    def enum_items(self, children):
        if not children:
            return []

        if isinstance(children, tuple):
            return [children]

        items: list[tuple[str, int]] = []
        last_val = -1
        for name, value in children:
            if value is None:
                value = last_val + 1
            last_val = value
            items.append((name, value))

        return items

    def enum_item(self, children):
        if len(children) == 1:
            return children[0], None
        else:
            return tuple(children)


class MethodmapMethodTransformer(ParamTransformer):
    pass


param_transformer = ParamTransformer()
enum_transformer = EnumTransformer()
methodmap_method_transformer = MethodmapMethodTransformer()


# TODO(zk): just use a full lark grammar
RGX_DEFINE = re.compile(
    r'''
    ^\#define[ ]+
    (?P<name>\w+)[ ]+
    (?P<value>.+?)[ ]*
    (?:/\*|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_NATIVE = re.compile(
    r'''
    ^native\s+
    (?P<return_type>\S+)\s+
    (?P<name>\w+)\s*
    \((?P<params>[^)]*)\)\s*
    (?:;|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_ENUM = re.compile(
    r'''
    ^(\s*)enum\s+
    (?P<name>\w+)
    (?:
        \s+ \{
        (?P<body>[\s\S]*?)
        \1}
        |
        \s*:\s*\{\s*}
    )
    (?:;|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_METHODMAP = re.compile(
    r'''
    methodmap\s+
    (?P<name>\w+)\s*
    <\s*
    (?P<base>\w+)\s*
    (\s*)\{
    (?P<body>[\s\S]+?)
    ^\3};?
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_METHODMAP_METHOD_DECL = re.compile(
    r'''
    public\s+
    (?:(?P<static>static)\s+)?
    native\s+
    (?P<return_type>\S+)\s+
    (?P<name>\w+)\s*
    \((?P<params>[^)]*)\)\s*
    (?:;|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_TYPESET = re.compile(
    r'''
    typeset\s+
    (?P<name>\w+)\s*
    \{
    (?P<body>[\s\S]+?)
    }(?:;|$)
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_TYPEDEF = re.compile(
    r'''
    typedef\s+
    (?P<name>\w+)\s*
    =\s*
    (?P<body>[\s\S]+?)
    ;
    ''',
    re.VERBOSE | re.MULTILINE,
)
RGX_FUNCTION_DECL = re.compile(
    r'''
    function\s+
    (?P<return_type>\S+)\s+
    \((?P<params>[^)]*)\)\s*
    ''',
    re.VERBOSE | re.MULTILINE,
)


def parse_include_files(include_dir: str | Path) -> list[IncludeFile]:
    include_dir = Path(include_dir)

    files = []
    for inc_path in Path(include_dir).glob('**/*.inc'):
        rel_path = inc_path.relative_to(include_dir)
        contents = inc_path.read_text()

        defines = dict(RGX_DEFINE.findall(contents))
        for name, value in defines.items():
            # TODO(zk): more performant
            contents = contents.replace(name, value)

        enums: list[SPEnum] = []
        natives: list[Native] = []
        methodmaps: list[Methodmap] = []
        typedef_decls: dict[str, list[Native]] = defaultdict(list)

        for match in RGX_TYPESET.finditer(contents):
            typeset_name = match.group('name')
            typeset_body = match.group('body')
            typeset_items = parse_typeset(typeset_body)
            typedef_decls[typeset_name].extend(typeset_items)

        for match in RGX_TYPEDEF.finditer(contents):
            typedef_name = match.group('name')
            typedef_body = match.group('body')
            typedef = parse_typedef(typedef_body)
            typedef_decls[typedef_name].append(typedef)

        typedefs = [
            Typedef(name=name, decls=decls)
            for name, decls in typedef_decls.items()
        ]

        for match in RGX_ENUM.finditer(contents):
            enum_name = match.group('name')
            enum_items = parse_enum_items(match.group('body'))
            enums.append(SPEnum(name=enum_name, items=enum_items))

        for match in RGX_NATIVE.finditer(contents):
            params = parse_native_params(match.group('params'))
            native = Native(
                name=match.group('name'),
                return_type=match.group('return_type'),
                params=params,
            )
            natives.append(native)

        for match in RGX_METHODMAP.finditer(contents):
            methodmap = parse_methodmap(
                match.group('name'),
                match.group('base'),
                match.group('body'),
            )
            methodmaps.append(methodmap)

        file = IncludeFile(
            path=rel_path,
            name=rel_path.stem,
            natives=natives,
            enums=enums,
            methodmaps=methodmaps,
            typedefs=typedefs,
        )
        files.append(file)

    return files


def parse_native_params(params_source: str) -> list[ParamInfo]:
    if not params_source:
        return []

    tree = param_parser.parse(params_source)
    return param_transformer.transform(tree)


def parse_enum_items(enum_body: str) -> list[tuple[str, int]]:
    if not enum_body:
        return []

    enum_items = enum_parser.parse(enum_body)
    return enum_transformer.transform(enum_items)


def parse_methodmap(name: str, base: str, body: str) -> Methodmap:
    methods = []
    for match in RGX_METHODMAP_METHOD_DECL.finditer(body):
        is_static = match.group('static') is not None

        params = parse_native_params(match.group('params'))
        if not is_static:
            # TODO(zk): move this to where ImportContext can see it
            handle_param = ParamInfo(
                name='this',
                base_type=lazy_string(lambda: f'{mod_handles.SourceModHandle}[{name}]'),
            )
            params.insert(0, handle_param)

        method = Native(
            name=match.group('name'),
            return_type=match.group('return_type'),
            params=params,
        )
        methods.append(method)

    return Methodmap(name=name, base=base, methods=methods)


def parse_typeset(typeset_body: str) -> list[Native]:
    typedefs = []

    for match in RGX_FUNCTION_DECL.finditer(typeset_body):
        params = parse_native_params(match.group('params'))
        native = Native(
            name=None,
            return_type=match.group('return_type'),
            params=params,
        )
        typedefs.append(native)

    return typedefs


def parse_typedef(typedef_body: str) -> Native:
    match = RGX_FUNCTION_DECL.match(typedef_body)
    params = parse_native_params(match.group('params'))
    return Native(
        name=None,
        return_type=match.group('return_type'),
        params=params,
    )
