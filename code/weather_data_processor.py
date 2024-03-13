import weather_api_call
import weather_data_analysis_function as analysis
import logging
import shutil

import os
import pandas as pd
import datetime


# API 키 파일과 날짜, 시간 설정
api_key = weather_api_call.WeatherDataFetcher.read_api_key("KMA_API_KEY(Decoding).txt")
current_date = datetime.datetime.now().strftime('%Y%m%d')  # 시스템의 현재 날짜를 YYYYMMDD 형식으로 가져옵니다.
base_time = '0500'  # 고정 시간

# WeatherDataFetcher 인스턴스 생성
fetcher = weather_api_call.WeatherDataFetcher(api_key)

# 격자 좌표 파일 불러오기
grid_points_path = 'API_grid_points.csv'  #
grid_points_df = pd.read_csv(grid_points_path, encoding='cp949')

# 각 격자 좌표에 대해 API 호출
for index, row in grid_points_df.iterrows():
    nx = row['nx']
    ny = row['ny']
    fetcher.fetch_data_for_location_and_time(current_date, base_time, nx, ny)

# 'region_grid_data_sigungu.csv' 파일을 불러와서 nx, ny에 해당하는 지역명을 매핑하는 딕셔너리를 생성합니다.
sigungu_data_path = './region_grid_data_sigungu.csv'
sigungu_df = pd.read_csv(sigungu_data_path, encoding='cp949')

# nx, ny를 키로, 지역명을 값으로 하는 딕셔너리를 생성합니다.
nx_ny_to_region = dict(zip(zip(sigungu_df['nx'], sigungu_df['ny']), sigungu_df['지역명']))

# 기상 상태와 상태 코드 인덱스 순서 안내
# 000000 코드의 순서. 001100 이면 폭설과 호우.
weather_status_indices = {
    'cold_wave': 0,
    'dry': 1,
    'heavy_snow': 2,
    'heavy_rain': 3,
    'strong_wind': 4,
    'heat_wave': 5,
}

try:
    # 데이터 폴더 내의 모든 파일을 순회하며 분석
    data_folder = './data'
    processed_data_folder = './data/processed'  # 처리된 파일을 저장할 폴더

    if not os.path.exists(processed_data_folder):
        os.makedirs(processed_data_folder)  # 폴더가 없으면 생성

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

            # 날짜별 날씨 분석
            daily_weather_report = analysis.analyze_daily_weather(weather_df, base_date)

            # 기상 조건 분석
            heat_wave, strong_wind, heavy_rain, heavy_snow, dry, cold_wave = analysis.analyze_weather_conditions(weather_df)

            # 상태 코드 생성
            status_code = ["0"] * 6  # 6자리 상태 코드 초기화
            weather_conditions_results = [cold_wave, dry, heavy_snow, heavy_rain, strong_wind, heat_wave]

            for index, condition in enumerate(weather_conditions_results):
                if condition:
                    status_code[index] = "1"  # 상태 코드 설정

            status_code_str = "".join(status_code)  # 상태 코드 문자열로 변환

            # 데이터 분석 완료 logging
            logging.info(f"Data analysis completed for {file_name}")

            # 최종 보고서 출력
            report = f"{region_name} 지역의 날씨 분석 보고서:\n"
            report += f"폭염 여부: {'있음' if heat_wave else '없음'}\n"
            report += f"강풍 여부: {'있음' if strong_wind  else '없음'}\n"
            report += f"호우 여부: {'있음' if heavy_rain else '없음'}\n"
            report += f"대설 여부: {'있음' if heavy_snow else '없음'}\n"
            report += f"건조 여부: {'있음' if dry else '없음'}\n"
            report += f"한파 여부: {'있음' if cold_wave else '없음'}\n\n"
            report += daily_weather_report
            report += "※ 참고사항: 보고서 내용은 기상청 예보 발표 시간 5:00am 이후 수치에 기반하여 작성되었습니다."

            # 보고서 파일 경로 설정
            report_folder = os.path.join(data_folder, "report")
            if not os.path.exists(report_folder):
                os.makedirs(report_folder)  # 폴더가 없으면 생성

            report_file_name = f'weather_report_{region_name}_{current_date}_{status_code_str}.txt'
            report_file_path = os.path.join(report_folder, report_file_name)

            with open(report_file_path, 'w', encoding='cp949') as report_file:
                report_file.write(report)
            logging.info(f"Report created for {file_name}")

            # 분석이 완료된 CSV 파일을 처리된 데이터 폴더로 이동
            shutil.move(os.path.join(data_folder, file_name),
                        os.path.join(processed_data_folder, file_name))
            logging.info(f"Moved processed file {file_name} to {processed_data_folder}")

except Exception as e:
    logging.error(f"Error in processing: {e}")