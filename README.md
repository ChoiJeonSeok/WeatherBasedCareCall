# WeatherBasedCareCall (날씨 모니터링 및 알림 시스템)

이 프로젝트는 특정 지역의 날씨를 모니터링하고 이상 기후 발생 시 사용자에게 알림을 전송하는 시스템입니다. 
<br>이는 고령의 조부모님과 같이 이상 기후에 민감한 사용자들에게 야외 활동을 자제할 것을 권고하기 위해 개발되었습니다.

## 설치 방법

### 필요한 라이브러리
-  Python 버전에 종속된 기능은 없습니다. 다만, 프로그램 개발이 Python 3.6 버전을 사용하여 진행되었다는 것을 참고하여 주시기 바랍니다.
- 필요한 라이브러리는 `requirements.txt`를 통해 설치할 수 있습니다. 
- 설치 방법: `pip install -r requirements.txt`


### 환경 설정
1. **기상청 API 인증키**:
   - 공공데이터 포털에서 기상청 단기예보 조회서비스 신청 후 받은 API 인증키를 `KMA_API_KEY(Decoding).txt` 파일에 저장합니다.
   - 파일 위치: `./` (weather_data_processor.py와 같은 디렉토리)

2. **이메일 설정**:
   - `credentials.txt` 파일에 첫 줄에는 발신자 Gmail 주소, 둘째 줄에는 해당 Gmail 계정의 애플리케이션 비밀번호를 입력합니다.
   - `receivers.txt` 파일에는 수신자의 이메일 주소를 입력합니다.
   - 파일 위치: `./email`

### 사용 방법
1. `API_grid_points.csv`에 기상 예보를 받고자 하는 지역의 `nx` 및 `ny` 좌표를 입력합니다.
2. 입력된 지역에 대한 기상 예보 데이터를 불러와 `data` 폴더에 CSV 파일로 저장합니다.
3. `weather_data_processor.py` 파일을 실행하여 데이터를 처리하고, `send_email.py`를 실행하여 이메일 알림을 보냅니다.
   ```bat
   @echo off
   cd C:\WORKSPACE-PYTHON\weather_test
   python weather_data_processor.py
   timeout /T 5 /nobreak
   cd C:\WORKSPACE-PYTHON\weather_test\email
   python send_email.py
   pause
   ```

4. 이상 기후 발생 시, 이메일을 통해 알림이 전송됩니다.

## 프로젝트 구조

### 파일 및 폴더 구조
- `API_grid_points.csv`: 기상 예보를 받고자 하는 지역의 `nx` 및 `ny` 좌표를 입력하는 파일입니다.
- `data`: 기상 예보 데이터가 CSV 파일로 저장되는 폴더입니다.
  - 보고서 파일은 `report` 폴더에 우선 저장된 후 이메일을 보낸 뒤 `reported` 폴더로 이동하게 됩니다.
  - `csv` 파일들은 우선 `data` 폴더에 저장된 후 데이터 분석이 완료되면 `processed` 폴더로 이동하게 됩니다.
- `weather_data_processor.py`: 기상 데이터를 처리하는 메인 스크립트입니다.
- `email/send_email.py`: 이상 기후 발생 시 알림을 이메일로 전송하는 스크립트입니다.


### 구조도
```
C:.
│  API_grid_points.csv
│  KMA_API_KEY(Decoding).txt
│  region_grid_data_sigungu.csv
│  weather_api_call.py
│  weather_data_analysis_function.py
│  weather_data_processor.py
│
├─data
│  │  (예시: weather_data_20240227_0500_56_80.csv)
│  ├─report
│  ├─reported
│  │       (예시: weather_report_전라북도 고창군_20240227_000000.txt)
│  └─processed
│
├─email
│  │  credentials.txt
│  │  receivers.txt
│  │  send_email.py
│  └─logs
│      └─email_logs
│              email_send.log
│
└─logs
        weather_data_fetch.log
```

### 시퀀스 다이어그램
![KMA 기상데이터 이상기후 이메일서비스 시퀀스다이어그램](https://github.com/ChoiJeonSeok/WeatherBasedCareCall/assets/82266289/f9d05c6b-b7d9-4227-9ee1-e8211a9df664)



## 에러 핸들링 및 로깅
- 프로젝트 실행 중 발생하는 에러는 로그 파일에 기록됩니다.
- 로그 파일 위치: `./logs` 및 `./email/logs/email_logs`

## 확장 계획
- 이 프로그램은 인간관계 관리에 다방면으로 도움을 주는 것을 최종 목표로 합니다.
- 관련 기능들을 추후 추가할 예정입니다.

## 라이센스
- 이 프로젝트는 MIT 라이센스 하에 공개되며, 누구나 사용, 수정이 가능합니다.

## 부록

### 결과 예시
- 이상 기후 발견 시 전송되는 메일 예시
- 
![image](https://github.com/ChoiJeonSeok/WeatherBasedCareCall/assets/82266289/99c39727-dba2-4690-9f31-4a64fae39a6a)