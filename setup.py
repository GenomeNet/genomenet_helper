from setuptools import setup, find_packages

setup(
    name="genomenet_helper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Bio',
        'numpy',
        'b2sdk',
    ],
    entry_points={
        'console_scripts': [
            'genomenet_helper=genomenet_helper.__main__:main',
        ],
    },
)
