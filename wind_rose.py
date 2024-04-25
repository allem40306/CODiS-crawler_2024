import matplotlib.pyplot as plt
import numpy as np
from windrose import WindroseAxes

import seaborn as sns
from windrose import WindroseAxes, plot_windrose

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt  # 正確匯入 cimgt
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
import cartopy.feature as cfeature # 預定義常量

class Wind_Rose:
    def init(self):
        pass

    # --------------繪製風花圖 --------------
    def wind_rose(self, combined_csv):
        # 轉換為數值
        combined_csv['風向(360degree)'] = pd.to_numeric(combined_csv['風向(360degree)'], errors='coerce')
        combined_csv['風速(m/s)'] = pd.to_numeric(combined_csv['風速(m/s)'], errors='coerce')

        # 移除任何包含 NaN 的行
        combined_csv.dropna(subset=['風向(360degree)', '風速(m/s)'], inplace=True)

        # 轉換為 numpy 陣列
        directions = combined_csv['風向(360degree)'].to_numpy()
        speeds = combined_csv['風速(m/s)'].to_numpy()

        # 繪製風花圖
        ax = WindroseAxes.from_ax()
        ax.bar(directions, speeds, normed=True, opening=0.8, edgecolor='white')

        # 設定標籤和標題
        ax.set_legend()
        ax.set_title("windrose plot")
        max_value = int(combined_csv['風速(m/s)'].max()) + 1
        print(max_value)
        # 修改Y軸以5為間隔
        yticks = np.arange(0, 26, 5) # 設定Y軸間距
        ax.set_yticks(yticks)
        ax.set_yticklabels([f"{i}%" for i in yticks])

        plt.show()

    # --------------繪製風花圖子圖 --------------
    def wind_rose_subplot(self, combined_csv):
        # 假設 combined_csv 是你的 DataFrame
        # 轉換 '日期' 欄位為 datetime 類型並提取月份
        combined_csv['日期'] = pd.to_datetime(combined_csv['日期'])
        combined_csv['month'] = combined_csv['日期'].dt.month

        # 風速和風向資料
        combined_csv['ws'] = combined_csv['風速(m/s)']
        combined_csv['wd'] = combined_csv['風向(360degree)']

        def plot_windrose_subplots(data, *, direction, var, color=None, **kwargs):
            """wrapper function to create subplots per axis"""
            ax = plt.gca()
            ax = WindroseAxes.from_ax(ax=ax)
            plot_windrose(direction_or_df=data[direction], var=data[var], ax=ax, **kwargs)

        # 建立子圖網格
        g = sns.FacetGrid(
            data=combined_csv,
            col="month",  # 使用提取的月份
            col_wrap=3,
            subplot_kws={"projection": "windrose"},
            sharex=False,
            sharey=False,
            despine=False,
            height=3.5,
        )

        # 對映資料到子圖
        g.map_dataframe(
            plot_windrose_subplots,
            direction="wd",
            var="ws",
            normed=True,
            bins=(0.1, 1, 2, 3, 4, 5),
            calm_limit=0.1,
            kind="bar",
        )

        # 子圖調整
        for ax in g.axes:
            ax.set_legend(
                title="$m \cdot s^{-1}$", 
                bbox_to_anchor=(1.1, 1),  # 將圖例放在右上角外側
                loc="upper left"          # 相對於 bbox_to_anchor 指定的點的 'upper left' 位置
            )
            ax.set_rgrids(y_ticks, y_ticks)

        plt.subplots_adjust(wspace=-0.2)
        plt.show()

    # --------------繪製風花圖_地圖 --------------
    def wind_rose_map(self, combined_csv):
        # 假設 combined_csv 是你的 DataFrame
        # 轉換資料類型並移除 NaN
        combined_csv['風向(360degree)'] = pd.to_numeric(combined_csv['風向(360degree)'], errors='coerce')
        combined_csv['風速(m/s)'] = pd.to_numeric(combined_csv['風速(m/s)'], errors='coerce')
        combined_csv.dropna(subset=['風向(360degree)', '風速(m/s)'], inplace=True)

        # 轉換為 numpy 陣列
        directions = combined_csv['風向(360degree)'].to_numpy()
        speeds = combined_csv['風速(m/s)'].to_numpy()
        station_longitude = 120.3957    # 經度
        station_latitude = 22.6056  # 緯度

        # 指定地圖的範圍
        minlon, maxlon, minlat, maxlat = (station_longitude-0.5,station_longitude+0.5, station_latitude-0.5, station_latitude+0.5)

        # 選擇 Stamen 地圖圖源
        stamen_terrain = cimgt.Stamen('terrain-background')

        # 建立地圖
        proj = ccrs.PlateCarree()
        fig = plt.figure(figsize=(10, 8))
        main_ax = fig.add_subplot(1, 1, 1, projection=proj)
        main_ax.set_extent([minlon, maxlon, minlat, maxlat], crs=proj)
        main_ax.coastlines()
        main_ax.add_feature(cfeature.LAND)#新增陸地
        main_ax.add_feature(cfeature.COASTLINE,lw = 0.3)#新增海岸線
        main_ax.add_feature(cfeature.RIVERS,lw = 0.25)#新增河流
        #ax.add_feature(cfeat.RIVERS.with_scale('50m'),lw = 0.25)  # 載入解析度為50的河流
        main_ax.add_feature(cfeature.LAKES)#新增湖泊
        main_ax.add_feature(cfeature.BORDERS, linestyle = '-',lw = 0.25)#不推薦，因為該預設參數會使得我國部分領土丟失
        main_ax.add_feature(cfeature.OCEAN)#新增海洋



        # 在地圖上新增風花圖的位置
        wrax = inset_axes(
            main_ax,
            width=1,  # size in inches
            height=1,  # size in inches
            loc="center",  # center bbox at given position
            bbox_to_anchor=(station_longitude, station_latitude),  # position of the axe
            bbox_transform=main_ax.transData,  # use data coordinate (not axe coordinate)
            axes_class=WindroseAxes,  # specify the class of the axe
        )

        # 繪製風花圖
        wrax.bar(directions, speeds, edgecolor='none', normed=True, opening=0.8, nsector=16, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                blowto=False)

        # 設定風花圖示題
        # wrax.set_title("Wind Rose")

        plt.show()

    def run(self, combined_csv):
        self.wind_rose(combined_csv)
        self.wind_rose_subplot(combined_csv)
        self.wind_rose_map(combined_csv)