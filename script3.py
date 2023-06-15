from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime, timedelta
import os
import dateutil.relativedelta
from datetime import datetime

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
        #Scroll Down Selenium python
        self.driver.execute_script("window.scrollTo(0, 1000)") 
        #Clicking custom report run

        self.driver.find_element(By.XPATH, value="//a[@ng-click='$ctrl.openOptionsModal(report)']").click()
        sleep(5)

        toDateVal = self.driver.find_element(By.XPATH, value="//input[@name='toDate']").get_attribute("value")
        toDate = datetime.strptime(toDateVal, "%Y-%m-%d")
        oneMonthPrior = toDate - dateutil.relativedelta.relativedelta(months=1)
        threeMonthPrior = toDate - dateutil.relativedelta.relativedelta(months=3)
        sixMonthPrior = toDate - dateutil.relativedelta.relativedelta(months=6)
        twelveMonthPrior = toDate - dateutil.relativedelta.relativedelta(months=12)

        oneMonthPriorString = datetime.strftime(oneMonthPrior,"%Y-%m-%d")
        threeMonthPriorString = datetime.strftime(threeMonthPrior,"%Y-%m-%d")
        sixMonthPriorString = datetime.strftime(sixMonthPrior,"%Y-%m-%d")
        twelveMonthPriorString = datetime.strftime(twelveMonthPrior,"%Y-%m-%d")
        self.driver.find_element(By.XPATH, value="//button[@aria-label='Close']").click()

        dates = [oneMonthPriorString,threeMonthPriorString,sixMonthPriorString,twelveMonthPriorString]

        for datee in dates:
            self.selectDate(datee)
            self.driver.find_element(By.XPATH, value="//a[contains(text(),'Run')]").click()
            sleep(5)


    def selectDate(self,date):
        self.driver.find_element(By.XPATH, value="//a[@ng-click='$ctrl.openOptionsModal(report)']").click()
        sleep(2)
        self.driver.find_element(By.XPATH, value="//input[@name='fromDate']").click()
        sleep(1)
        self.driver.find_element(By.XPATH, value="//div[contains(@class,'datepicker-days')]//tr[2]/th[2]").click()
        sleep(1)
        self.driver.find_element(By.XPATH, value="//div[contains(@class,'datepicker-months')]//tr[2]/th[2]").click()
        sleep(1)
        year, month, datte = date.split("-")[0],date.split("-")[1],date.split("-")[2]
        y=self.driver.find_element(By.XPATH, value=f"//div[contains(@class,'datepicker-years')]/table/tbody/tr/td/span[contains(text(),'{year}')]")
        self.driver.execute_script("arguments[0].click()",y)
        sleep(1)
        m=self.driver.find_element(By.XPATH, value=f"//div[contains(@class,'datepicker-months')]/table/tbody/tr/td/span[{month}]")
        self.driver.execute_script("arguments[0].click()",m) 
        sleep(1)
        days=self.driver.find_element(By.XPATH, value=f"//div[contains(@class,'datepicker-days')]/table/tbody/tr/td[contains(text(),'{datte}')]")
        self.driver.execute_script("arguments[0].click()",days)





    def uploadToBucket(self):
        latestFile = glob.glob(os.getcwd()+"\\pdf\\*.pdf")
        latestFile = latestFile[0]
        

interactiveReports().startWorking()

