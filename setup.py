import os
import sys
from setuptools import setup
from simplethirty import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

extra = {}
requirements = ['argparse', 'libthirty==0.4']
tests_require = ["nose", "mock", "coverage"]

if sys.version_info < (2, 6):
    requirements.append('simplejson')

# In case we use python3
if sys.version_info >= (3,):
    extra['use_2to3'] = True


setup(
    name="simplethirty",
    version=__version__,
    description="A simplified client for the 30loops platform.",
    long_description=read('README.rst'),
    url='http://30loops.net/',
    license='BSD',
    author='30loops.net team',
    author_email='bas@30loops.net',
    include_package_data=True,
    packages=['simplethirty', 'simplethirty.actions'],
    install_requires=requirements,

    setup_requires='nose',
    tests_require=tests_require,
    test_suite="nose.collector",
    extras_require={'test': tests_require},

    #packages = find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    entry_points={
        'console_scripts': ['simplethirty = simplethirty.shell:main']
    },
    **extra
)
