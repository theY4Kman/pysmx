PySMX
=====

PySMX is a Python module for reading information from compiled SourcePawn plug-ins. At the moment, the most useful thing PySMX does is read the strings from the myinfo variable. However, technically, PySMX is a full SMX reader, extracting and reading all sections.

Usage
-----

As the myinfo struct is most important at this stage, here's the canonical example for how to extract it from a plug-in:

```python
import smx
with open('myplugin.smx', 'rb') as fp:
    plugin = smx.SourcePawnPlugin(fp)
    print plugin.myinfo
```