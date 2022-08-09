from setuptools import find_packages, setup
import os

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

#
# the README file content is the long description
#
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
]

setup(
    name="careers",
    version="0.0.1",
    author="Donald Bacon",
    author_email="dwbzen@gmail.com",
    description="Careers Game game engine and server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/careers.git",
    packages=find_packages(exclude=["test",]),
    data_files=[('resources', ['resources/editions.json','resources/experienceCards_Hi-Tech.json','resources/opportunityCards_Hi-Tech.json',
                'resources/gameLayout_Hi-Tech.json', 'resources/gameLayout_UK.json',
                'resources/occupations_Hi-Tech.json','resources/occupations_UK.json',
                'resources/FMC_Hi-Tech.json','resources/UF_Hi-Tech.json'])],
    install_requires=requirements,
    license="MIT",
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Development",
		"Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
	    "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8',
    keywords="careers game",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
