from setuptools import setup, find_packages

#with open("requirements.txt") as f:
#	install_requires = f.read().strip().split("\n")

install_requires = [
    "GitPython==3.1.27",
    "pyyaml==5.4.1"
]

# get version from __version__ variable in engage/__init__.py
from engage import __version__ as version

setup(
	name="engage",
	version=version,
	description="Engage is a live training application",
	author="Pipal Academy",
	author_email="anand@pipal.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
