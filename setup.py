import os

from setuptools import setup


repo_dir = os.path.dirname(__file__)
readme_path = os.path.join(repo_dir, 'README.md')


def get_readme():
    with open(readme_path) as fp:
        return fp.read()


setup(
    name='pysmx',
    version='0.0.1',
    packages=['smx'],
    url='https://github.com/theY4Kman/pysmx',
    license='MIT',
    author='they4kman',
    author_email='they4kman@gmail.com',
    description='Interact with SourceMod plug-ins',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
)
