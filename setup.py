# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
        name='kinnara',
        version='1.1',
        packages=find_packages(),
        url='https://github.com/nukemiko/Kinnara',
        license='MIT',
        author='nukemiko',
        author_email='north666dakota@gmail.com',
        maintainer='nukemiko',
        maintainer_email='north666dakota@gmail.com',
        description='A tool can decrypt copyright protected music file from Chinese music platforms',
        python_requires='>=3.6',
        install_requires=('pycryptodomex', 'mutagen'),
        platforms='any',
        keywords=['ncm', 'qmc', 'unlock music', 'cloudmusic', 'cloud music', 'qqmusic', 'qq music'],
        zip_safe=False
)
