import requests
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import csv
import os


# API 키를 읽어오는 함수
def read_api_key(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("API key file not found.")
        return None


# API 호출 및 데이터 추출 함수
def fetch_all_weather_data(api_url, params):
    # API 요청
    try:
        res = requests.get(api_url, params=params)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"API 요청 실패: {e}")
        return None

    # XML 파싱
    root = ET.fromstring(res.text)

    # item 태그를 모두 찾음
    item_list = root.findall('body/items/item')

    # 결과를 저장할 딕셔너리 생성
    result_list = []

    # 각 item을 순회하면서 태그와 값을 딕셔너리에 추가
    for item in item_list:
        item_dict = {}
        for elem in item:
            tag = elem.tag  # 태그 이름
            value = elem.text or "Nan"  # 태그 값
            item_dict[tag] = value  # 딕셔너리에 추가
        result_list.append(item_dict)

    return result_list


# API 키 읽기
api_key = read_api_key("KMA_API_KEY(Decoding).txt")
if not api_key:
    print("Failed to read API key. Exiting.")
    exit(1)

# API URL 및 파라미터 설정
api_url = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
params = {
    'serviceKey': api_key,
    'pageNo': 1,
    'numOfRows': 100,
    'dataType': 'XML',
    'dataCd': 'ASOS',
    'dateCd': 'HR',
    'startDt': '20230501',
    'startHh': '00',
    'endDt': '20230503',
    'endHh': '23',
    'stnIds': 108
}

# 결과를 저장할 빈 리스트
result_dicts = []

# 페이지 범위 설정
page_range = 1

# 데이터 수집
for i in range(1, page_range + 1):
    params['pageNo'] = i  # 페이지 번호를 설정합니다.
    result_list = fetch_all_weather_data(api_url, params)  # 데이터를 가져옵니다.
    if result_list:  # 가져온 데이터가 있다면,
        result_dicts.extend(result_list)  # 결과 리스트를 확장합니다.

# DataFrame 생성
df = pd.DataFrame(result_dicts)

# CSV 파일이 이미 존재하는지 확인하여 헤더를 쓸지 결정
write_header = not os.path.exists(csv_file_path)

# CSV 파일로 저장
csv_file_path = 'weather_data.csv'
try:
    # df.to_csv(csv_file_path, index=False, encoding='cp949')
    df.to_csv(csv_file_path, mode='a', header=write_header, index=False, encoding='cp949')
except Exception as e:
    print(f"Error occurred while saving CSV: {e}")

print(f"Data has been saved to {csv_file_path}")