#!/usr/bin/env python

import setuptools

setuptools.setup(name='geocloud-es',
      version='0.9',
      description='ElasticSearch ingestor for GPSD JSON',
      long_description="""ElasticSearch ingestor for GPSD JSON""",
      long_description_content_type="text/markdown",
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/geocloud-es',
      packages=setuptools.find_packages(),
      install_requires=[
          'elasticsearch',
          'elasticsearch_dsl',
          'socket-tentacles'
      ],
      include_package_data=True,
      entry_points='''
      [console_scripts]
      geocloud-es = geocloud_es:main
      '''
  )
