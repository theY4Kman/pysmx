import click as click

from pysmx_stubgen.gen import generate_stubs


@click.command()
@click.argument('output-dir', type=click.Path(file_okay=False, dir_okay=True, writable=True))
def stubgen(output_dir: str):
    generate_stubs(output_dir=output_dir)
