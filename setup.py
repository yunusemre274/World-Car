from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="worldcar",
    version="0.1.0",
    author="Your Name",
    description="Graph-Based Intelligent Route & Traffic Simulation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/worldcar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "osmnx>=1.9.0",
        "networkx>=3.2",
        "shapely>=2.0.0",
        "geopandas>=0.14.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "jupyter>=1.0.0",
            "matplotlib>=3.8.0",
            "folium>=0.15.0",
        ],
    },
)
