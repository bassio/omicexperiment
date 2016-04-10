import os
import re
import ast
from setuptools import setup, find_packages


# version parsing from __init__ pulled from scikit-bio
# https://github.com/biocore/scikit-bio/blob/master/setup.py
# which is itself based off Flask's setup.py https://github.com/mitsuhiko/flask/blob/master/setup.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

package_name = "omicexperiment"

with open('omicexperiment/__init__.py', 'rb') as f:
    hit = _version_re.search(f.read().decode('utf-8')).group(1)
    version = str(ast.literal_eval(hit))


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'numpy >= 1.10.4',
    'pandas >= 0.17.1',
    'biom-format >= 2.1.5',
    'pygal >= 2.1.1'
    ]

setup(name=package_name,
      version=version,
      license='BSD',
      description="For analysis of omic experiments.",
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
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
      install_requires=requires,
      entry_points="""\
      """,
      )

