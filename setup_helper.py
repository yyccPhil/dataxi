import re
import requests

package_name = "dataxi"


def curr_version():
    # with open('VERSION') as f:
    #     version_str = f.read()
    # return version_str
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    latest_version = data["info"]["version"]
    return latest_version

def get_version():
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", curr_version())
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    patch += 1
    # if patch > 9:
    #     patch = 0
    #     minor += 1
    #     if minor > 9:
    #         minor = 0
    #         major += 1
    new_version_str = f"{major}.{minor}.{patch}"
    return new_version_str

def update_version_file():
    new_version = get_version()
    with open("VERSION", "w") as f:
        f.write(new_version)
    print(f"Updated version to {new_version}")


if __name__ == '__main__':
    update_version_file()

