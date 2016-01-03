# via: https://github.com/pypa/sampleproject/blob/master/setup.py
from setuptools import setup

DESC = """
Briticle is a Python library to extract the main content of a webpage.

Requirements:

- BeautifulSoup 4
- html5lib / lxml
- kindelgen (required if you want save into mobi files)

"""

setup(
    name='briticle',
    version='0.9.1',

    description='Extract the main content of a webpage',
    long_description=DESC,

    url='https://github.com/mitnk/briticle',
    author='mitnk',
    author_email='w@mitnk.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='briticle blog content',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    py_modules=["briticle"],
)
