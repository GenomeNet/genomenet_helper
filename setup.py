from setuptools import setup, find_packages

setup(
    name="genomenet_helper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Biopython',
        'numpy',
        'b2sdk',
        'ncbi-genome-download',
        'appdirs',
         'pandas',
        'scikit-learn',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'genomenet_helper=genomenet_helper.__main__:main',
        ],
    },
)
