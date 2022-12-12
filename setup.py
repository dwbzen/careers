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
    version="0.1.3",
    author="Donald Bacon",
    author_email="dwbzen@gmail.com",
    description="Careers Game game engine and server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwbzen/careers.git",
    packages=find_packages(exclude=["tests","docs"]),
    data_files=[('resources', ['resources/editions.json',
                'resources/Hi-Tech/experienceCards_Hi-Tech.json','resources/Hi-Tech/opportunityCards_Hi-Tech.json',
                'resources/Hi-Tech/gameParameters_Hi-Tech.json', 'resources/Hi-Tech/gameParameters_Hi-Tech_prod.json', 'resources/Hi-Tech/gameParameters_Hi-Tech_test.json',
                'resources/Hi-Tech/collegeDegrees_Hi-Tech.json', 'resources/Hi-Tech/gameLayout_Hi-Tech.json', 'resources/Hi-Tech/occupations_Hi-Tech.json',
                'resources/Hi-Tech/FMC_Hi-Tech.json','resources/Hi-Tech/UF_Hi-Tech.json', 'resources/Hi-Tech/Amazon_Hi-Tech.json', 'resources/Hi-Tech/ESPN_Hi-Tech.json',
                'resources/Hi-Tech/Disney_Hi-Tech.json','resources/Hi-Tech/Facebook_Hi-Tech.json','resources/Hi-Tech/Google_Hi-Tech.json',
                'resources/Hi-Tech/ListerAndBacon_Hi-Tech.json','resources/Hi-Tech/Pfizer_Hi-Tech.json', 'resources/Hi-Tech/SpaceX_Hi-Tech.json',
                
                'resources/UK/gameParameters_UK.json', 'resources/UK/gameParameters_UK_prod.json', 'resources/UK/gameParameters_UK_test.json',
                'resources/UK/collegeDegrees_UK.json',
                'resources/UK/AGRIVI_UK.json', 'resources/UK/Oxford_UK.json', 
                'resources/UK/Harrods_UK.json', 'resources/UK/Arsenal_UK.json', 'resources/UK/Stonehenge_UK.json',
                'resources/UK/ListerAndBacon_UK.json', 'resources/UK/BBCNews_UK.json', 
                'resources/UK/TowerOfLondon_UK.json', 'resources/UK/Pfizer_UK.json', 'resources/UK/RollsRoyce_UK.json',
                'resources/UK/experienceCards_UK.json', 'resources/UK/opportunityCards_UK.json'
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
    python_requires='>=3.10',
    keywords="careers game",
    maintainer='Donald Bacon',
    maintainer_email='dwbzen@gmail.com'
)
