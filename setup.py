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
    version="0.1.0",
    author="Donald Bacon",
    author_email="dwbzen@gmail.com",
    description="Careers Game game engine and server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/careers.git",
    packages=find_packages(exclude=["test",]),
    data_files=[('resources', ['resources/editions.json','resources/experienceCards_Hi-Tech.json','resources/opportunityCards_Hi-Tech.json',
                'resources/gameParameters_Hi-Tech.json',
                'resources/collegeDegrees_Hi-Tech.json', 'resources/gameLayout_Hi-Tech.json', 'resources/occupations_Hi-Tech.json',
                'resources/FMC_Hi-Tech.json','resources/UF_Hi-Tech.json', 'resources/Amazon_Hi-Tech.json', 'resources/ESPN_Hi-Tech.json',
                'resources/Disney_Hi-Tech.json','resources/Facebook_Hi-Tech.json','resources/Google_Hi-Tech.json',
                'resources/ListerAndBacon_Hi-Tech.json','resources/Pfizer_Hi-Tech.json', 'resources/SpaceX_Hi-Tech.json'
                ])],
    install_requires=requirements,
    license="MIT",
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Developers",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.9',
    keywords="careers game",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
