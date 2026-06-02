import sys
import utils
from pick import pick

# 匯入三個功能模組
import grab
import send
import dedupe

def main():
    # 初始化全域快捷鍵
    utils.setup_hotkeys()
    
    while True:
        title = """
==================================================
 Awin KOL 自動化工具
==================================================
請使用 [上下方向鍵] 選擇功能，按 [Enter] 進入:
        """
        options = [
            "1. 📥 收集抓取名單 (Grab)",
            "2. ✉️ 自動發送邀請 (Send)",
            "3. 🔄 跨檔案進度同步 (Dedupe)",
            "4. ❌ 離開程式 (Exit)"
        ]
        
        selected_option, index = pick(options, title)
        
        # 根據使用者的選擇執行對應的模組
        if index == 0:
            grab.run()
        elif index == 1:
            send.run()
        elif index == 2:
            dedupe.run()
        elif index == 3:
            print("\n👋 感謝使用，程式已關閉。")
            sys.exit()
            
        input("\n[ 按 Enter 鍵返回主選單 ]")

if __name__ == "__main__":
        
    main()