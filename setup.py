from setuptools import setup, find_packages

setup(
    name="contract_automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)