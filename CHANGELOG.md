# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [0.4.0] — 2023-03-02
### Added
 - Add basic SP runtime exception system, including stack traces
 - Add full support for array generation/initialization, including support for old-style indirect arrays (plugins without `kUsesDirectArrays` code feature)
 - Add support for calling plugin functions with arguments (including by-ref/copyback args, with their mutated values returned)
 - Allow the specification of a filename in `compile_plugin` (this filename is baked into debug info)
 - Add `BreakString` native
 - Add `heap.save` and `heap.restore` instructions for the `kUsesHeapScopes` code feature
 - Implement `bounds` instruction, reporting runtime errors if out-of-bounds
 - Add support for top-level function types in native params
 - Group stack spew by frame

### Fixed
 - Fix improper calling convention implementation (pushing return address to stack) causing parent-frame references (such as `this` in enum struct methods) to point at wrong address
 - Fix non-public array-returning methods not properly allocating space for the return value when called with `PluginFunction`
 - Fix issue with `lodb.i` instruction and sizes 1 or 2 reading from wrong memory
 - Fix broken `TrimString` native implementation
 - Fix `RoundToZero` doing exactly opposite of what it should do
 - Fix varargs natives params (the `...` type) improperly passing num params to native implementation
 - Fix RTTI info for enum struct fields being read from wrong section (`rtti.enumstruct_fields`, not `rtti.es_fields`)
 - Resolve broken `switch` implementation
 - Resolve `sdiv` signed division instructions improperly rounding to floor, instead of to zero
 - `sdiv` division by zero and overflow now reported as runtime error
 - Resolve `shr` unsigned shift right instruction improperly shifting over 1's, not 0's (this behaviour is due to Python's arbitrary-sized integers and how they work when not masked)
 - Fix `inc` and `dec` family of instructions double-dereferencing
 - Fix `movs` not actually copying data

### Changed
 - Allow multiple include dirs to be passed to `compile_plugin`
 - Allow native functions beginning with `__` to avoid Python class name mangling
 - Print spew instruction before executing, and update the line afterward (using the magic of carriage returns)
 - Reorganize innards into more modules
 - Remove useless level of indirection, `PluginDebug`

### Testing
 - Add and pass the full sourcepawn test suite
 - Add icdiff-based pretty diffs on test failures


## [0.3.0] — 2023-02-23
### BREAKING
 - Renamed `smx.compiler.compile` to `smx.compiler.compile_plugin` (now available as `smx.compile_plugin`)

### Added
 - Add float natives (which power normal floating point operators)
 - Add trigonometric natives
 - Add `File.Read` native
 - Add some basic string natives (`strlen`, `StrContains`, `strcmp`, `strncmp`, `strcopy`, `TrimString`)
 - Add option to spew stack during execution

### Fixed
 - Resolve incorrect calling convention leading to empty stack pops and other faults
 - Resolve broken `File.ReadLine` native
 - Handle natives' "bytes written" counts when null terminators are involved

### Changed
 - Overhauled opcode parsing and execution to allow `spew` to properly show annotated params and return values
 - Natives' return values are now automatically converted back to cell values (especially important for floats)


## [0.2.0] — 2023-02-22
### Added
 - Read all RTTI sections
 - Expand RTTI value interpretation and string formatting
 - Add `spew` param to emit all executed instructions and their params
 - Add basic `files.inc` natives (`BuildPath`, `OpenFile`, `File.ReadLine`, `File.EndOfFile`)

### Fixed
 - Resolve broken function RTTI parsing
 - Prevent error when encountering unknown RTTI control bytes
 - Resolve natives reading strings from wrong address


## [0.1.1] — 2023-02-21
### Fixed
 - Remove dead references to `six` library
 - Actually show compiler output on error


## [0.1.0] — 2023-02-21
### BREAKING
 - Drop support for end-of-life Python versions — minimum supported Python version is now 3.7
 - Drop support for ASM verification, as the compiler no longer outputs the bytecode assembly
 - Updated all compiler binaries to their latest versions

### Added
 - Add support for the beautiful runtime type information (RTTI) made available in .smx (NOTE: not all types/type declarations supported, yet)
 - Add 64-bit compilers for windows/linux

### Changed
 - Updated all include files
 - Switch to Poetry
 - Use GitHub Actions for testing
 - Switch to [construct](https://construct.readthedocs.io/en/latest/) for binary parsing (leaning on [construct-typing](https://github.com/timrid/construct-typing) for a usable interface)


## [0.0.3] - 2018-04-27
### Added
 - Use tox to test py27 and py36

### Fixed
 - Choose correct compiler on Py3.3+ Linux


## [0.0.2] - 2018-04-27
### Added
 - Python 3 support!
 - Added GetConVarString native

### Fixed
 - Functions may now call other functions
 - Include compiler in package


## [0.0.1] - 2018-04-27
Initial package release
