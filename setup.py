import os

from setuptools import setup


repo_dir = os.path.dirname(__file__)
pkg_dir = os.path.join(repo_dir, 'smx')
version_path = os.path.join(pkg_dir, 'version.py')
requirements_path = os.path.join(repo_dir, 'requirements.txt')
readme_path = os.path.join(repo_dir, 'README.md')


def get_version():
    with open(version_path) as fp:
        context = {}
        exec(fp.read(), context)
        return context['VERSION']


def get_requirements():
    with open(requirements_path) as fp:
        return list(fp)


def get_readme():
    with open(readme_path) as fp:
        return fp.read()


setup(
    name='pysmx',
    version=get_version(),
    packages=['smx'],
    url='https://github.com/theY4Kman/pysmx',
    license='MIT',
    author='they4kman',
    author_email='they4kman@gmail.com',
    description='Interact with SourceMod plug-ins',
    install_requires=get_requirements(),
    include_package_data=True,
    long_description=get_readme(),
    long_description_content_type='text/markdown',
)
