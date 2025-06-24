#python -m playwright codegen --target python -o test.py -b chromium https://codis.cwa.gov.tw/StationData

# from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
import os
from tqdm import tqdm

class TqdmWrapper(tqdm):
    """提供了一個 `total_time` 格式參數"""
    
    @property
    def format_dict(self):
        # 取得父類別的format_dict
        d = super().format_dict
        
        # 計算總共花費的時間
        total_time = d["elapsed"] * (d["total"] or 0) / max(d["n"], 1)
        
        # 更新字典以包含總共花費的時間
        d.update(total_time='總計: ' + self.format_interval(total_time))

        # 返回更新後的字典
        return d

class Crawler:
    def __init__(self, station_name, start_date, end_date, base_download_path):                
        # 定義站名
        self.station_name = station_name
        self.station_code = self.station_name.split()[-1].strip("()")  # 提取站號

        # 定義日期區間
        self.start_date = start_date
        self.end_date = end_date

        # 建立下載路徑
        self.station_download_path = os.path.join(base_download_path, self.station_code)

        # 如果資料夾不存在，則建立它
        if not os.path.exists(self.station_download_path):
            os.makedirs(self.station_download_path)

        # 在下載時使用 station_download_path 作為儲存路徑
        self.download_path = self.station_download_path

        # 計算日期間隔天數
        self.days_diff = (self.end_date - self.start_date).days

        # 生成等長的數字序列
        self.number_list = list(range(self.days_diff + 1))

    def run(self, playwright):
        browser = playwright.chromium.launch(headless=True)  # 不跳出瀏覽器
        print('browser open')
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto("https://codis.cwa.gov.tw/StationData")
        page.wait_for_load_state("load")
        page.get_by_label("自動雨量站").check()
        page.get_by_label("自動氣象站").check()
        page.get_by_label("農業站").check()
        page.get_by_role("button", name="顯示", exact=True).click()
        page.locator("li").filter(has_text="站名站號").get_by_role("combobox").click()
        page.locator("li").filter(has_text="站名站號").get_by_role("combobox").fill(self.station_code)
        page.locator(".leaflet-marker-icon > .icon_container > .marker_bgcolor > .bg_triangle").first.click()
        page.get_by_role("button", name="資料圖表展示").click()
        
        # 獲取當前日期
        current_date = datetime.now()

        # 獲取前一天的日期
        previous_date = current_date - timedelta(days=1)

        # 格式化日期
        year = previous_date.strftime("%Y")
        month = previous_date.strftime("%m月")
        day = previous_date.strftime("%d")

        # 選擇年份
        if previous_date.year != self.end_date.year:
            page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
            time.sleep(1)
            page.get_by_text(str(previous_date.year), exact=True).click()  # 選擇當前年份
            time.sleep(1)
            page.query_selector(f".vdatetime-year-picker__item:has-text('{str(self.end_date.year)}')").click()  # 選擇目標年份
            page.get_by_text("Continue").click()
            print('year select ok')
            time.sleep(1)
        # 選擇月份
        if previous_date.month != self.end_date.month:
            page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
            print('month select start')
            page.get_by_text(f"月{previous_date.day}日").click()
            print('month select ')
            print(f"{previous_date.month}月")
            time.sleep(1)
            print('end_date select ')
            print(f"{self.end_date.month}月")
            page.query_selector(f".vdatetime-month-picker__item:has-text('{self.end_date.month}月')").click() 
            print('month select ok')
            time.sleep(1)
            page.get_by_text("Continue").click()
            time.sleep(1)
        # 選擇日期
        if previous_date.day != self.end_date.day:
            print("end_date.day select:")
            print(self.end_date.day)
            page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label").click()
            page.query_selector(f".vdatetime-calendar__month__day:has-text('{str(self.end_date.day)}')").click()
            print('date select ok')
    
        # 處理下載
        
        for i in TqdmWrapper(self.number_list, desc=f"{' '*10}下載進度",ncols=200, unit='file', unit_scale=True):
            # 根據結束時間往前推算當前日期
            current_date = self.end_date - timedelta(days=i)

            # 構建預期的檔名（格式為：站號-年-月-日.csv）
            expected_filename = f"{self.station_code}-{current_date.year}-{current_date.month:02d}-{current_date.day:02d}.csv"
            expected_filepath = os.path.join(self.download_path, expected_filename)

            # 檢查檔案是否存在
            if os.path.exists(expected_filepath):
                print(f"\r檔案 {expected_filename} 已存在，跳過下載。", end=" ")
                page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label > .datetime-tool > div").first.click()
                #time.sleep(0.5)
                continue

            # 如果檔案不存在，執行下載操作
            with page.expect_download() as download_info:
                page.locator(".lightbox-tool-type-ctrl-btn-group > div").first.click()
                download = download_info.value
                download.save_as(self.download_path+"/" +  download.suggested_filename)  # 儲存檔案
                #print(download.url)  # 獲取下載的url地址
                # 這一步只是下載下來，生成一個隨機uuid值儲存，程式碼執行完會自動清除
                print("\r"+"檔案不存在，以下載 : "+download.suggested_filename,end=" ")  # 獲取下載的檔名
                time.sleep(1)
                page.locator("div:nth-child(5) > .lightbox-tool-type-ctrl > .lightbox-tool-type-ctrl-form > label > .datetime-tool > div").first.click()
                time.sleep(2)
            
        context.close()
        browser.close()
