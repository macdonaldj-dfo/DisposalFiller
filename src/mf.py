import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from var import XPaths, murl, Result


class MFException(Exception):
    pass


class MFExceptionNoResults(MFException):
    pass


class MF:

    short_timeout = 10
    long_timeout = 30

    def __init__(self):
        self.browser = None
        self.current_asset = ""

        self.attributes = dict()

    def login(self, username, password):
        """
        Create a webdriver and log in to maximo webpage.
        """
        # Create the browser object
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)
        self.browser.get(murl)

        # Find the credential boxes and submit cred
        user_box = self.browser.find_element(By.NAME, "username")
        pass_box = self.browser.find_element(By.NAME, "password")

        user_box.send_keys(username)
        pass_box.send_keys(password)
        pass_box.send_keys(Keys.RETURN)

        if self.browser.title != "Assets":
            self.browser.close()
            return False

        return True

    def wait_for_element(self, xpath):
        """
        Wait for a given element to load for as long as our timeout. Raise an error if it fails.
        """
        try:
            element = EC.presence_of_element_located((By.XPATH, xpath))
            return WebDriverWait(self.browser, MF.short_timeout).until(element)
        except TimeoutException:
            raise MFException(f"Timeout waiting for the page to load: {xpath}")
        except Exception as e:
            raise MFException("Unexpected error while waiting for element") from e

    def wait_for_clickable_element(self, xpath):
        """
        Wait for a given element that should be clickable to load
        """
        try:
            element = EC.element_to_be_clickable((By.XPATH, xpath))
            return WebDriverWait(self.browser, MF.short_timeout).until(element)
        except TimeoutException:
            raise MFException(f"Timeout waiting for clickable element: {xpath}")
        except Exception as e:
            raise MFException("Unexpected error while waiting for clickable element") from e

    def wait_for_results(self):
        """
        Wait for a result or a no result popup
        """
        options = (
            XPaths.get("NoRecordsOK") + "[contains(text(), 'OK')]",
            XPaths.get("Name")
        )

        element = None
        opt = -1
        # Horrible loop until success or failure
        while not element:
            for i in range(len(options)):
                try:
                    element = self.browser.find_element(By.XPATH, options[i])
                    opt = i
                    break
                except NoSuchElementException:
                    pass
                except Exception as e:
                    raise MFException("An unexpected error occurred waiting for results")

        if opt == 0:
            # Even though it found the button it isn't immediately clickable
            self.wait_for_clickable_element(XPaths.get("NoRecordsOK")).click()
            raise MFExceptionNoResults("No results found for asset")
        elif opt == -1:
            raise MFException("An unexpected error occurred waiting for results")

    def search_for_asset(self):
        """
        Open the advanced search window and enter the details
        """
        adv_btn = self.wait_for_element(XPaths.get("AdvButton"))

        if not adv_btn:
            raise MFException("Could not find the search button")

        adv_btn.click()
        adv_asset_box = self.wait_for_element((XPaths.get("AdvAsset")))
        if not adv_asset_box:
            raise MFException("Could not find search box")

        adv_asset_box.clear()
        adv_asset_box.send_keys(self.current_asset)

        adv_status_box = self.wait_for_element(XPaths.get("AdvStatus"))
        if not adv_status_box:
            raise MFException("Could not find the status box")

        adv_status_box.clear()
        adv_status_box.send_keys("%")
        adv_status_box.send_keys(Keys.RETURN)

    def collect_attributes(self):
        """
        Loop through all the desires attributes and grab them from the webpage
        """
        for term in self.attributes.keys():
            attribute_box = self.wait_for_element(XPaths.get(term))

            if not attribute_box:
                raise MFException("Error finding the asset details")

            # Collect the value from the html element and assign it to out dictionary
            self.attributes[term] = attribute_box.get_attribute("value")

    def return_to_search(self):
        """
        Return to search from the asset view
        """
        returnButton = self.wait_for_element(XPaths.get("ReturnButton"))

        if not returnButton:
            raise MFException("Could not return to search")

        returnButton.click()

    def clear_search(self):
        """
        Clear the search results and refresh for good measure
        """
        clearButton = self.wait_for_element(XPaths.get("ClearButton"))

        if not clearButton:
            raise MFException("Could not clear the results")

        clearButton.click()

        # An alert asking if you want to proceed without saving will pop up, we must accept and move without saving
        self.browser.refresh()
        alert = self.browser.switch_to.alert
        alert.accept()

        time.sleep(0.5)

    def get_asset_data(self, assetNum):
        """
        Perform all search operations to retrieve the asset data
        """
        self.attributes.clear()
        self.attributes = {
            "Name": "",
            "LocalInfo": "",
            "Manufacturer": "",
            "PartNumber": "",
            "SerialNumber": "",
            "Location": ""
        }

        self.current_asset = assetNum

        print(f"Begin search for {assetNum}")

        try:
            print("search")
            self.search_for_asset()
            print("wait for result")
            self.wait_for_results()
            print("collect")
            self.collect_attributes()
            print("return")
            self.return_to_search()
            print("Clear")
            self.clear_search()

        except MFExceptionNoResults as e:
            return e
        except MFException as e:
            print(e)
            return e
        except Exception as e:
            print("An unexpected error has occurred!")
            print(e)
            return e

        self.attributes["AssetNumber"] = assetNum
        return Result(self.attributes)
