#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip()]

setup(
    name="pdftomd",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="用于PDF文档转Markdown并进行数据清洗，为大语言模型微调准备高质量训练数据",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/21thsth/pdf-to-md-for-finetune",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pdftomd=pdftomd.cli:main",
        ],
    },
) 