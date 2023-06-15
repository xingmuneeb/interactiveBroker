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
        self.driver.find_element(By.XPATH, value="//*[@id='authcredentials']/div[1]/div/p[1]/span[2] | //span[contains(text(),'Live')]/following-sibling::label").click()
        #typing credentials
        sleep(2)
        self.driver.find_element(By.XPATH, value="//input[@id='user_name'] | //input[@name='username']").send_keys("emagin910")
        self.driver.find_element(By.XPATH, value="//input[@id='password'] | //input[@name='password']").send_keys("alpha2023!1")
        self.driver.find_element(By.XPATH, value="//button[@id='submitForm'] | (//button[@type='submit'][contains(text(),'Login')])[1]").click()
        sleep(10)
        self.getReport()

    def getReport(self):
        #Navigating to the statemtns page
        awaitedEl=self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'Performance & Reports')]")))
        awaitedEl.click()
        sleep(1)
        awaitedEl=self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'PortfolioAnalyst')]")))
        awaitedEl.click()
        # self.driver.get("https://www.interactivebrokers.co.uk/AccountManagement/AmAuthentication?action=PORTFOLIOANALYST_BETA")
        awaitedEl=self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(),'Reports')]")))
        awaitedEl.click()
        sleep(4)
        #Getting All PDFs
        pdfs = self.driver.find_elements(By.XPATH,value="(//i[contains(@class,'fa-file-pdf')]/parent::a)[position()>2]")
        for pdf in pdfs:
            pdf.click()
            sleep(5)

    def uploadToBucket(self):
        latestFile = glob.glob(os.getcwd()+"\\pdf\\*.pdf")
        latestFile = latestFile[0]
        

interactiveReports().startWorking()

