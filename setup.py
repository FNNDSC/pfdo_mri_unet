import sys

# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'pfdo_mri_unet',
      version          =   '0.1',
      description      =   'Runs mri_unet on each nested dir of an inputdir',
      long_description =   readme(),
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/pfdo_mri_unet',
      packages         =   ['pfdo_mri_unet'],
      install_requires =   ['pfmisc', 'pftree', 'pfdo', 'mri_unet', 'nibabel', 'pandas', 'numpy', 'imageio', 'matplotlib'],
      #test_suite       =   'nose.collector',
      #tests_require    =   ['nose'],
      scripts          =   ['bin/pfdo_mri_unet'],
      license          =   'MIT',
      zip_safe         =   False
)
