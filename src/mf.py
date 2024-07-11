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
        try:
            element = EC.presence_of_element_located((By.XPATH, xpath))
            return WebDriverWait(self.browser, MF.short_timeout).until(element)
        except TimeoutException:
            raise MFException(f"Timeout waiting for the page to load: {xpath}")
        except Exception as e:
            raise MFException("Unexpected error while waiting for element") from e

    def adv_wait(self, xpath, loaded=False):

        t = [
            xpath,
            XPaths.get("NoResults") + "[contains(text(), 'There are no rows to display')]",
        ]

        if not loaded:
            t.append(XPaths.get("Loading"))

        element = None

        opt = -1

        while not element:
            for i in range(len(t)):
                try:
                    element = self.browser.find_element(By.XPATH, t[i])
                    print(f"found {t[i]}")
                    opt = i
                    break
                except:
                    pass

        if opt == 0:
            return element
        elif opt == 1:
            raise MFExceptionNoResults("No results found during adv search")
        elif opt == 2:
            print("Maximo is loading")
            return self.wait_for_load(xpath)
        else:
            raise MFException("An unexpected error occurred during adv search!")

    def wait_for_load(self, xpath):
        # Loading window exists, so wait for it to go away
        try:
            element = EC.presence_of_element_located((By.XPATH, XPaths.get("Loading")))
            WebDriverWait(self.browser, MF.long_timeout).until_not(element)
        except TimeoutException:
            raise MFException("Maximo is taking too long")
        except Exception as e:
            raise MFException("An unexpected error occurred") from e

        print("loading box gone, resume search for asset item")

        return self.adv_wait(xpath, loaded=True)

    def search_for_asset(self):

        assetbox = self.wait_for_element(XPaths.get("AssetBox"))

        if not assetbox:
            raise MFException("Could not find the search bar")

        assetbox.clear()
        assetbox.send_keys(self.current_asset)
        assetbox.send_keys(Keys.RETURN)

    def select_asset_result(self):

        assetitem = self.adv_wait(XPaths.get("AssetItem"))

        if not assetitem:
            raise MFException("Error finding results!")

        try:
            assetitem.click()
        except StaleElementReferenceException as e:
            print("Stale element, reselect")
            self.select_asset_result()

    def collect_attributes(self):

        for term in self.attributes.keys():
            attribute_box = self.wait_for_element(XPaths.get(term))

            if not attribute_box:
                raise MFException("Error finding the asset details")

            # Collect the value from the html element and assign it to out dictionary
            self.attributes[term] = attribute_box.get_attribute("value")

    def return_to_search(self):

        returnButton = self.wait_for_element(XPaths.get("ReturnButton"))

        if not returnButton:
            raise MFException("Could not return to search")

        returnButton.click()

    def clear_search(self):
        clearButton = self.wait_for_element(XPaths.get("ClearButton"))

        if not clearButton:
            raise MFException("Could not clear the results")

        clearButton.click()

        self.browser.refresh()
        alert = self.browser.switch_to.alert
        alert.accept()

        time.sleep(0.5)

    def get_asset_data(self, assetNum):

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
            print("select")
            self.select_asset_result()
            print("collect")
            self.collect_attributes()
            print("reset")
            self.return_to_search()

        except MFExceptionNoResults as e:
            self.clear_search()
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
