from setuptools import setup, find_packages

setup(
    name='podcast_gpt',
    version='0.1',
    description='A Python package for processing podcasts using GPT',
    author='Matthew',
    author_email='mmym.ezout@gmail.com',
    url='https://github.com/alex/podcast_agent_gpt',
    packages=find_packages(),
    install_requires=[
        'elevenlabs',
        'tqdm',
        'mutagen',
        'langchain',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)
