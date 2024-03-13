import requests
import pandas as pd
import xml.etree.ElementTree as ET
import os
import logging

# 로깅 설정
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_path = os.path.join(log_folder, 'weather_data_fetch.log')
logging.basicConfig(filename=log_file_path, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class WeatherDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        if not self.api_key:
            logging.error("API key reading failed. Exiting.")
            exit(1)
        self.api_url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    @staticmethod
    def read_api_key(file_path):
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            logging.error("API key file not found.")
            return None

    def fetch_all_weather_data(self, params):
        # 요청 URL을 생성합니다.
        request_url = requests.Request('GET', self.api_url, params=params).prepare().url

        try:
            res = requests.get(self.api_url, params=params)
            res.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"API request failed for params {params}: {e}")
            return None
    
        root = ET.fromstring(res.text)
        item_list = root.findall('./body/items/item')
        if not item_list:
            logging.warning(f"No items found in the XML response for params {params}.")
            return None

        result_list = []
        for item in item_list:
            item_dict = {}
            for elem in item:
                tag = elem.tag
                value = elem.text or "Nan"
                item_dict[tag] = value
            result_list.append(item_dict)

        return result_list

    def fetch_data_for_location_and_time(self, base_date, base_time, nx, ny, custom_file_name=None, num_rows=809, page_range=1):
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': num_rows,
            'dataType': 'XML',
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }

        result_dicts = []
        for i in range(1, page_range + 1):
            params['pageNo'] = i
            result_list = self.fetch_all_weather_data(params)
            if result_list:
                result_dicts.extend(result_list)

        df = pd.DataFrame(result_dicts)
        if df.empty:
            logging.warning(f"No data to save for params {params}.")
            return None

        grouped = df.groupby(['baseDate', 'baseTime', 'fcstDate', 'fcstTime', 'nx', 'ny'])
        new_df = pd.DataFrame()

        for name, group in grouped:
            record = {
                'baseDate': name[0],
                'baseTime': name[1],
                'fcstDate': name[2],
                'fcstTime': name[3],
                'nx': name[4],
                'ny': name[5]
            }
            for i, row in group.iterrows():
                category = row['category']
                value = row['fcstValue']
                record[category] = value

            new_df = pd.concat([new_df, pd.DataFrame([record])], ignore_index=True)
        
        data_folder = 'data'
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            
        if custom_file_name:
            csv_file_path = os.path.join(data_folder, custom_file_name)
        else:
            csv_file_name = f'weather_data_{base_date}_{base_time}_{nx}_{ny}.csv'
            csv_file_path = os.path.join(data_folder, csv_file_name)
        new_df.to_csv(csv_file_path, index=False, encoding='cp949')
        logging.info(f"Data has been saved to {csv_file_path}")
        return new_df