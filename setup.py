# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gemini-model-rotater",
    version="1.0.1",
    author="Santosh Kanumuri",
    author_email="pavan.kanumuri@hotmail.com",
    description="A package to rotate Gemini API models based on rate limits.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/santoshkanumuri/gemini-model-rotater",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
