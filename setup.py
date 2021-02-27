import setuptools

with open("ReadMe.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="GamessUSReader",
    url = "https://github.com/gutow/GamessUSReader",
    version="0.9.0",
    description="Utilities for reading and plotting GAMESSUS output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    install_requires=[
        'jupyter>=1.0.0',
        'k3d>=2.9.1',
        'matplotlib>=3',
        'pandas>=1.2',
        'numpy>=1.19',
        'jupyter>=1.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ]
)