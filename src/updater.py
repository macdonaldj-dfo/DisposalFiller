import requests
import var


def check_for_update():

    response = requests.get(var.git_url)

    if response.status_code != 200:
        return False

    latest_version = response.url.split("/").pop()

    if latest_version > var.__version__:
        return True
    else:
        return False





