import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import shutil

# 로깅 설정
log_folder = 'logs/email_logs'  # 이메일 전송 로그를 위한 별도의 폴더
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

email_log_file_path = os.path.join(log_folder, 'email_send.log')

# 이메일 전송을 위한 별도의 로거 설정
email_logger = logging.getLogger('emailLogger')
email_logger.setLevel(logging.INFO)

# 파일 핸들러 설정
file_handler = logging.FileHandler(email_log_file_path)
file_handler.setLevel(logging.INFO)

# 로그 포맷터 설정
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 기존 핸들러가 있는지 확인하고, 없으면 추가
if not email_logger.handlers:
    email_logger.addHandler(file_handler)

# 이메일 발신 준비
with open('credentials.txt', 'r') as file:
    sender_email = file.readline().strip()  # 발신자 이메일 주소
    password = file.readline().strip()  # 발신자 이메일 앱 비밀번호

with open('receivers.txt', 'r') as file:
    receivers = file.read().splitlines()  # 수신자 이메일 주소 목록

def load_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8 인코딩으로 파일을 엽니다
            return file.read()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    except UnicodeDecodeError:
        print(f"파일 인코딩 문제: {file_path}")
        return None

def create_message(sender_email, receiver_email, subject, text, html):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    return message

def extract_info_from_filename(filename):
    # 파일 이름에서 지역명, 날짜 및 코드 추출을 위한 정규 표현식 수정
    match = re.search(r'weather_report_(.+?)_(\d{8})_(\d{6})\.txt', filename)
    if match:
        location = match.group(1)
        base_date = match.group(2)
        code = match.group(3)
        return location, base_date, code
    return None, None, None


def create_subject(location, base_date, code):
    conditions = [weather_conditions[i] for i, flag in enumerate(code) if flag == "1"]
    condition_str = ", ".join(conditions) if conditions else "특보 없음"
    return f"{base_date} {location} 지역 {condition_str}"

# 날씨 코드 입력.
weather_conditions = {
    0: "한파",
    1: "건조",
    2: "대설",
    3: "호우",
    4: "강풍",
    5: "폭염",
}

# ../data/report 폴더에서 txt 파일을 읽고 이메일로 보냅니다. 
# 이메일 전송이 성공하면 보고서를 reported 폴더로 이동하여 보존합니다.
report_folder = '../data/report'
reported_folder = '../data/reported'

# 'reported' 폴더가 없으면 생성합니다.
if not os.path.exists(reported_folder):
    os.makedirs(reported_folder)

for file_name in os.listdir(report_folder):
    if file_name.endswith('.txt'):
        location, base_date, code = extract_info_from_filename(file_name)
        if not location or not code:
            email_logger.error(f"Failed to extract location and code from file name: {file_name}")
            continue  # 현재 파일 처리를 건너뛰고 다음 파일로 넘어갑니다

        subject = create_subject(location, base_date, code)
        if code != "000000":
            with open(os.path.join(report_folder, file_name), 'r', encoding='cp949') as file:
                email_content = file.read()

            for receiver_email in receivers:
                # HTML 형식으로 이메일 본문을 변환
                email_content_html = email_content.replace('\n', '<br>')

                # MIMEText 객체를 생성할 때 HTML 본문을 사용
                message = create_message(sender_email, receiver_email, subject, email_content, email_content_html)

                # 이메일 전송 시도
                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, message.as_string())
                        print(f"{receiver_email}로 이메일 전송 성공")
                        # 별도의 로거를 사용하여 로그 기록 
                        email_logger.info(f"Email has been sent to {receiver_email} for file {file_name}")
                except Exception as e:
                    print(f"이메일 전송 실패: {e}")
                    # 별도의 로거를 사용하여 로그 기록
                    email_logger.error(f"Failed to send email to {receiver_email}: {e}")

# 보고서 파일 reported 폴더로 이동
for file_name in os.listdir(report_folder):
    if file_name.endswith('.txt'):
        source_path = os.path.join(report_folder, file_name)
        destination_path = os.path.join(reported_folder, file_name)
        shutil.move(source_path, destination_path)
        print(f"{file_name} 파일이 {reported_folder}로 이동되었습니다.")
        