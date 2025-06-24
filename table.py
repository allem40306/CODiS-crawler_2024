#----------------------資料整理----------------------
import pandas as pd
import os
import glob
from prettytable import PrettyTable


class Table:
    def __init__(self, station_name, base_download_path, month):     
        # 定義站名
        self.station_name = station_name
        self.station_code = self.station_name.split()[-1].strip("()")  # 提取站號
        
        # 建立下載路徑
        self.station_download_path = os.path.join(base_download_path, self.station_code)
        self.month = month

    def print_df_as_table(self, df, max_rows=5):
        """
        Print the first five rows of a Pandas DataFrame as a PrettyTable.

        Parameters:
        df (pandas.DataFrame): The DataFrame to print.
        """
        table = PrettyTable()
        table.field_names = df.columns.tolist()

        for row in df.head(max_rows).itertuples(index=False):
            table.add_row(row)

        print(table)

    def run(self):
        #匯入 station_download_path 資料夾下所有csv檔案，並將檔名作為一個新的欄位
        extension = 'csv'
        all_filenames = [i for i in glob.glob(f"{self.station_download_path}/*{self.month}*.{extension}")]

        # 讀取所有檔案，跳過第二行，並新增檔名作為新列
        combined_csv = pd.concat([pd.read_csv(f, skiprows=[1]).assign(檔名=os.path.basename(f)) for f in all_filenames])

        #提取檔名中的日期新增到新的欄位
        combined_csv['日期'] = combined_csv['檔名'].str.extract('(\d{4}-\d{2}-\d{2})')

        #刪除檔名欄位
        combined_csv = combined_csv.drop(['檔名'], axis=1)
        self.print_df_as_table(combined_csv)
        combined_csv.to_csv(f"download/{self.station_code}.csv", index=False, encoding='utf-8-sig')

        self.print_df_as_table(combined_csv,10)

        return combined_csv
