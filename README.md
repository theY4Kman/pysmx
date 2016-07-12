PySMX
=====

PySMX is a Python module for reading and executing compiled SourcePawn plug-ins. Its aim is to enable unit testing of plug-ins, improving code quality and enabling test-driven development in SourceMod.

At the moment, 131 of 148 opcodes have been implemented (17 left!), allowing for some simple plug-ins to be executed, including the test plug-in under the `test/` directory. The formatting functionality of `PrintToServer` is also implemented, sans game-dependent specifiers such as translations and player names.

PySMX boasts a managed Python stack (with a buffer backing) and executed instructions list, as well as a verification feature which will match a SourcePawn assembly file (compiled using `spcomp -a`) instruction for instruction.

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