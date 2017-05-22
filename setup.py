from setuptools import find_packages, setup

setup(
    name="qzig",
    version="0.0.1",
    author="Seluxit ApS",
    author_email="info@seluxit.com",
    description="A ZigBee convertor for Seluxit Q platform",
    license="GPL-3.0",
    keywords="zigbee q seluxit converter",
    url="http://q.seluxit.com",
    packages=find_packages(exclude=['*.tests']),
    scripts=["qzig/main.py"],
    entry_points={
        'console_scripts': ['qzig=qzig.main:main'],
    },
    install_requires=[
        'bellows',
    ],
    tests_require=[
        'pytest',
    ],
)
