from setuptools import setup, find_packages
from pathlib import Path

extra_reqs = {
    "dev": [
        "pytest==8.2.2",
        "black==24.4.2",
        "ruff==0.5.0",
    ],
}

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="podcast_gpt",
    version="0.1",
    description="A Python package for processing podcasts using GPT",
    long_description=README,
    author="Matthew",
    author_email="mmym.ezout@gmail.com",
    url="https://github.com/alex/podcast_agent_gpt",
    packages=find_packages(),
    install_requires=[
        "elevenlabs",
        "tqdm",
        "mutagen",
        "langchain",
        "fastapi",
    ],
    extras_require=extra_reqs,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
