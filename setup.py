from setuptools import setup

setup(
    name="AVP Aviary API scripts",
    version="0.1.dev0",
    description="A set of command-line tool that interact with the AVP Aviary API to build reports and upload content.",
    #url="https://github.com/",
    license="Unlicense",
    install_requires=['requests>=2.31'],
    python_requires='>=3.7',
    py_modules=[]
)