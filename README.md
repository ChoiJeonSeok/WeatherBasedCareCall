# WeatherBasedCareCall (날씨 모니터링 및 알림 시스템)

이 프로젝트는 특정 지역의 날씨를 모니터링하고 이상 기후 발생 시 사용자에게 알림을 전송하는 시스템입니다. 
<br>이는 고령의 조부모님과 같이 이상 기후에 민감한 사용자들에게 야외 활동을 자제할 것을 권고하기 위해 개발되었습니다.

## 설치 방법

### 필요한 라이브러리
- Python 버전: 
- 사용된 주요 라이브러리: 

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
3. 이상 기후 발생 시, 이메일을 통해 알림이 전송됩니다.

## 프로젝트 구조
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
│  └─reported
│          (예시: weather_report_전라북도 고창군_20240227_000000.txt)
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

## 에러 핸들링 및 로깅
- 프로젝트 실행 중 발생하는 에러는 로그 파일에 기록됩니다.
- 로그 파일 위치: `./logs` 및 `./email/logs/email_logs`

## 확장 계획
- 이 프로그램은 인간관계 관리에 다방면으로 도움을 주는 것을 최종 목표로 합니다.
- 관련 기능들을 추후 추가할 예정입니다.

## 라이센스
- 이 프로젝트는 MIT 라이센스 하에 공개되며, 누구나 사용, 수정이 가능합니다.