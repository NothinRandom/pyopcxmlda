from setuptools import setup

__version__      = '0.1.1'
__license__      = 'MIT'
__author__       = 'Tri Quach'
__author_email__ = 'nothinrandom@gmail.com'
__url__          = 'https://github.com/NothinRandom/pyopcxmlda'

setup(
    name="pyopcxmlda",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    description="A Python3 OPC XML-DA library.",
    license="MIT",
    packages=["pyopcxmlda"],
    python_requires=">=3.7.0",
    install_requires=["requests"]
)
