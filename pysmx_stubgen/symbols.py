from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path
from typing import Callable, Protocol

import inflection
from isort.wrap_modes import WrapModes

from smx.compat import iskeyword

try:
    import isort
    HAS_ISORT = True
except ImportError:
    HAS_ISORT = False

_import_ctx: ContextVar[ImportContext] = ContextVar('import_ctx')


class ImportContext:
    def __init__(self):
        self._names: set[ImportedName] = set()
        self._reset_token: Token | None = None

    def __enter__(self):
        self._reset_token = _import_ctx.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _import_ctx.reset(self._reset_token)
        self._reset_token = None

    def add(self, name: ImportedName):
        self._names.add(name)

    def get_imports(self) -> list[str]:
        children = sorted((imp for imp in self._names if not imp.is_parent), key=lambda imp: imp.parent)
        by_module = {
            module: sorted(imp.name for imp in imp_names)
            for module, imp_names in groupby(children, key=lambda imp: imp.parent)
        }
        import_lines = [
            f'from {module} import {", ".join(names)}'
            for module, names in by_module.items()
        ]
        return sorted(import_lines)


def _import(parent: str) -> ImportedName:
    return ImportedName(parent)


class ImportedName(str):
    name: str | None
    parent: str | None
    is_parent: bool

    def __new__(cls, name: str | None, parent: str | None = None):
        self = super().__new__(cls, name or '')
        self.name = name
        self.parent = parent
        self.is_parent = self.name is None or self.parent is None
        self._register_usage()
        return self

    def __str__(self):
        self._register_usage()
        return super().__str__()

    def __getattr__(self, item: str) -> ImportedName:
        self.is_parent = True
        return ImportedName(item, self.fqn)

    @property
    def fqn(self) -> str:
        if not self.name:
            return ''
        if not self.parent:
            return self.name
        return f'{self.parent}.{self.name}'

    def _register_usage(self):
        try:
            _import_ctx.get().add(self)
        except LookupError:
            pass


mod_enum = _import('enum')
mod_exc = _import('smx.exceptions')
mod_runtime = _import('smx.runtime')
mod_handles = _import('smx.sourcemod.handles')
mod_natives_base = _import("smx.sourcemod.natives.base")


def lazy_string(fn: Callable[[], str]) -> str:
    class LazyString(str):
        def __str__(self):
            return fn()
    return LazyString()


class PyFormatMixin:
    def py_format(
        self,
        *,
        indent: int | str | None = None,
        resolve_import: ImportResolver | None = None,
    ) -> str:
        raise NotImplementedError


class PyStubBase(PyFormatMixin):
    def py_exports(self) -> set[str]:
        return set()


class ImportResolver(Protocol):
    def __call__(self, file: IncludeFile, name: str) -> tuple[str | ImportedName, Methodmap | SPEnum | None]:
        ...


def calc_indent(indent: int | str | None = None) -> str:
    if indent is None:
        return ''
    if isinstance(indent, int):
        return ' ' * indent
    return indent


RESERVED_BUILTIN_NAMES = frozenset({
    'type',
    'map',
    'chr',
    'iter',
    'format',
    'filter',
    'min',
    'max',
    'set',
    'str',
    'len',
    'bytes',
    'dir',
})


@dataclass
class ParamInfo(PyStubBase):
    name: str
    base_type: str
    dims: list[int | None] | None = None

    is_const: bool = False
    is_ref: bool = False
    is_varargs: bool = False

    def __str__(self):
        components = []
        if self.is_const:
            components.append('const ')
        if self.base_type:
            components.append(self.base_type)
            if self.dims:
                for dim in self.dims:
                    if dim is None:
                        components.append('[]')
                    else:
                        components.append(f'[{dim}]')
            components.append(' ')

        if self.is_varargs:
            components.append('...')
        else:
            name_prefix = '&' if self.is_ref else ''
            components.append(name_prefix + self.name)

        return ''.join(components)

    def py_type(self, **kwargs) -> str:
        if self.is_varargs:
            return 'Any'

        dims = self.dims or []
        type_ = py_format_type(self.base_type, dims, **kwargs)
        if type_ == 'str' and dims:
            dims = ()

        for _ in reversed(dims or []):
            type_ = f'{mod_natives_base.Array}[{type_}]'

        if self.is_ref:
            type_ = f'{mod_natives_base.Pointer}[{type_}]'

        return type_

    def py_format(self, **kwargs) -> str:
        if self.is_varargs:
            return '*args'

        name = inflection.underscore(self.name)
        if name in RESERVED_BUILTIN_NAMES or iskeyword(name):
            name = f'{name}_'
        return f'{name}: {self.py_type(**kwargs)}'


def py_format_type(
    type_: str,
    dims: list[int | None] | None = None,
    *,
    containing_file: IncludeFile | None = None,
    resolve_import: ImportResolver | None = None,
) -> str:
    if type_ in ('Any', '_', 'any'):
        return 'int'
    elif type_ == 'char':
        return 'str'
    if type_ in ('Any', '_', 'any'):
        return 'int'
    elif type_ == 'char':
        if dims:
            return 'str'
        else:
            return 'int'
    elif type_ == 'Handle':
        return mod_handles.SourceModHandle
    elif type_ == 'Function':
        return mod_runtime.PluginFunction
    elif type_ == 'void':
        return 'None'
    elif type_ in ('bool', 'int', 'float'):
        return type_
    elif resolve_import:
        name, obj = resolve_import(containing_file, type_)
        if isinstance(obj, Methodmap):
            return f'{mod_handles.SourceModHandle}[{name}]'
        return name
    else:
        return type_


@dataclass
class Native(PyStubBase):
    name: str | None
    return_type: str
    params: list[ParamInfo]

    def py_format(
        self,
        *,
        indent: int | str | None = None,
        **kwargs,
    ) -> str:
        if isinstance(indent, int):
            indent = ' ' * indent
        if indent is None:
            indent = ''

        params = ['self']
        i = 0
        while i < len(self.params):
            param = self.params[i]
            if i == len(self.params) - 1:
                params.append(param.py_format(**kwargs))
                break

            next_param = self.params[i + 1]

            if (
                param.py_type(**kwargs) == 'str'
                and next_param.py_type() == 'int'
                and next_param.name == 'maxlength'
            ):
                params.append(f'{param.name}: {mod_natives_base.WritableString}')
                i += 2
            else:
                params.append(param.py_format(**kwargs))
                i += 1

        return_type = py_format_type(self.return_type, **kwargs)
        return (
            f'{indent}@{mod_natives_base.native}\n'
            f'{indent}def {self.name}({", ".join(params)}) -> {return_type}:\n'
            f'{indent}    raise {mod_exc.SourcePawnUnboundNativeError}'
        )


@dataclass
class Methodmap(PyStubBase):
    name: str
    base: str
    methods: list[Native]

    def py_exports(self) -> set[str]:
        name = self.py_name
        return {name, f'{name}MethodMap'}

    @property
    def py_name(self) -> str:
        return inflection.camelize(self.name)

    def py_format(
        self,
        *,
        indent: int | str | None = None,
        containing_file: IncludeFile | None = None,
        resolve_import: ImportResolver | None = None,
        **kwargs,
    ) -> str:
        resolve_kwargs = {
            'containing_file': containing_file,
            'resolve_import': resolve_import,
            **kwargs,
        }

        indent = calc_indent(indent)
        method_indent = indent + '    '

        base_cls = (
            mod_natives_base.MethodMap
            if self.base == 'Handle'
            else resolve_import(containing_file, f'{self.base}MethodMap')[0]
        )

        if self.methods:
            cls_body = '\n\n'.join(
                method.py_format(indent=method_indent, **resolve_kwargs)
                for method in self.methods
            )
        else:
            cls_body = f'{method_indent}pass'

        return (
            f'{indent}class {self.py_name}MethodMap({base_cls}):\n'
            f'{cls_body}'
        )

    def py_format_decl(self, *, indent: int | str | None = None) -> str:
        indent = calc_indent(indent)
        return f'{indent}{self.py_name} = {self.py_name}MethodMap()'

    def py_format_handle_class(
        self,
        *,
        indent: int | str | None = None,
        containing_file: IncludeFile | None = None,
        resolve_import: ImportResolver | None = None,
    ) -> str:
        indent = calc_indent(indent)
        base_cls = (
            None
            if self.base == 'Handle'
            else resolve_import(containing_file, self.base)[0]
        )
        base_decl = f'({base_cls})' if base_cls else ''
        return (
            f'{indent}class {self.py_name}{base_decl}:\n'
            f'{indent}    pass'
        )


@dataclass
class SPEnum(PyStubBase):
    name: str
    items: list[tuple[str, int]]

    def py_exports(self) -> set[str]:
        return {self.name}

    def py_format(self, *, indent: int | str | None = None, **kwargs) -> str:
        indent = calc_indent(indent)
        lines = [f'{indent}class {self.name}({mod_enum.IntEnum}):']

        items = [f'{indent}    {name} = {value}' for name, value in self.items]
        if not items:
            items = [f'{indent}    pass']
        lines.extend(items)

        return '\n'.join(lines)


@dataclass
class Typedef(PyStubBase):
    name: str
    decls: list[Native]

    def py_exports(self) -> set[str]:
        return {self.name}

    def py_format(self, *, indent: int | str | None = None, **kwargs) -> str:
        indent = calc_indent(indent)
        return f'{indent}{self.name} = {_import("typing").Callable}'


@dataclass
class IncludeFile:
    path: Path
    name: str
    natives: list[Native]
    enums: list[SPEnum]
    methodmaps: list[Methodmap]
    typedefs: list[Typedef]

    exports: dict[str, SPEnum | Methodmap | Typedef] = field(init=False)

    def __post_init__(self):
        self.exports = {
            exported_name: obj
            for obj_sets in (self.typedefs, self.enums, self.methodmaps)
            for obj in obj_sets
            for exported_name in obj.py_exports()
        }

    def __bool__(self):
        return bool(self.natives or self.enums or self.methodmaps)

    @property
    def py_mod(self) -> ImportedName:
        return _import(f'smx.natives.{self.name}')

    def py_format(
        self,
        *,
        indent: int | str | None = None,
        resolve_import: ImportResolver | None = None,
    ) -> str:
        sections: list[str] = []
        cls_lines: list[str] = []

        with ImportContext() as import_ctx:
            resolve_kwargs = {
                'containing_file': self,
                'resolve_import': resolve_import,
            }

            if self.typedefs:
                typedefs = '\n'.join(
                    typedef.py_format(**resolve_kwargs)
                    for typedef in self.typedefs
                )
                sections.append(typedefs)

            if self.enums:
                for enum in self.enums:
                    sections.append(enum.py_format())

            if self.methodmaps:
                handle_class_decls = []
                methodmap_classes = []
                methodmap_class_vars = []

                for methodmap in self.methodmaps:
                    handle_class_decls.append(methodmap.py_format_handle_class(**resolve_kwargs))
                    methodmap_classes.append(methodmap.py_format(**resolve_kwargs))
                    methodmap_class_vars.append(methodmap.py_format_decl(indent=4))

                sections.extend(handle_class_decls)
                sections.extend(methodmap_classes)
                cls_lines.append('\n'.join(methodmap_class_vars))

            if self.natives:
                for native in self.natives:
                    cls_lines.append(native.py_format(indent=4, **resolve_kwargs))

            if cls_lines:
                cls_name = inflection.camelize(self.name)
                cls_body = '\n\n'.join(cls_lines)
                sections.append(
                    f'class {cls_name}Natives({mod_natives_base.SourceModNativesMixin}):\n'
                    f'{cls_body}'
                )

            imports = [
                'from __future__ import annotations',
                *import_ctx.get_imports(),
            ]
            import_section = '\n'.join(imports)
            if HAS_ISORT:
                import_section = isort.code(
                    import_section,
                    multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
                )

            sections.insert(0, import_section.strip())

        return '\n\n\n'.join(sections) + '\n'

