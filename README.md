# pysmx

**pysmx** is a Python package for parsing, executing, and simulating the environment of SourceMod plug-ins.


## Quickstart

```shell
pip install pysmx
```

```python
from smx.compiler import compile

plugin = compile('''
    public TwoPlusTwo() {
        return 2 + 2;
    }
    public String:Snakes() {
        new String:s[] = "hiss";
        return s;
    }
''')

print(plugin.runtime.call_function_by_name('TwoPlusTwo'))
# 4
print(plugin.runtime.call_function_by_name('Snakes'))
# 'hiss'
```
