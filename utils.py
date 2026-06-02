import time
import os
import csv
import subprocess
import keyboard
import config

# 暫停控制機制

is_paused = False

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print("\n⏸️ [系統暫停] 已觸發 F12！程式將在目前動作完成後卡住等待。再次按下 F12 可恢復執行...")
    else:
        print("\n▶️ [系統恢復] 已解除暫停，程式繼續執行！\n")

def check_pause():
    while is_paused:
        time.sleep(1)

def setup_hotkeys():
    keyboard.add_hotkey('F12', toggle_pause)
    print("\n⌨️  F12 暫停功能已啟用！執行過程中隨時按下即可暫停/恢復。")

# 瀏覽器與網站共用邏輯

def launch_debug_chrome():
    command = [
        config.CHROME_PATH,
        f"--remote-debugging-port={config.DEBUG_PORT}",
        f"--user-data-dir={config.USER_DATA_DIR}",
        "--no-first-run"
    ]
    print("🚀 啟動 Chrome 瀏覽器...")
    subprocess.Popen(command)
    time.sleep(5)

def check_and_login(page):
    """檢查是否在登入畫面，若是則執行登入流程。"""
    if "login" in page.url or "id.awin.com" in page.url or page.locator("button", has_text="Continue").is_visible(timeout=3000):
        print("  ⚠️ 偵測到 Session 逾期或登入畫面，啟動自動登入救援！")
        try:
            continue_btn = page.locator("button", has_text="Continue").first
            if continue_btn.is_visible(timeout=5000):
                continue_btn.click(force=True)
                print("  -> 已點擊 Continue，等待 5 秒...")
                page.wait_for_timeout(5000)
            
            signin_btn = page.locator("button", has_text="Sign in").first
            if signin_btn.is_visible(timeout=5000):
                signin_btn.click(force=True)
                print("  -> 已點擊 Sign in，等待 40 秒讓系統完成驗證與載入...")
                page.wait_for_timeout(30000)
            return True
        except Exception as e:
            print(f"  ❌ 自動登入失敗: {e}")
            if not is_paused: toggle_pause()
            return False
    return False

# CSV 檔案共用邏輯 (統一使用 Dict 讀寫)

def get_csv_files():
    return [f for f in os.listdir('.') if f.endswith('.csv')]

def read_kol_csv(filepath):
    """讀取 CSV 並確保每個 Dict 都有 Status 欄位"""
    kols = []
    fieldnames = []
    if not os.path.exists(filepath):
        return kols, fieldnames
        
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for row in reader:
            # 確保有 Status 欄位，沒有就補上空值
            if "Status" not in row:
                row["Status"] = ""
            kols.append(row)
            
    # 如果原始檔案沒有 Status 標題，幫忙加上去
    if "Status" not in fieldnames and fieldnames:
        fieldnames.append("Status")
        
    return kols, fieldnames

def write_kol_csv(filepath, kols, fieldnames):
    """將名單寫回 CSV 檔案"""
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kols)