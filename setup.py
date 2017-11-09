from setuptools import find_packages, setup

setup(
    name="qzig",
    version="0.0.4",
    author="Seluxit ApS",
    author_email="info@seluxit.com",
    maintainer="Andreas Bomholtz",
    maintainer_email="andreas@seluxit.com",
    description="A ZigBee convertor for Seluxit IoT platform",
    license="GPL-3.0",
    keywords="zigbee iot seluxit converter",
    url="http://iot.seluxit.com",
    download_url="https://github.com/Seluxit/qzig",
    bugtrack_url="https://github.com/Seluxit/qzig/issues",
    packages=find_packages(exclude=['*.tests']),
    entry_points={
        'console_scripts': ['qzig=qzig.main:main'],
    },
    install_requires=[
        'bellows==0.4.0',
    ],
    requires=[
        'bellows',
    ],
    tests_require=[
        'pytest',
    ],
    platforms=[
        'Linux'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: AsyncIO',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
