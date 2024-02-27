import pandas as pd
from datetime import datetime

# 체감온도 계산 함수
def calculate_heat_index(temp, humidity):
    return temp + (humidity / 10)

# 호우 분석 함수
def analyze_heavy_rain(df):
    # PCP 열의 데이터를 숫자로 변환
    df['PCP_numeric'] = df['PCP'].replace({'1.0mm 미만': 0.5, '30.0~50.0mm': 40, '50.0mm 이상': 60}).apply(pd.to_numeric, errors='coerce')
    # 3시간 및 12시간 강우량 계산
    three_hour_rain = df['PCP_numeric'].rolling(3).sum()
    twelve_hour_rain = df['PCP_numeric'].rolling(12).sum()
    # 호우 조건 확인
    heavy_rain = (three_hour_rain.max() >= 60) or (twelve_hour_rain.max() >= 110)
    return heavy_rain

# 대설 분석 함수
def analyze_heavy_snow(df):
    # SNO 열의 데이터를 숫자로 변환
    df['SNO_numeric'] = df['SNO'].replace({'1.0cm 미만': 0.5, '5.0cm 이상': 5}).apply(pd.to_numeric, errors='coerce')
    # 24시간 적설량 계산
    daily_snow = df['SNO_numeric'].rolling(24).sum()
    # 대설 조건 확인
    heavy_snow = daily_snow.max() >= 5
    return heavy_snow

# 종합 기상 분석 함수
def analyze_weather_conditions(df):
    # 폭염과 강풍 분석
    heat_indexes = df.apply(lambda x: calculate_heat_index(x['TMX'], x['REH']), axis=1)
    heat_wave = heat_indexes.max() >= 33
    strong_wind = df['WSD'].max() > 50.4

    # 호우 분석
    heavy_rain = analyze_heavy_rain(df)

    # 대설 분석
    heavy_snow = analyze_heavy_snow(df)

    # 건조 분석
    dry = df['REH'].min() <= 35

    # 한파 분석
    cold_wave = df['TMN'].min() <= -12

    return heat_wave, strong_wind, heavy_rain, heavy_snow, dry, cold_wave


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