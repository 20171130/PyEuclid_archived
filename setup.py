from setuptools import setup, find_packages


setup(
    name='pyeuclid',
    version='1.0.0',
    description='PyEuclid: A Versatile Formal Plane Geometry System in Python',
    packages=find_packages(),
    install_requires=[  
        "gurobipy",
        "matplotlib",
        "numpy",
        "stopit",
        "sympy",
        "tqdm",
        "z3-solver"
    ], 
    include_package_data=True,
)