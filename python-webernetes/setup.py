from setuptools import setup, find_packages

setup(
    name="webernetes_wrapper",
    version="1.0.0",
    description="Python wrapper for the webernetes javascript API",
    author="Your Name",
    packages=find_packages(),
    package_data={
        "webernetes_wrapper": ["bridge.js"],
    },
    install_requires=[
        # No extra python dependencies needed. Node.js must be installed.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "webernetes-python=webernetes_wrapper.__main__:main",
        ],
    },
    python_requires='>=3.6',
)
