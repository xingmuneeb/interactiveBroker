import platform
import glob
import re
import io
import json
import logging
import os
import time
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep
import boto3
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

session = requests.Session()
session.trust_env = False
from random import shuffle
from typing import Any, Dict, List, Union
import numpy as np
from bs4 import BeautifulSoup

s3 = boto3.client('s3')

# logging.basicConfig(level=logging.INFO)
# LOGGER = logging.getLogger(__name__)

now = datetime.utcnow()
timestamp = now.strftime("%Y%m%d%H%M%S")
dateToday = datetime.today().strftime("%Y-%m-%d")
report_date = (pd.to_datetime(dateToday) - timedelta(days=1)).strftime("%Y%m%d")

from database_moniz import AWSClient

def main():

    def is_running_on_lambda():
        return 'AWS_EXECUTION_ENV' in os.environ and 'LAMBDA_TASK_ROOT' in os.environ

    if is_running_on_lambda():
        print("Running on AWS Lambda")
    else:
        print("Running on a local machine")
                    
    def enable_download_headless(browser,download_dir):
        browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        browser.execute("send_command", params)

        
    def html_parse(page, names: List[str]) -> pd.DataFrame:
        soup = BeautifulSoup(page, "html.parser")
        x = []
        for ele in soup.find_all("tr"):
            link = ele.find("td")
            if link is not None:
                info = [" ".join(x.text.split()) for x in ele.find_all("td")]
                if (
                    (len(info) == 11)
                    and (" C" in info[0] or " P" in info[0])
                    and ("Total" not in info[0])
                    and (
                        info[10] == "C"
                        or info[10] == "P"
                        or info[10] == "C;P"
                        or info[10] == "O"
                        or info[10] == "O;P"                                           
                    )
                ):
                    x.append(dict(zip(names, info)))

        ibkr_activity = pd.DataFrame(x)

        return ibkr_activity


    class interactiveReports:
            
        def __init__(self):
            self.service = ChromeService(executable_path='/opt/chromedriver')
            self.options = Options()
            if is_running_on_lambda():

                self.options.binary_location = '/opt/headless-chromium'
            
            # self.options.add_argument("--headless=new")
            self.options.add_argument("--headless")
            self.options.add_argument('--no-sandbox')
            self.options.add_argument('--start-maximized')
            self.options.add_argument('--start-fullscreen')
            self.options.add_argument('--single-process')
            self.options.add_argument('--disable-dev-shm-usage')
            # set donwload path default
            self.options.add_experimental_option("prefs", {
                # "profile.default_content_settings.popups": 0,
                "download.default_directory": r"/tmp",
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": True
            })
            self.driver = Chrome(
                service=self.service,
                options=self.options,
            )
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.execute_script("")
        
        def get(self):
            driver = Chrome('/opt/chromedriver', options=self.options)
            return driver


        def getReport(self, dateToday: str) -> None:

            dateYesterday = (pd.to_datetime(dateToday) - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )

            time.sleep(5)

            bucket = 'moniz-research-lab'
            key = 'screenshots/ibkr.png'
            # key = "resources/secrets/sam5_secrets.json"
            upload_path_screenshots = '/tmp/ibkr.png'
            if platform.system() == 'Windows':
                windows_path_prefix = 'c:/users/alexk/moniz-research-lab'
                upload_path_screenshots = f"{windows_path_prefix}{upload_path_screenshots}"
            # take a screenshot
            self.driver.save_screenshot(upload_path_screenshots)

            # save file to s3

            s3.upload_file(upload_path_screenshots, bucket, key)

            print("clicking on performance and reports")

            # Navigating to the statements page
            try:
                awaitedEl = self.driver.find_element(By.XPATH, "//button[contains(text(),'Performance & Reports')]")
                awaitedEl.click()
            except Exception as e:
                print("Exception when trying to find and click the element: ", e)
                return

            time.sleep(5)
            awaitedEl.click()
            time.sleep(1)
            awaitedEl = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[contains(text(),'Statement')]")
                )
            )
            awaitedEl.click()

            time.sleep(4)
            # Scroll Down Selenium python
            self.driver.execute_script("window.scrollTo(0, 1000)")
            awaitedEl = self.wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//strong[contains(text(),'Activity')]/parent::p/parent::div/following-sibling::div/p/span/a",
                    )
                )
            )
            awaitedEl.click()
            time.sleep(2)
            # Selecting Custom Date Range
            self.driver.find_element(
                By.XPATH, value="//option[contains(text(),'Custom Date Range')]"
            ).click()
            time.sleep(1)
            dfrom = datetime.today() - timedelta(days=1)
            dfrom = dfrom.strftime("%Y-%m-%d")

            fromel = self.driver.find_element(By.XPATH, value="//input[@name='fromDate']")
            self.driver.execute_script("arguments[0].value='{}'".format(dfrom), fromel)
            toel = self.driver.find_element(By.XPATH, value="//input[@name='toDate']")
            self.driver.execute_script(
                "arguments[0].value='{}'".format(dateYesterday), toel
            )
            self.driver.find_element(
                By.XPATH,
                value="(//p[contains(text(),'HTML')]/parent::div/following-sibling::div/p/span/a[last()])[1]",
            ).click()
            time.sleep(5)
        
        def startWorking(self, dateToday: str, ibkr_creds: List) -> None:
            ibkr_uid = ibkr_creds[0]
            ibkr_pwd = ibkr_creds[1]
            self.driver.get(
                "https://ndcdyn.interactivebrokers.com/sso/Login?RL=1&locale=en_US"
            )
            
            time.sleep(10)
            self.driver.find_element(
                By.XPATH,
                value="//*[@id='authcredentials']/div[1]/div/p[1]/span[2] | //span[contains(text(),'Live')]/following-sibling::label",
            ).click()

            # typing credentials
            time.sleep(2)
            self.driver.find_element(
                By.XPATH, value="//input[@id='user_name'] | //input[@name='username']"
            ).send_keys(ibkr_uid)
            print("typing password")
            self.driver.find_element(
                By.XPATH, value="//input[@id='password'] | //input[@name='password']"
            ).send_keys(ibkr_pwd)
            # take screenshot
            
            
            self.driver.find_element(
                By.XPATH,
                value="//button[@id='submitForm'] | (//button[@type='submit'][contains(text(),'Login')])[1]",
            ).click()
            print("logged in")
            time.sleep(10)
            self.getReport(dateToday)


    parser = ArgumentParser(description="")

    parser.add_argument(
        "--names",
        type=str,
        default="['Symbol', 'Date/Time', 'Quantity', 'T. Price', 'C. Price', "
        "'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L', 'MTM P/L', 'Code']",
        help="column names of interest [trades] from html",
    )

    key = "resources/secrets/sam5_secrets.json"
    download_path_secrets = '/tmp/moniz-research-lab-secrets.json'
    if platform.system() == 'Windows':
        windows_path_prefix = 'c:/users/alexk/moniz-research-lab'
        download_path_secrets = f"{windows_path_prefix}/{download_path_secrets}"

    s3 = boto3.client("s3")
    # s3.download_file(Bucket="moniz-research-lab", Key=key, Filename="/tmp/sam5_secrets.json")
    # download secrets.json from s3
    s3.download_file(
        "moniz-research-lab",
        key,
        download_path_secrets,
    )
    parser.add_argument(
        "--secrets",
        type=str,
        help="path to secrets file json",
        default="/tmp/sam5_secrets.json",
    )
    args = parser.parse_args()

    # open the sell_limits command line argument
    names = args.names
    names = names.replace("'", '"')
    """Note: read-in list of names via json"""
    names = json.loads(names)

    # aws credentials
    with open(download_path_secrets, "r") as f:
        secrets = json.load(f)

    aws_client = AWSClient(
        aws_access_key_id=secrets["aws_access_key_id"],
        aws_secret_access_key=secrets["aws_secret_access_key"],
        region_name=secrets["aws_region"],
    )

    ibkr_id = secrets["ibkr_paper_id"]
    ibkr_pwd = secrets["ibkr_paper_pwd"]
    ibkr_creds = [ibkr_id, ibkr_pwd]


    interactiveReports().startWorking(dateToday, ibkr_creds)
    
    print(f"report created at {timestamp}")

    # read in the htm and parse
    print("report date",report_date)
    if platform.system() == 'Windows':
        fname = f"{windows_path_prefix}/tmp/DU6852623_{report_date}_{report_date}.htm"
        print("list of files in /tmp folder: ")
        print(os.listdir(f"{windows_path_prefix}/tmp"))
    else:
        fname = f"/tmp/DU6852623_{report_date}_{report_date}.htm"
        print("list of files in /tmp folder: ")
        print(os.listdir(f"/tmp"))

    if os.path.exists(fname):
        HtmlFile = open(fname, "r", encoding="utf-8")
    else:
        print(f"File not found: {fname}")
        
        return
        
    ibkr_activity = html_parse(HtmlFile, names)
    print(f"got the ibkr activity html parsed")
    
    if ibkr_activity.empty:
        print(f"no activity for {report_date}")
        sys.exit(0)
    

    # make all headers lower case
    ibkr_activity.columns = map(str.lower, ibkr_activity.columns)
    # replace certain strings in column names
    ibkr_activity.rename(
        columns={
            "symbol": "series_id",
            "date/time": "date",
            "t. price": "transaction_price",
            "c. price": "closing_price",
            "comm/fee": "commission",
            "realized p/l": "realized profit",
            "mtm p/l": "mtm profit",
        },
        inplace=True,
    )

    # split date into date and time as distinct fields
    date_time = ibkr_activity["date"].str.split(",", expand=True)
    ibkr_activity["date"] = date_time[0].values
    ibkr_activity["time"] = date_time[1].values

    # set certain fields as type float
    cols = [
        "quantity",
        "transaction_price",
        "closing_price",
        "commission",
        "realized profit",
        "mtm profit",
    ]
    # remove commas from string values
    ibkr_activity.replace(",", "", regex=True, inplace=True)
    for col in cols:
        ibkr_activity[col] = ibkr_activity[col].astype(float)
    # reorder
    cols_at_begin = ["series_id", "date", "time"]
    ibkr_activity = ibkr_activity[
        [c for c in cols_at_begin if c in ibkr_activity]
        + [c for c in ibkr_activity if c not in cols_at_begin]
    ]

    # now upload to AWS
    aws_client.merge_into_dataset(
        data=ibkr_activity,
        partition_cols=["date"],
        key_cols=[
            "id",
            "quantity",
            "transaction_price",
            "closing_price",
            "commission",
        ],
        data_dir="ibkr/completed_orders",
        completed_orders = True,
    )
    
    
def lambda_handler(event, context):
    print("*****************************************")
    print("starting SAM5")
    # return
    main()
    
    # ibkr_get_completed_orders
    
    print("Starting SAM 5 Crawler")
    
    crawler_name = "ibkr_get_completed_orders"
    glue = boto3.client("glue")
    try:
        glue.start_crawler(Name=crawler_name)
    except Exception as e:
        print(f"Error: {e}")
        raise e
    
    print("*****************************************")

if __name__ == "__main__":
    lambda_handler(None, None) 
