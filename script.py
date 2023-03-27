from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime, timedelta
import os
import glob

class interactiveReports:

    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : os.getcwd()+"\\pdf"}
        chromeOptions.add_experimental_option("prefs",prefs)
        self.driver =  webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chromeOptions)
        self.wait =  WebDriverWait(self.driver, 20)
        

    def startWorking(self):
        self.driver.get("https://ndcdyn.interactivebrokers.com/sso/Login?RL=1&locale=en_US")
        self.driver.find_element(By.XPATH, value='//*[@id="authcredentials"]/div[1]/div/p[1]/span[2]').click()
        #typing credentials
        self.driver.find_element(By.XPATH, value="//input[@id='user_name']").send_keys("emagin909")
        self.driver.find_element(By.XPATH, value="//input[@id='password']").send_keys("Alex1234!")
        self.driver.find_element(By.XPATH, value="//button[@id='submitForm']").click()
        sleep(5)
        self.getReport()

    def getReport(self):
        #Navigating to the statemtns page
        self.driver.get("https://ndcdyn.interactivebrokers.com/AccountManagement/AmAuthentication?action=Statements")
        awaitedEl=self.wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(),'Activity')]/parent::p/parent::div/following-sibling::div/p/span/a")))
        awaitedEl.click()
        sleep(2)
        #Selecting Custom Date Range
        self.driver.find_element(By.XPATH, value="//option[contains(text(),'Custom Date Range')]").click()
        sleep(1)
        dateToday = datetime.today().strftime("%Y-%m-%d")
        dfrom = datetime.today() - timedelta(days=1)
        dfrom = dfrom.strftime("%Y-%m-%d")

        fromel=self.driver.find_element(By.XPATH, value = "//input[@name='fromDate']")
        self.driver.execute_script("arguments[0].value='{}'".format(dfrom),fromel)
        toel=self.driver.find_element(By.XPATH, value = "//input[@name='toDate']")
        self.driver.execute_script("arguments[0].value='{}'".format(dateToday),toel)
        self.driver.find_element(By.XPATH, value="(//p[contains(text(),'HTML')]/parent::div/following-sibling::div/p/span/a[last()])[1]").click()
        sleep(5)

    def uploadToBucket(self):
        latestFile = glob.glob(os.getcwd()+"\\pdf\\*.pdf")
        latestFile = latestFile[0]
        

interactiveReports().startWorking()

