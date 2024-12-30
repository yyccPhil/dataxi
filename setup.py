import setuptools
import re
# import requests
# from bs4 import BeautifulSoup

package_name = "data-injection"


def curr_version():
    with open('VERSION') as f:
        version_str = f.read()
    return version_str


def get_version():
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", curr_version())
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    patch += 1
    if patch > 9:
        patch = 0
        minor += 1
        if minor > 9:
            minor = 0
            major += 1
    new_version_str = f"{major}.{minor}.{patch}"
    return new_version_str


def upload():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    with open('requirements.txt') as f:
        required = f.read().splitlines()

    setuptools.setup(
        name=package_name,
        version=curr_version(),
        author="Yuan Yuan",
        author_email="yyccphil@gmail.com",
        description="Data injection is a cross-DBMS server tool that can help you centralize the data extraction and transfer from different data sources.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url=f"https://pypi.org/project/{package_name}/",
        packages=setuptools.find_packages(),
        data_files=["requirements.txt"], # yourtools库依赖的其他库
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
        install_requires=required,
    )


def write_now_version():
    print("Current VERSION:", get_version())
    with open("VERSION", "w") as version_f:
        version_f.write(get_version())


def main():
    try:
        upload()
        print("Upload success , Current VERSION:", curr_version())
    except Exception as e:
        raise Exception("Upload package error", e)


if __name__ == '__main__':
    main()

