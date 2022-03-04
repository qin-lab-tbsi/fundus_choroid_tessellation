from setuptools import setup, find_packages 

with open('README.md', 'r') as fd:
    readme = fd.read


with open('LICENSE', 'r') as fd:
    license = fd.read


setup(
    name = "tessellator",
    version = "1.0.0",
    description = "Some description about the package/project",
    long_description=readme,
    long_description_content_type="text/markdown", 
    url="git_project_url", 
    author='bilha g',
    author_email='bilha.analytics@gmail.com',
    license = license,
    packages=find_packages(exclude=('tests', 'docs', 'notebooks') ),
    python_requires=">=3.6", 
    classifiers = [ ## index and pip metadata << https://pypi.org/classifiers/
        "Programming Language :: Python :: 3", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", 
    ]
)