from crawler import Crawler
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from table import Table
from wind_rose import Wind_Rose

station_name="淡水 (466900)"
base_download_path = "D:/CODiS-crawler_2024/download"

crawler = Crawler(station_name=station_name, start_date=datetime(2023, 11, 1), end_date=datetime(2023, 11, 30), base_download_path=base_download_path)

with sync_playwright() as playwright:
    crawler.run(playwright)

table = Table(station_name=station_name, base_download_path=base_download_path)
combined_csv = table.run()

wind_Rose = Wind_Rose()
wind_Rose.run(combined_csv)