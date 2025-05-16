from setuptools import setup, find_packages

setup(
    name="xview",  # Le nom de ton package
    version="0.1",  # Version de ton package
    packages=find_packages(),  # Trouver tous les packages Python automatiquement
    install_requires=[  # Dépendances nécessaires
        # Liste ici les bibliothèques que ton package requiert, si nécessaire
    ],
    include_package_data=True,  # Inclure d'autres fichiers nécessaires dans le package
    description="Librairie Python pour visualiser l'apprentissage de modèle de machine learning.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Joffrey Michaud",
    author_email="joffrey.michaud@outlook.fr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Spécifie la version Python minimale
)
