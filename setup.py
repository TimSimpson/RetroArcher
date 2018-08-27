from setuptools import setup


setup(
    name='RetroArcher',

    packages=['retroarcher'],
    install_requires=['typing'],

    entry_points={
        'console_scripts': [
            'retroarcher=retroarcher.main:main',
        ],
    },
)
