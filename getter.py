from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import time
import os


def get_list(progress):
    def update(msg):
        if progress:
            progress(msg)

    # get password
    load_dotenv()
    USER = os.getenv("YZU_ID")
    PASSWORD = os.getenv("YZU_PASS")

    # go to login page
    update("啟動瀏覽器 ...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    update("開啟登入頁 ...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx")

    time.sleep(0.2)

    # login
    update("登入中 ...")
    account_input = driver.find_element(By.ID, "Txt_UserID")
    password_input = driver.find_element(By.ID, "Txt_Password")
    account_input.send_keys(USER)  # type: ignore
    password_input.send_keys(PASSWORD)  # type: ignore

    time.sleep(0.2)

    password_input.send_keys(Keys.ENTER)
    print("已登入")
    update("等待清單載入 ...")

    time.sleep(4.6)

    # get info
    update("抓取作業資料 ...")
    hw_names = [
        h.text.strip() for h in driver.find_elements(By.CSS_SELECTOR, "div.wine-red a")
    ]
    hw_times = [
        t.text.strip()
        for t in driver.find_elements(By.CSS_SELECTOR, "div.wine-red span.LeftDays")
    ]

    driver.quit()
    print("抓取完成！")
    update("抓取完成！")

    time.sleep(0.5)

    return hw_names, hw_times
