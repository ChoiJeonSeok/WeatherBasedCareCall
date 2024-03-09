import json
import weather_api_call
import weather_data_analysis_function as analysis
import logging
import pytz
import pandas as pd
import datetime
import boto3
from io import StringIO

# Boto3 클라이언트 초기화 및 S3 파일 읽기 함수
s3_client = boto3.client('s3')
bucket_name = 'weatherbasedcarecall'

def read_file_from_s3(bucket, key, format):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode(format)

def list_files_in_s3_folder(bucket, prefix, format):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith(format)]


def lambda_handler(event, context):
    try:
        # API 키 파일과 날짜, 시간 설정
        api_key = read_file_from_s3(bucket_name, 'WeatherBasedCareCall/KMA_API_KEY(Decoding).txt', 'utf-8')
        seoul_tz = pytz.timezone('Asia/Seoul')
        current_date = datetime.datetime.now(seoul_tz).strftime('%Y%m%d')
        base_time = '0500'  # 고정 시간

        # WeatherDataFetcher 인스턴스 생성
        fetcher = weather_api_call.WeatherDataFetcher(api_key)

        # 격자 좌표 파일 불러오기
        grid_points_data = read_file_from_s3(bucket_name, 'WeatherBasedCareCall/API_grid_points.csv', 'cp949')
        grid_points_df = pd.read_csv(StringIO(grid_points_data), encoding='cp949')

        
        # 각 격자 좌표에 대해 API 호출
        for index, row in grid_points_df.iterrows():
            nx = row['nx']
            ny = row['ny']
            fetcher.fetch_data_for_location_and_time(current_date, base_time, nx, ny)

        # 'region_grid_data_sigungu.csv' 파일을 불러와서 nx, ny에 해당하는 지역명을 매핑하는 딕셔너리를 생성합니다.
        sigungu_data_path = read_file_from_s3(bucket_name, 'WeatherBasedCareCall/region_grid_data_sigungu.csv', 'cp949')
        sigungu_df = pd.read_csv(StringIO(sigungu_data_path), encoding='cp949')

        # nx, ny를 키로, 지역명을 값으로 하는 딕셔너리를 생성합니다.
        nx_ny_to_region = dict(zip(zip(sigungu_df['nx'], sigungu_df['ny']), sigungu_df['지역명']))

        # 기상 상태와 상태 코드 인덱스 매핑
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
            data_files = list_files_in_s3_folder(bucket_name, 'WeatherBasedCareCall/data/', '.csv')
            processed_data_folder = 'WeatherBasedCareCall/data/processed'  # 처리된 파일을 저장할 폴더

            for file_name in data_files:
                weather_data = read_file_from_s3(bucket_name, file_name, 'utf-8')
                weather_df = pd.read_csv(StringIO(weather_data), encoding='utf-8')

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

                # 보고서 파일 생성 및 S3에 저장
                report_file_name = f'weather_report_{region_name}_{current_date}_{status_code_str}.txt'
                report_folder = 'WeatherBasedCareCall/data/report'  # 보고서를 저장할 폴더
                report_file_key = f'{report_folder}/{report_file_name}'
                s3_client.put_object(Bucket=bucket_name, Key=report_file_key, Body=report.encode('cp949'))
                logging.info(f"Report created for {file_name}")

                # 원본 CSV 파일을 processed 폴더로 이동
                processed_file_key = file_name.replace('data/', 'data/processed/')
                s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_name}, Key=processed_file_key)
                s3_client.delete_object(Bucket=bucket_name, Key=file_name)
                logging.info(f"Moved processed file {file_name} to {processed_data_folder}")

        except Exception as e:
            logging.error(f"Error in processing: {e}")

            return {
            'statusCode': 200,
            'body': json.dumps('Process completed successfully')
        }
    except Exception as e:
        logging.error(f"Error in processing: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error occurred during lambda execution')
        }