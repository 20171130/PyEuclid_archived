from setuptools import setup, find_packages


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='euclid-omni',
    version='1.0.0',
    description='Euclid-Omni: A Unified Neuro-Symbolic Framework for Plane Geometry',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
)
