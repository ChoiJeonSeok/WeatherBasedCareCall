import requests
import csv
import xml.etree.ElementTree as ET

# API URL 및 파라미터 설정
api_url = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
params = {
    'serviceKey': 'SGD3J7nUrX%2Bod%2B6SN3Fu%2BZB4N9DS13PXL4NV7jwYaFGTFjJSmN4Uk2eIr3ErirViBOIzt2L%2FiYtsg%2BItaPW6YA%3D%3D',
    'pageNo': 1,
    'numOfRows': 10,
    'dataType': 'XML',
    'dataCd': 'ASOS',
    'dateCd': 'HR',
    'startDt': '20220101',
    'startHh': '01',
    'endDt': '20220102',
    'endHh': '01',
    'stnIds': 108
}

# API 호출
response = requests.get(api_url, params=params)
xml_data = response.text

# XML 파싱
root = ET.fromstring(xml_data)

# CSV 파일 쓰기
with open('weather_data.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # 첫 번째 <item> 태그의 모든 하위 태그 이름을 CSV 헤더로 사용
    first_item = root.find('.//item')
    headers = [child.tag for child in first_item]
    csvwriter.writerow(headers)

    # 각 <item> 태그의 하위 태그 값을 CSV에 쓰기
    for item in root.findall('.//item'):
        row_data = [item.find(tag).text if item.find(tag) is not None else '' for tag in headers]
        csvwriter.writerow(row_data)
