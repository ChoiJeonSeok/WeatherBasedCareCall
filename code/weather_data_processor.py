import weather_api_call
import weather_data_analysis_function as analysis
import logging

import os
import pandas as pd
import datetime


# API 키 파일과 날짜, 시간 설정
api_key_file = "KMA_API_KEY(Decoding).txt"
base_date = datetime.datetime.now().strftime('%Y%m%d')  # 시스템의 현재 날짜를 YYYYMMDD 형식으로 가져옵니다.
base_time = '0500'  # 고정 시간

# WeatherDataFetcher 인스턴스 생성
fetcher = weather_api_call.WeatherDataFetcher(api_key_file)

# 격자 좌표 파일 불러오기
grid_points_path = 'API_grid_points.csv'  #
grid_points_df = pd.read_csv(grid_points_path, encoding='cp949')

# 각 격자 좌표에 대해 API 호출
for index, row in grid_points_df.iterrows():
    nx = row['nx']
    ny = row['ny']
    fetcher.fetch_data_for_location_and_time(base_date, base_time, nx, ny)

# 'region_grid_data_sigungu.csv' 파일을 불러와서 nx, ny에 해당하는 지역명을 매핑하는 딕셔너리를 생성합니다.
sigungu_data_path = './region_grid_data_sigungu.csv'
sigungu_df = pd.read_csv(sigungu_data_path, encoding='cp949')

# nx, ny를 키로, 지역명을 값으로 하는 딕셔너리를 생성합니다.
nx_ny_to_region = dict(zip(zip(sigungu_df['nx'], sigungu_df['ny']), sigungu_df['지역명']))

try:
    # 데이터 폴더 내의 모든 파일을 순회하며 분석
    data_folder = './data'
    for file_name in os.listdir(data_folder):
        if file_name.endswith('.csv'):
            weather_data_path = os.path.join(data_folder, file_name)
            weather_df = pd.read_csv(weather_data_path, encoding='cp949')

            # nx, ny 좌표 추출
            nx, ny = file_name.split('_')[-2], file_name.split('_')[-1].replace('.csv', '')

            # 추출된 nx, ny 값을 기반으로 지역명을 찾습니다.
            region_name = nx_ny_to_region.get((int(nx), int(ny)), "알 수 없는 지역")

            # 기준 날짜 설정
            base_date = min(weather_df['fcstDate'].unique())

            # 폭염과 강풍 분석
            heat_wave, strong_wind = analysis.analyze_weather_conditions(weather_df)

            # 날짜별 날씨 분석
            daily_weather_report = analysis.analyze_daily_weather(weather_df, base_date)

            # 파일 이름에 상태 표시 추가
            status_code = '00'
            if heat_wave and strong_wind:
                status_code = '11'
            elif heat_wave:
                status_code = '10'
            elif strong_wind:
                status_code = '01'
            
            # 데이터 분석 완료 logging
            logging.info(f"Data analysis completed for {file_name}")

            # 최종 보고서 출력
            report = f"{region_name} 지역의 날씨 분석 보고서:\n"
            report += f"폭염 여부: {'있음' if heat_wave else '없음'}\n"
            report += f"강풍 여부: {'있음' if strong_wind else '없음'}\n\n"
            report += daily_weather_report
            report += "※ 참고사항: 보고서 내용은 기상청 예보 발표 시간 5:00am 이후 수치에 기반하여 작성되었습니다."

            # 보고서 파일 경로 설정
            report_folder = os.path.join(data_folder, "report")
            if not os.path.exists(report_folder):
                os.makedirs(report_folder)  # 폴더가 없으면 생성

            report_file_name = f'weather_report_{region_name}_{status_code}.txt'
            report_file_path = os.path.join(report_folder, report_file_name)

            with open(report_file_path, 'w', encoding='cp949') as report_file:
                report_file.write(report)
            logging.info(f"Report created for {file_name}")

except Exception as e:
    logging.error(f"Error in processing: {e}")