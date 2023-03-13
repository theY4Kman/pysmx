from pathlib import Path

from pysmx_stubgen.parser import parse_include_files
from pysmx_stubgen.symbols import ImportedName, IncludeFile, Methodmap, mod_handles, SPEnum
from smx.compiler import INCLUDE_DIR


def generate_stubs(*, include_dir: str | Path = None, output_dir: str | Path) -> None:
    """Generate stubs for all natives in the given include dir"""
    if include_dir is None:
        include_dir = Path(INCLUDE_DIR)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = parse_include_files(include_dir)
    exports: dict[str, tuple[IncludeFile, SPEnum | Methodmap]] = {
        name: (file, obj)
        for file in files
        for name, obj in file.exports.items()
    }

    def resolve_import(file: IncludeFile, name: str) -> tuple[str | ImportedName, Methodmap | SPEnum | None]:
        if name not in exports:
            return name, None

        owning_file, obj = exports[name]
        if file == owning_file:
            return name, obj

        imported_name = getattr(owning_file.py_mod, name)
        if not name.endswith('MethodMap') and isinstance(obj, Methodmap):
            return f'{mod_handles.SourceModHandle}[{imported_name}]', obj

        return imported_name, obj

    for file in files:
        if not file:
            continue

        file_path = output_dir / file.path.with_suffix('.py')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.py_format(resolve_import=resolve_import))
