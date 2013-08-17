Briticle
========

Briticle is a Python library to extract the main content of a webpage.

Requirements
------------

  - BeautifulSoup 4
  - html5lib / lxml
  - [kindelgen](http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) (required if you want save into mobi files)

Installation
------------

Copy the single briticle.py file to your project or install it into your pythonpath:

    # python setup.py install

Basic Usage
-----------

```python
>>> from briticle import Briticle
>>> bs = Briticle()
>>> bs.open('http://example.com/blog-post-url/')
>>> print bs.text # the main content
>>> print bs.html # the main content with html tags

# If we want save to mobi file
>>> save_dir = "/Users/mitnk/tmp"
>>> url = "http://mitnk.com/79/code_notes_i/"
>>> bf = BriticleFile(url, save_dir)
>>> bf.save_to_mobi()
```

How to Test
-----------

Just run the following command in the directory 
contains briticle.py:

    # python test.py

Author
------

mitnk @ twitter
whgking AT gmail DOT com
