import os

# Awin 相關設定
ADVERTISER_ID = "122034"
BASE_URL = f"https://app.awin.com/en/awin/advertiser/{ADVERTISER_ID}/partnerships/overview"
PROFILE_BASE_URL = f"https://app.awin.com/en/awin/advertiser/{ADVERTISER_ID}/partnerships/overview/profile/"

# Chrome 啟動設定
CHROME_PATH_64 = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PATH_32 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
CHROME_PATH = CHROME_PATH_64 if os.path.exists(CHROME_PATH_64) else CHROME_PATH_32
USER_DATA_DIR = r"C:\chrome_dev_profile"
DEBUG_PORT = 9222

# 檔案設定
MESSAGE_TEMPLATE_FILE = "invite_message.txt"