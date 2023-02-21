# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]


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
