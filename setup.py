#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import setuptools

version='0.1'
setuptools.setup(
    name='TracDevPlatformPlugin',
    version=version,
    
    description='Provide helpers to ease development on top of Trac',
    author='Felix Schwarz',
    author_email='felix.schwarz@oss.schwarz.eu',
    url='http://www.schwarz.eu/opensource/projects/trac_dev_platform',
    download_url='http://www.schwarz.eu/opensource/projects/trac_dev_platform/download/%s' % version,
    license='MIT',
    install_requires=['Trac >= 0.11'],
    extras_require={'BeautifulSoup': 'BeautifulSoup'},
    
    tests_require=['nose'],
    test_suite = 'nose.collector',
    
    zip_safe=False,
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Trac',
    ],
)

