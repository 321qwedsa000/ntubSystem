from setuptools import setup,find_packages
__version__ = "1.0b"
setup(
    name="ntubSystem",
    version=__version__,
    author="TecHaonical",
    description="NTUB 選課系統",
    keywords="ntub",
    license='MIT',
    url="https://github.com/321qwedsa000/ntubSystem",
    packages=find_packages(where="src"),
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    python_requires='>=3.6'
)