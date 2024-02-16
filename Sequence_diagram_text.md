# Weather Based Care Call 시퀀스 다이어그램 

1. **시작 (Initialization)**
   - Actor: 사용자 (User)
   - System Component: 스케줄러 (Scheduler)
   - Action: 스케줄러가 주기적인 작업을 초기화한다.

2. **기상청 API 호출**
   - System Component: 데이터 수집 모듈 (Data Collection Module)
   - External System: 기상청 API (KMA API)
   - Action: 데이터 수집 모듈이 기상청 API에 요청을 보낸다.

3. **데이터 수신 및 저장**
   - External System: 기상청 API (KMA API)
   - System Component: 데이터 수집 모듈 (Data Collection Module)
   - System Component: 데이터베이스 (Database)
   - Action: 데이터 수집 모듈이 기상청 API로부터 데이터를 수신하고, 이를 데이터베이스에 저장한다.

4. **데이터 전처리 및 분석**
   - System Component: 분석 엔진 (Analysis Engine)
   - System Component: 데이터베이스 (Database)
   - Action: 분석 엔진이 데이터베이스로부터 데이터를 읽어들이고, 전처리 및 분석 과정을 수행한다.

5. **이상 기후 감지 및 사용자 대상 결정**
   - System Component: 분석 엔진 (Analysis Engine)
   - System Component: 사용자 관리 모듈 (User Management Module)
   - Action: 분석 엔진이 이상 기후를 감지하고, 사용자 관리 모듈을 통해 해당 이상 기후에 관심 있는 사용자를 식별한다.

6. **이메일 보고서 생성 및 전송**
   - System Component: 이메일 서비스 (Email Service)
   - Actor: 사용자 (User)
   - Action: 이메일 서비스가 이상 기후 보고서를 생성하고, 이를 관심 있는 사용자에게 이메일로 전송한다.

7. **오류 처리 및 로깅**
   - System Component: 모든 모듈 (All Modules)
   - System Component: 로깅 시스템 (Logging System)
   - Action: 각 모듈에서 발생하는 오류를 로깅 시스템을 통해 기록하고 처리한다.