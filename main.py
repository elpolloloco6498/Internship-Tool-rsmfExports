import eel
import os
import shutil
import time
from datetime import datetime
import keyring
import json
import pathlib
from pprint import pprint

# selenium imports
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

eel.init("web")

# general variables

# function definition
def login(driver, credentials):
    driver.find_element(by=By.NAME, value="user").send_keys(credentials["username"])
    driver.find_element(by=By.NAME, value="password").send_keys(credentials["password"])
    driver.find_element(by=By.CSS_SELECTOR, value=".loginButton").click()

def logout(driver):
    print("Finished !")
    driver.close()

def listEqualContent(list1, list2):
    if len(list1) == len(list2):
        for elt in list1:
            if elt not in list2:
                return False
        return True
    return False

def getAllDocsInDir(dir):
    return os.listdir(dir)

def getDocInfosDir(dir):
    infos = []
    for doc in os.listdir(dir):
        infos.append({
            "date": datetime.fromtimestamp(os.stat(os.path.join(dir, doc)).st_ctime).strftime("%d/%m/%y %H:%M"),
            "name": doc
        })
    return infos

def latest_download_file(dir):
    os.chdir(dir)
    files = sorted(os.listdir('.'), key=os.path.getmtime)
    os.chdir('..')
    if files:
        print(f"Files in download dir : {files}")
        return files[len(files) - 1]
    print("No files found")
    return None

def renameFile(filename, searchId, searchIdValue):
    name, ext = filename.split('.')
    return f"{name}_{searchId}_{searchIdValue}.{ext}"

@eel.expose
def downloadData(confStr):
    downloadConf = json.loads(confStr)
    pprint(downloadConf)
    with open('config.json', 'r', encoding='utf-8') as f:
        confRSMF = json.load(f)
        #pprint(confRSMF)
    
    RSMF_URL = confRSMF["app"]["url"]
    DOWNLOAD_DIR = os.path.join(pathlib.Path().absolute(), "exports")  # directory in which files will be downloaded
    REPORT_FILE = confRSMF["selenium"]["report"]
    GECKO_DRIVER_PATH = confRSMF["selenium"]["geckodriver"]

    # TODO test list docs
    print(getDocInfosDir(DOWNLOAD_DIR))
    eel.renderDownloadedDocuments(getDocInfosDir(DOWNLOAD_DIR))

    credentials = {
        "username": confRSMF["app"]["username"],
        "password": keyring.get_password(confRSMF["app"]["name"], confRSMF["app"]["username"])
    }

    queries = downloadConf["queries"]

    serv = Service(GECKO_DRIVER_PATH)

    options = FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False);
    options.set_preference("browser.helperApps.alwaysAsk.force", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/plain, application/vnd.ms-excel, text/csv, text/comma-separated-values, application/octet-stream")
    options.set_preference("browser.download.dir", DOWNLOAD_DIR)
    
    # Initializing the driver
    driver = webdriver.Firefox(service=serv, options=options)
    driver.implicitly_wait(50)
    actionChains = ActionChains(driver)

    driver.get(RSMF_URL)

    login(driver, credentials)

    # Accessing the data
    time.sleep(20)

    for query in queries:
        searchIds = query["searchIds"]
        searchIds = [id.replace(' ', '') for id in searchIds]
        exportFields = query["exports"]

        print(f"Current query : {query['name']}")

        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[@id='DATA']/a/div/span"))).click()
        time.sleep(3)  # load page
        driver.switch_to.frame(1)
        time.sleep(3)

        link = driver.find_element(by=By.XPATH, value=f"//span[contains(text(), '{query['name']}')]")
        actionChains.double_click(link).perform()

        time.sleep(8)

        print(searchIds)
        for id in searchIds:
            print(f"Current ID : {id}")
            # choosing a specific bank with ID
            inputId = driver.find_element(by=By.XPATH,
                                          value=f"//div[@class='property-container']/label[contains(text(),'{query['searchBy'].upper()}')]/following-sibling::div[1]/input")
            inputId.clear()
            inputId.send_keys(id)
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//td[contains(text(),'Run Search')]"))).click()

            time.sleep(7)

            # select first element list search results
            search_result_item = driver.find_elements(by=By.XPATH, value="//table[@class='extdt-table-layout rich-table ']/tbody/tr")[1]
            actionChains.double_click(search_result_item).perform()

            time.sleep(7)

            # access general menu
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='rich-label-text-decor']/img[@class='more_actions_button']"))).click()

            time.sleep(1)

            # access export
            actionChains.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys("e").key_up(Keys.CONTROL).key_up(
                Keys.ALT).perform()

            time.sleep(1)

            # check export data to see if creating a new config is necessary
            selectedColumns = driver.find_elements(by=By.XPATH,
                                                   value="//div[@class='rich-panel-body ']/table/tbody/tr[2]/td[3]/div/div/div/table/tbody/tr/td[3]")
            selectedColumns = [elt.text for elt in selectedColumns]
            print(selectedColumns)
            if not listEqualContent(selectedColumns, exportFields):
                # create new config
                # enter export settings
                settingsMenu = driver.find_elements(by=By.XPATH, value="//div[@class='rich-label-text-decor']")[1]
                settingsMenu.click()

                time.sleep(1)

                actionChains.move_to_element(settingsMenu).perform()
                actionChains.move_by_offset(0, 20).click().perform()

                time.sleep(1)

                inputConfigName = driver.find_element(by=By.XPATH,
                                                      value="//td[@class='spn-mpnl-pnl-b spn-mpnl-body']/div/input")
                inputConfigName.clear()

                time.sleep(1)

                inputConfigName.send_keys('config')
                driver.find_element(by=By.XPATH, value="//td[contains(text(), 'OK')]").click()

                time.sleep(1)

                # create config export
                for field in exportFields:
                    fieldElt = driver.find_element(by=By.XPATH, value=f"//td[contains(text(), '{field}')]")
                    fieldElt.click()
                    time.sleep(3)
                    addBtn = driver.find_elements(by=By.XPATH, value="//input[@class='pagerButton']")[0]
                    addBtn.click()
                    time.sleep(3)

            # export csv
            driver.find_elements(by=By.XPATH, value="//div[@class='sipbutton']")[4].click()

            time.sleep(3)

            if not listEqualContent(selectedColumns, exportFields):
                # do not save dialog
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//td[contains(text(), 'Do not Save')]"))).click()

            time.sleep(10)

            # render downloaded documents JS
            newestFile = latest_download_file(DOWNLOAD_DIR)
            shutil.move(os.path.join(DOWNLOAD_DIR, newestFile),
                        os.path.join(DOWNLOAD_DIR, renameFile(newestFile, query["searchBy"], id)))

            eel.renderDownloadedDocuments(getDocInfosDir(DOWNLOAD_DIR))

            # close current tab
            driver.find_elements(by=By.XPATH, value="//div[@class='tabPanelIcon']/div")[1].click()

            time.sleep(6)

        # rename

        # close tab query menu
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='tabPanelIcon']/div"))).click()

        time.sleep(1)

    eel.removeDownloadSpinner()

    # go to data manager
    logout(driver)

# Start the index.html file
eel.start("index.html", mode='edge', port=8000)
