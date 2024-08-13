import requests
import base64
import json
from var import max_api_url, Result


class MaxAPI:

    def __init__(self):

        self.session = requests.session()

    def login(self, username, password):
        """
        Log in to maximo using api
        """
        # Encode the string to bin so it can then be encoded to b64
        up64 = base64.b64encode(f"{username}:{password}".encode())
        header = {"maxauth": up64}
        response = self.session.post(url=max_api_url + "/login", headers=header, verify=False)

        if response.status_code == 200:
            return True
        else:
            return False

    def get_asset_data(self, assetnum):
        """
        Search for an asset, returns a dict of attributes
        """
        params = {
            "oslc.where": f'assetnum="%{assetnum}%"',
            "oslc.select": 'assetnum,location,description,serialnum,manufacturer.name,ccg_modelnum'
        }
        response = self.session.get(url=max_api_url + "/os/mxasset", params=params, verify=False)

        if response.status_code == 200:
            return self.create_dict(response)
        else:
            return None

    def create_dict(self, response):
        """
        convert the json response to a result object
        """
        js = json.loads(response.text)
        data = js.get("rdfs:member")

        if len(data) == 0:
            return None

        result = Result()

        result.Name = data[0].get("spi:description")
        result.AssetNumber = data[0].get("spi:assetnum")
        result.Manufacturer = data[0].get("manufacturer").get("name")
        result.PartNumber = data[0].get("spi:ccg_modelnum")
        result.SerialNumber = data[0].get("spi:serialnum")
        result.Location = data[0].get("spi:location")

        return result

def pretty_print(response):
    """Function to print request json objects"""
    parsed = json.loads(response.text)
    print(json.dumps(parsed, indent=4))