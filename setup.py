from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bower.py',
    version='1.0',
    description='How I learned to stop worrying and love the bower',
    long_description=long_description,
    url='https://github.com/r1chardj0n3s/laughing-robot',
    author='Richard Jones',
    author_email='r1chardj0n3s@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='bower javascript',
    install_requires=['requests', 'semantic_version', 'github3.py'],
    packages=['bowerlib'],
    entry_points={
        'console_scripts': [
            'bower.py = bowerlib.main:main',
        ],
    },
)
