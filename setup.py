"""
Setup script for the Aptitude Generator application.

This script allows the package to be installed with pip.
"""
import os
from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the README file for the long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aptitude-generator',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    
    # Metadata
    author='Your Name',
    author_email='your.email@example.com',
    description='A web application for generating and practicing aptitude test questions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/aptitude-generator',
    license='MIT',
    
    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
        'Topic :: Education :: Testing',
    ],
    
    # Entry points
    entry_points={
        'console_scripts': [
            'aptitude-generator=wsgi:main',
        ],
    },
    
    # Data files
    package_data={
        'app': ['templates/*', 'static/*'],
    },
)
