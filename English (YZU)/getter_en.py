from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import time
import os


def get_list(progress):
    def update(bar, msg):
        if progress:
            progress(bar, msg)

    # get password
    load_dotenv()
    USER = os.getenv("YZU_ID")
    PASSWORD = os.getenv("YZU_PASS")

    # go to login page
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    update(0, "Opening page ...")
    driver = webdriver.Chrome(options=chrome_options)
    update(3, "Opening page ...")
    driver.get("https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx")

    update(4, "Opening page ...")
    time.sleep(0.2)

    # login
    update(5, "Logging in ...")
    account_input = driver.find_element(By.ID, "Txt_UserID")
    password_input = driver.find_element(By.ID, "Txt_Password")
    account_input.send_keys(USER)  # type: ignore
    password_input.send_keys(PASSWORD)  # type: ignore

    update(6, "Logging in ...")
    time.sleep(0.2)

    update(7, "Loading list ...")
    password_input.send_keys(Keys.ENTER)

    # go to hw page
    for i in range(25):
        time.sleep(0.2)
        update(8 + i, "Loading list ...")

    # get info
    update(33, "Fetching data ...")
    hw_names = [
        h.text.strip() for h in driver.find_elements(By.CSS_SELECTOR, "div.wine-red a")
    ]
    hw_times = [
        t.text.strip()
        for t in driver.find_elements(By.CSS_SELECTOR, "div.wine-red span.LeftDays")
    ]

    driver.quit()
    update(35, "Fetch completed!")

    time.sleep(0.5)

    return hw_names, hw_times
