from setuptools import setup, find_packages


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='pyeuclid',
    version='1.0.0',
    description='PyEuclid: A Versatile Formal Plane Geometry System in Python',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
)