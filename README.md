# pysmx

**pysmx** is a Python package for parsing, executing, and simulating the environment of SourceMod plug-ins.


## Quickstart

```shell
pip install pysmx
```

```python
from smx import compile_plugin

plugin = compile_plugin('''
    public TwoPlusTwo() {
        return 2 + 2;
    }
    public float FiveDividedByTen() {
        return 5.0 / 10.0;
    }
    public String:Snakes() {
        new String:s[] = "hiss";
        return s;
    }
''')

print(plugin.runtime.call_function_by_name('TwoPlusTwo'))
# 4
print(plugin.runtime.call_function_by_name('FiveDividedByTen'))
# 0.5
print(plugin.runtime.call_function_by_name('Snakes'))
# 'hiss'
```
