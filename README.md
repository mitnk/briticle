Briticle
========

Briticle is a Python library to extract the main content of a webpage.

Requirements
------------

  - BeautifulSoup 4
  - html5lib / lxml

Installation
------------

Copy the single briticle.py file to your project or install it into your pythonpath:

    # python setup.py install

Basic Usage
-----------

    >>> from briticle import Briticle
    >>> bs = Briticle()
    >>> bs.open('http://example.com/blog-post-url/')
    >>> print bs.text # the main content
    >>> print bs.html # the main content with html tags

How to Test
-----------

Just run the following command in the directory 
contains briticle.py:

    # python test.py

Author
------

mitnk @ twitter
whgking AT gmail DOT com
