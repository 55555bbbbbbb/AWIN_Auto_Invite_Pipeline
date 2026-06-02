import utils
import config
import os
from pick import pick
from playwright.sync_api import sync_playwright

def run():
    print("==================================================")
    print("🤖 啟動 [Awin KOL 自動派信機器人]")
    print("==================================================")

    csv_files = utils.get_csv_files()
    if not csv_files:
        print("❌ 找不到任何 CSV 檔案，請先執行抓取。")
        return
        
    selected_csv, _ = pick(csv_files, "📂 請選擇要發送邀請的 CSV 名單:")
    print(f"✅ 已選擇載入：{selected_csv}\n")

    if not os.path.exists(config.MESSAGE_TEMPLATE_FILE):
        print(f"❌ 找不到 {config.MESSAGE_TEMPLATE_FILE}！請先建立並寫入內容。")
        return
    with open(config.MESSAGE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        message_template = f.read()

    kol_list, fieldnames = utils.read_kol_csv(selected_csv)
    if not kol_list:
        print("⚠️ 名單為空。")
        return

    pending_indices = [i for i, k in enumerate(kol_list) if k.get("Status", "") != "Y"]
    if not pending_indices:
        print(f"\n✅ 檔案中的 {len(kol_list)} 位皆已處理完畢！")
        return
        
    print(f"📊 本次將針對剩餘的 {len(pending_indices)} 筆資料進行操作。")
    target_input = input("請輸入這次要「成功發送」的數量 (輸入 0 代表跑到完): ").strip()
    target_limit = int(target_input) if target_input.isdigit() else 0

    utils.launch_debug_chrome()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{config.DEBUG_PORT}")
        page = browser.contexts[0].new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        success_count = 0 
        for current_index in pending_indices:
            utils.check_pause() 
            kol = kol_list[current_index]
            kol_id, kol_name = kol["ID"], kol["Name"]
            
            print(f"\n[進度: {success_count+1}/{len(pending_indices)}] 前往 {kol_name} (ID: {kol_id})...")
            profile_url = f"{config.PROFILE_BASE_URL}{kol_id}"
            
            retry_current = True 
            while retry_current:
                page.goto(profile_url, wait_until="domcontentloaded")
                page.wait_for_timeout(20000)
                utils.check_pause()

                if utils.check_and_login(page): continue
                utils.check_pause()

                message_box = page.locator("textarea[formcontrolname='message']")
                contact_btn = page.locator("button", has_text="Contact partner").first

                if message_box.is_visible(timeout=2000):
                    print("  🟢 判定為【新夥伴】！準備發送邀請...")
                    message_box.click(force=True)
                    message_box.fill(message_template.replace("{name}", kol_name))
                    page.wait_for_timeout(2000)

                    send_btn = page.locator("button", has_text="Send invitation").first
                    if send_btn.is_visible():
                        # send_btn.click() # 實戰時解除註解
                        print("  ✅ [模擬發送成功] 指令已就緒！")
                        success_count += 1 
                        
                        kol_list[current_index]["Status"] = "Y"
                        utils.write_kol_csv(selected_csv, kol_list, fieldnames)
                        retry_current = False
                    else:
                        print("  ⚠️ 找不到發送按鈕，自動重整...")
                        page.reload()
                        page.wait_for_timeout(25000)
                        
                elif contact_btn.is_visible(timeout=1000):
                    print("  ⏭️ 略過：已寄送過邀請。")
                    kol_list[current_index]["Status"] = "Y"
                    utils.write_kol_csv(selected_csv, kol_list, fieldnames)
                    retry_current = False
                else:
                    print("  🚨 異常警告：找不到輸入框與按鈕，自動重整...")
                    page.reload()
                    page.wait_for_timeout(20000)

            if target_limit > 0 and success_count >= target_limit:
                print(f"\n🎯 達到目標 ({target_limit} 位)！提早結束任務。")
                break

        print(f"\n🎉 任務結束！本次成功發送：{success_count} 位。")
        page.close()