PySMX
=====

PySMX is a Python module for reading and executing compiled SourcePawn plug-ins. Its aim is to enable unit testing of plug-ins, improving code quality and enabling test-driven development in SourceMod.

At the moment, only a small subset of opcodes and one native (format-string-only PrintToServer) are implemented, allowing for the execution of the test plug-in at test/test.smx.

Usage
-----

Here's how to load and execute a plug-in:

```python
import smx
with open('myplugin.smx', 'rb') as fp:
    plugin = smx.SourcePawnPlugin(fp)
    print 'Loaded %s...' % plugin
    plugin.run()
```