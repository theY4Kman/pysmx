from __future__ import annotations

import functools
import inspect
import pprint

from _pytest.config import Config
from icdiff import ConsoleDiff

from test.util.terminalsize import get_terminal_size

# When reporting errors, pytest prefixes each line with "E   " (4 chars).
# When printing assertion failures, each line is indented with an additional 2
# spaces.
#
# By accounting for these extra spaces, we ensure no wrapping occurs.
#
PYTEST_PREFIX_LEN = 6

# Comparison operations we support pretty diffs for
SUPPORTED_OPS = {'=='}


# source: https://stackoverflow.com/a/25959545/148585
def get_class_that_defined_method(meth) -> type | None:
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)

    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing

    if inspect.isfunction(meth):
        cls = getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
            None,
        )
        if isinstance(cls, type):
            return cls

    return getattr(meth, '__objclass__', None)  # handle special descriptor objects


class PrettyPrinter(pprint.PrettyPrinter):
    _dispatch = dict(pprint.PrettyPrinter._dispatch)

    def _format_dict_items(self, items, stream, indent, allowance, context, level):
        write = stream.write
        indent += self._indent_per_level
        nlindent = '\n' + ' ' * indent
        last_index = len(items) - 1
        for i, (key, ent) in enumerate(items):
            is_last = i == last_index
            rep = self._repr(key, context, level)
            write(rep)
            write(': ')
            self._format(ent, stream, indent, 1, context, level)
            write(',')
            if not is_last:
                write(nlindent)

    def _pprint_dict(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('{')
        length = len(object)
        if length:
            items = object.items()
            write('\n' + ' ' * (indent + self._indent_per_level))
            self._format_dict_items(items, stream, indent, allowance + 1,
                                    context, level)
            write('\n' + ' ' * indent)
        write('}')

    _dispatch[dict.__repr__] = _pprint_dict

    @classmethod
    def get_supported_types(cls) -> tuple[type]:
        return tuple(
            t
            for t in (get_class_that_defined_method(repr_func) for repr_func in cls._dispatch)
            if t is not None
        )


# Types which we support pretty diffs on
SUPPORTED_TYPES = PrettyPrinter.get_supported_types()


def _format_obj(o, indent=2, width=60):
    if isinstance(o, str):
        return o

    return PrettyPrinter(indent=indent, width=width, sort_dicts=False).pformat(o)


def pytest_assertrepr_compare(config: Config, op: str, left, right):
    # Resets the red color from the "E" at the start of each pytest
    # exception/assertion traceback line
    reset_colors = lambda s: f'\x1b[0m{s}'

    if op not in SUPPORTED_OPS:
        return

    if not (isinstance(left, SUPPORTED_TYPES) and isinstance(right, SUPPORTED_TYPES)):
        return

    term_width, term_height = get_terminal_size()
    available_width = term_width - PYTEST_PREFIX_LEN
    col_width = available_width / 2 - 1  # extra space for a cleaner output

    left_desc = f'{type(left).__name__}(<left>)'
    right_desc = f'{type(right).__name__}(<right>)'
    rewritten_assert = f'{left_desc} {op} {right_desc}'

    summary = 'Full diff:'

    left_repr = _format_obj(left, width=col_width)
    right_repr = _format_obj(right, width=col_width)

    differ = ConsoleDiff(tabsize=4, cols=available_width)
    diff = differ.make_table(
        fromdesc=left_desc,
        fromlines=left_repr.splitlines(),
        todesc=right_desc,
        tolines=right_repr.splitlines(),
    )

    lines = [
        rewritten_assert,
        '',
        summary,
        '',
    ]
    lines.extend(
        reset_colors(diff_line)
        for diff_line in diff
    )
    return lines
