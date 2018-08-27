import setuptools


setuptools.setup(
    name='RetroArcherScripts',
    entry_points={
        'console_scripts': [
            "retroarcher-tests = runner:main",
        ],
    }
)
