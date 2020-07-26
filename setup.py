from setuptools import setup, find_packages

with open("README.md") as f:
    readme  =  f.read()

with open("LICENSE") as f:
    license  =  f.read()

setup(
    name = "pypass",
    version = "0.1.0",
    description = "Command-line password manager",
    long_description = readme,
    author = "Joe Tacheron",
    author_email = "joetache4@gmail.com",
    url = "https://github.com/joetache4/pypass",
    license = license,
    packages = find_packages(exclude = ("tests", "docs"))
)