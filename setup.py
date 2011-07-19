from setuptools import setup, find_packages

version = '0.1'

setup(name='wsgibrowserid',
      version=version,
      description="Stand-alone app to implement relying-party browserid.org support",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi browserid authentication',
      author='Ian Bicking',
      author_email='ianb@mozilla.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
        'pycurl',
      ],
      entry_points="""
      [paste.app_factory]
      main = wsgibrowserid.wsgiapp:make_app
      """,
      )
