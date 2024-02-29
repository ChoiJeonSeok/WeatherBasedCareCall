import pandas as pd
from datetime import datetime, timedelta

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
    # base_date를 문자열로 변환합니다.
    base_date_str = str(base_date)
    base_date = datetime.strptime(base_date_str, '%Y%m%d')
    
    # '내일'과 '모레' 날짜를 datetime 객체로 계산
    tomorrow = (base_date + timedelta(days=1)).strftime('%Y%m%d')
    day_after_tomorrow = (base_date + timedelta(days=2)).strftime('%Y%m%d')

    # 포함할 날짜 리스트 생성
    include_dates = [base_date_str, tomorrow, day_after_tomorrow]

    for date in include_dates:
        # 'fcstDate' 열이 문자열이라면 변환하지 않고, 정수라면 문자열로 변환하여 비교
        daily_df = df[df['fcstDate'].astype(str) == date]
        
        # 해당 날짜의 데이터가 없으면 다음 날짜로 건너뜀
        if daily_df.empty:
            continue
        
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