__version__ = "v0.4.0"

max2pdf = {
    "Description":      "Asset Description",
    "Asset Num":        "Inventory Number (Tag)",
    "Manufacturer":     "Maufacturer",
    "Serial Num":       "Current location of Asset",
    "Model Num":        "Model Number",
    "Location":         "Current location of Asset_1",
    "Date":             "Date",
    "Details":          "Condition details",
    "Operational":      "Check Box1",
    "Repair Required":  "Check Box2",           # Value is either '/Off'   or   '/Yes'
    "Parts Only":       "Check Box3",
    "Scrap Only":       "Check Box4",
    "Unknown":          "Check Box15",
    "HazardFree":       "Select Yes or No3"     # '/V'  :   ['Select', 'Yes', 'No']
}

max_api_url = "https://maximo.ccg-gcc.ent.dfo-mpo.ca/maximo/oslc"

class Result:

    def __init__(self, res=None):
        if res is None:
            res = dict()

        self.Name = res.get("Name")
        self.AssetNumber = res.get("AssetNumber")
        self.Manufacturer = res.get("Manufacturer")
        self.SerialNumber = res.get("SerialNumber")
        self.PartNumber = res.get("PartNumber")
        self.Location = res.get("Location")
