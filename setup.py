from setuptools import setup, find_packages

setup(
    name='Test',
    version='0.1',
    description='A simple test package',
    author='Waqas Ahmed',
    author_email='wiqaaas@gmail.com',
    packages=find_packages(),
    install_requires=[
        open('requirements.txt').read().splitlines()
    ],
)
