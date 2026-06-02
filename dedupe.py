import utils
from pick import pick

def run():
    print("==================================================")
    print("🤖 啟動 [跨檔案去重複/進度同步工具]")
    print("==================================================")
    
    csv_files = utils.get_csv_files()
    if len(csv_files) < 2:
        print("❌ 資料夾中的 CSV 檔案不足兩個，無法進行跨檔案比較。")
        return

    target_file, _ = pick(csv_files, "🔄 請選擇「要被檢查與更新」的目標檔案:")
    reference_files = [f for f in csv_files if f != target_file]

    print(f"[-] 目標檔案: {target_file}")
    print(f"[-] 參考檔案共 {len(reference_files)} 個，正在掃描歷史紀錄...")

    completed_ids = set()
    for ref_file in reference_files:
        try:
            kols, _ = utils.read_kol_csv(ref_file)
            for kol in kols:
                if kol.get("Status", "").strip().upper() == 'Y':
                    completed_ids.add(kol.get("ID", "").strip())
        except Exception as e:
            print(f"  ⚠️ 讀取參考檔案 {ref_file} 時錯誤: {e}")

    print(f"[-] 掃描完畢，其他檔案中共有 {len(completed_ids)} 筆已完成 (Y) 的 ID。")

    try:
        target_kols, target_fieldnames = utils.read_kol_csv(target_file)
        match_count = 0
        
        for kol in target_kols:
            current_id = kol.get("ID", "").strip()
            current_status = kol.get("Status", "").strip().upper()
            
            if current_id in completed_ids and current_status != 'Y':
                kol["Status"] = "Y"
                match_count += 1
                
        utils.write_kol_csv(target_file, target_kols, target_fieldnames)
        
        print("-" * 30)
        print(f"✅ 處理完成！共將 {match_count} 筆重複的 ID 同步補上了 'Y'。")
        print(f"結果已更新至檔案：{target_file}")

    except Exception as e:
        print(f"❌ 處理目標檔案時發生錯誤：{e}")