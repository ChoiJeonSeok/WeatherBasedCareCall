import pandas as pd
from datetime import datetime

# 체감온도 계산 함수
def calculate_heat_index(temp, humidity):
    return temp + (humidity / 10)

# 폭염과 강풍 분석 함수
def analyze_weather_conditions(df):
    heat_indexes = df.apply(lambda x: calculate_heat_index(x['TMX'], x['REH']), axis=1)
    heat_wave = heat_indexes.max() >= 33
    strong_wind = df['WSD'].max() > 50.4
    return heat_wave, strong_wind

# 날짜별 분석 함수
def analyze_daily_weather(df, base_date):
    daily_report = ""
    for date in sorted(df['fcstDate'].unique()):
        if date > base_date + 2:
            continue
        daily_df = df[df['fcstDate'] == date]
        max_temp = daily_df['TMX'].max()
        min_temp = daily_df['TMN'].min() if not pd.isna(daily_df['TMN'].min()) else daily_df['TMP'].min()
        max_precipitation = daily_df['PCP'].max()
        max_snowfall = daily_df['SNO'].max()

        daily_report += f"날짜: {date}\n"
        daily_report += f"최고 기온: {max_temp}°C\n"
        daily_report += f"최저 기온: {min_temp}°C\n"
        daily_report += f"최대 강수량: {max_precipitation}\n"
        daily_report += f"최대 적설량: {max_snowfall}\n\n"
    return daily_report