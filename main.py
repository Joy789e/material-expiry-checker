import webview
import os
import sys
import pandas as pd
from backend import MaterialDateChecker

class Api:
    def check_dates(self, data):
        """檢查日期並返回結果"""
        return MaterialDateChecker.check_dates(data)
    
    def convert_date_code(self, dc_code, format_type):
        """轉換日期代碼格式"""
        return MaterialDateChecker.convert_date_format(dc_code, format_type)

if __name__ == '__main__':
    # 獲取資源路徑
    if getattr(sys, 'frozen', False):
        # 如果是打包後的執行檔
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是直接執行腳本
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # 資源路徑
    assets_path = os.path.join(application_path, 'assets')
    html_path = os.path.join(assets_path, 'index.html')
    
    # 確保icon文件存在於assets目錄
    icon_path = os.path.join(assets_path, 'CAL.ico')
    if not os.path.exists(icon_path):
        # 如果icon不在assets目錄，嘗試在應用根目錄查找
        root_icon_path = os.path.join(application_path, 'CAL.ico')
        if os.path.exists(root_icon_path):
            try:
                # 如果assets目錄不存在，創建它
                if not os.path.exists(assets_path):
                    os.makedirs(assets_path)
                # 複製icon到assets目錄
                import shutil
                shutil.copy2(root_icon_path, icon_path)
            except Exception as e:
                print(f"複製圖標文件時出錯: {e}")
    
    # 創建API實例
    api = Api()
    
    # 創建窗口 (移除了icon參數)
    window = webview.create_window(
        '材料儲存期限檢查系統', 
        html_path,
        js_api=api,
        width=1024,
        height=768,
        min_size=(800, 600)
    )
    
    # 啟動應用
    webview.start(debug=False)  # 設置debug=True以獲取更多錯誤信息