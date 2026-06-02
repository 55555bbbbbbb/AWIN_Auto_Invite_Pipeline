import utils
import config
import os
import csv
from playwright.sync_api import sync_playwright

def run():
    print("==================================================")
    print("🤖 啟動 [Awin KOL 自動化收集器]")
    print("==================================================")
    
    target_input = input("請輸入要抓取的數量 (輸入 0 代表全部抓取直到最底): ").strip()
    target_limit = int(target_input) if target_input.isdigit() else 0
    search_keyword = input("請輸入搜尋關鍵字 (預設為 gaming，直接按 Enter 帶入預設): ").strip() or "gaming"

    collected_kols = {}
    csv_filename = f"awin_kol_list_{search_keyword}.csv"

    # 讀取歷史紀錄
    if os.path.exists(csv_filename):
        try:
            kols, _ = utils.read_kol_csv(csv_filename)
            for k in kols:
                collected_kols[k.get("ID")] = k.get("Name")
            print(f"📁 已從檔案載入 {len(collected_kols)} 筆歷史紀錄！將自動略過。")
        except Exception as e:
            print(f"⚠️ 讀取歷史檔案失敗。({e})")

    utils.launch_debug_chrome()

    with sync_playwright() as p:
        print("🔌 連線至 Chrome 中...")
        browser = p.chromium.connect_over_cdp(f"http://localhost:{config.DEBUG_PORT}")
        page = browser.contexts[0].new_page() 
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        print("\n=== 初始化階段 ===")
        page.goto(config.BASE_URL, wait_until="domcontentloaded")
        print("⏳ 初次開啟網站，等待 30 秒...")
        page.wait_for_timeout(30000)

        utils.check_pause()
        utils.check_and_login(page)
        
        # 執行搜尋邏輯
        print(f"🌐 搜尋 '{search_keyword}'...")
        page.goto(config.BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        try: page.locator("#partnerships-toggle").click(timeout=5000)
        except: pass
        page.wait_for_timeout(2000)
        
        search_box = page.locator("input[placeholder*='Search']").first
        search_box.wait_for(state="attached", timeout=10000)
        search_box.click(force=True)
        page.keyboard.type(search_keyword, delay=150)
        page.keyboard.press("Enter")
        print("🎉 搜尋送出完成！等待 40 秒讓結果載入...")
        page.wait_for_timeout(40000)

        print("\n=== 開始收集階段 ===")
        while True:
            utils.check_pause() 
            cards = page.locator("app-publisher-card-item").all()
            
            if len(cards) == 0 or page.get_by_text("Failed to load partners", exact=False).is_visible(timeout=1000):
                print("\n🚨 網頁異常，執行重整 (Reload)...")
                page.reload(wait_until="domcontentloaded")
                page.wait_for_timeout(20000)
                continue 

            cards_to_check = cards[-30:] if len(cards) > 30 else cards
            new_batch = []
            
            for card in cards_to_check:
                try:
                    name = card.locator("span.fw-600").first.inner_text().strip()
                    kol_id = card.locator("span.fw-600 + span").first.inner_text().strip()
                    if kol_id and kol_id not in collected_kols:
                        collected_kols[kol_id] = name
                        new_batch.append({"ID": kol_id, "Name": name, "Status": ""})
                        print(f"  [抓取] 發現新夥伴: {name} (ID: {kol_id})")
                        if target_limit > 0 and len(collected_kols) >= target_limit: break
                except: continue
            
            # 即時備份
            if new_batch:
                file_exists = os.path.exists(csv_filename)
                with open(csv_filename, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Status"])
                    if not file_exists: writer.writeheader()
                    writer.writerows(new_batch)
                print(f"  💾 [即時備份] 累積共 {len(collected_kols)} 筆名單已存檔！")

            if target_limit > 0 and len(collected_kols) >= target_limit:
                print(f"\n🎯 已達目標 ({target_limit} 筆)！")
                break 

            load_more_btn = page.locator("button", has_text="Show 10 more results")
            if load_more_btn.is_visible():
                load_more_btn.click()
                page.wait_for_timeout(8000) 
            else:
                print("\n🛑 已經滑到最底，沒有更多結果了。")
                break 
        page.close()