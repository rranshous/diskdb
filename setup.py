from setuptools import setup

requirements = [
]

setup(
    name="diskdb",
    version='0.0.2',
    author="Robby Ranshous",
    author_email="rranshous@gmail.com",
    description="simple disk based k/v store",
    keywords="database",
    url="https://github.com/rranshous/diskdb",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Database",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=requirements,
)
