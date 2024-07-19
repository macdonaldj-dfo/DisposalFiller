__version__ = "v0.3.0"

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

XPaths = {
    "AssetBox":     "//*[@id='m6a7dfd2f_tfrow_[C:1]_txt-tb']",
    "AssetItem":    "//*[@id='m6a7dfd2f_tdrow_[C:1]_ttxt-lb[R:0]']",
    "ReturnButton": "//*[@id='m397b0593-tabs_middle']",
    "Name":         "//*[@id='m73f28d7-tb2']",
    "LocalInfo":    "//*[@id='m46652238-tb']",
    "Manufacturer": "//*[@id='me8f323cc-tb2']",
    "PartNumber":   "//*[@id='mbe745998-tb']",
    "SerialNumber": "//*[@id='m5bd63dc-tb']",
    "Location":     "//*[@id='m7b0033b9-tb']",
    "StopSearch":   "//*[@id='m4b77cc6f-pb']",
    "Loading":      "//*[@id='query_longopwait-dialog_inner']",
    "ClearButton":  "//*[@id='m6a7dfd2f-ti3_img']",
    "NoResults":    "//*[@id='m6a7dfd2f_tbod_tempty_tcell_statictext-lb']",
    # "WholeTable": 'id("m6a7dfd2f_tbod-tbd")/tbody[1]'
    "AdvButton": "//*[@id='m68d8715f-tbb_text']",
    "AdvAsset": "//*[@id='md1329a0c-tb']",
    "AdvStatus": "//*[@id='m4f560faf-tb']",
    "NoRecordsOK": "//*[@id='m88dbf6ce-pb']"
}

maximo_url = "https://maximo.ccg-gcc.ent.dfo-mpo.ca/maximo/ui/?event=loadapp&value=asset"
git_url = "https://github.com/macdonaldj-dfo/DisposalFiller/releases/latest"


class Result:

    def __init__(self, res):
        self.Name = res.get("Name")
        self.AssetNumber = res.get("AssetNumber")
        self.Manufacturer = res.get("Manufacturer")
        self.SerialNumber = res.get("SerialNumber")
        self.PartNumber = res.get("PartNumber")
        self.Location = res.get("Location")
