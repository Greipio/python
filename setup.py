from setuptools import setup, find_packages

setup(
    name="greip",
    version="1.0.0",
    description="Python wrapper for Greip API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Greip",
    author_email="info@greip.io",
    url="https://github.com/Greipio/python",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires='>=3.6',
)