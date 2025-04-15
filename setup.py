"""Setup script for PIPO agent."""

from setuptools import setup, find_packages

setup(
    name="pipo-agent",
    version="0.1.0",
    description="Program In Program Out - A code-focused AI agent framework",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "langfun[all]>=0.1.1",
        "pyglove>=0.3.1",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0"
        ]
    }
) 