import os
import re
import ast
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext

package_name = "omicexperiment"


# version parsing from __init__ pulled from scikit-bio
# https://github.com/biocore/scikit-bio/blob/master/setup.py
# which is itself based off Flask's setup.py https://github.com/mitsuhiko/flask/blob/master/setup.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')


# Bootstrap setup.py with numpy
# from the solution by coldfix http://stackoverflow.com/a/21621689/579416
class build_ext_numpy(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        import builtins
        builtins.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


with open('omicexperiment/__init__.py', 'rb') as f:
    hit = _version_re.search(f.read().decode('utf-8')).group(1)
    version = str(ast.literal_eval(hit))


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

try:
    import pypandoc
    long_description = pypandoc.convert(README + '\n\n' +  CHANGES, 'rst', format='md')
except ImportError:
    long_description= README + '\n\n' + CHANGES

setup_requires = [
    'numpy >= 1.10.4'
    ]

install_requires = [
    'numpy >= 1.10.4',
    'scipy>=0.16.1',
    'pandas >= 0.17.1',
    'biom-format >= 2.1.5',
    'lxml>=3.5.0',
    'pygal >= 2.1.1',
    'scikit-bio==0.4.2']


setup(name=package_name,
      version=version,
      license='BSD',
      description="For analysis of omic experiments.",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
      cmdclass={'build_ext': build_ext_numpy},
      author='Ahmed Bassiouni',
      author_email='ahmedbassi@gmail.com',
      maintainer="Ahmed Bassiouni",
      maintainer_email="ahmedbassi@gmail.com",
      url='https://github.com/bassio/omicexperiment',
      download_url = 'https://github.com/bassio/omicexperiment/tarball/' + version,
      keywords='bioinformatics',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='omicexperiment.tests',
      install_requires=install_requires,
      setup_requires=setup_requires,
      entry_points="""\
      """,
      )

