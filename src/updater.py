import requests
import var


def check_for_update():

    response = requests.get(var.git_url)

    if response.status_code != 200:
        print("Bad status code from github")
        return False

    latest_version = response.url.split("/").pop()

    print(f"Current version: {var.__version__}. Latest version: {latest_version}")

    if latest_version > var.__version__:
        return True
    else:
        return False





