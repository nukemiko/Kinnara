from setuptools import setup, find_packages

setup(
        name='kinnara',
        version='1.0',
        packages=find_packages(),
        url='https://github.com/kinnara',
        license='MIT',
        author='nukemiko',
        author_email='north666dakota@gmail.com',
        maintainer='nukemiko',
        maintainer_email='north666dakota@gmail.com',
        description='A tool can decrypt copyright protected music file from Chinese music platforms',
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
        install_requires=('pycryptodome', 'mutagen'),
        platforms='any',
        keywords=['ncm', 'qmc', 'unlock music', 'cloudmusic', 'cloud music', 'qqmusic', 'qq music'],
        zip_safe=False
)
