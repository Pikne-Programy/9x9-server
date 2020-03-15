import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="9x9-server-Pikne-Programy",
    version="0.0.1",
    author="Nircek",
    author_email="nircek-2103@protonmail.com",
    description="The Server Software of 9x9 Game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pikne-Programy/9x9-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
