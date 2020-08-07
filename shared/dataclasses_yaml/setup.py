from setuptools import setup, find_packages

setup(
    name="dataclasses_yaml",
    packages=find_packages(),
    install_requires=[
        'pyyaml>=5.3.1',
        'dataclasses_json'
        ]
    )
