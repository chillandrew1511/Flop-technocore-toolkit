from pathlib import Path
from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent

# Read the long description from README
long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="flop-technocore-toolkit",
    version="0.1.0",
    author="Andrew Chill",
    author_email="andrew@example.com",
    description="Helper toolkit for Technocore platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chillandrew1511/Flop-technocore-toolkit",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "PyYAML>=6.0",
        "click>=8.1.0",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "flop=flop_technocore.cli:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
