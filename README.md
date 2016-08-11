# pysmx

**pysmx** is a Python package for parsing, executing, and simulating the environment of SourceMod plug-ins.


## Quickstart

```python
from smx.compile import compile
plugin = compile('''
    public TwoPlusTwo() {
        return 2 + 2;
    }
''')
print plugin.runtime.call_function_by_name('TwoPlusTwo')
```
