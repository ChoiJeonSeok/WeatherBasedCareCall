import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

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
    match = re.search(r'weather_report_(.+?)_(\d{2})\.txt', filename)
    if match:
        location = match.group(1)
        code = match.group(2)
        return location, code
    return None, None

def create_subject(location, code):
    condition = ""
    if code == "11":
        condition = "폭염 및 강풍 예보"
    elif code == "10":
        condition = "폭염 예보"
    elif code == "01":
        condition = "강풍 예보"

    return f"{location} 지역 {condition}"

# ../data/report 폴더에서 txt 파일을 읽고 이메일로 보냅니다.
report_folder = '../data/report'
for file_name in os.listdir(report_folder):
    if file_name.endswith('.txt'):
        location, code = extract_info_from_filename(file_name)
        if location and code:
            subject = create_subject(location, code)
            with open(os.path.join(report_folder, file_name), 'r', encoding='cp949') as file:
                email_content = file.read()

            for receiver_email in receivers:
                # HTML 형식으로 이메일 본문을 변환
                email_content_html = email_content.replace('\n', '<br>')

                # MIMEText 객체를 생성할 때 HTML 본문을 사용 (수정된 부분)
                message = create_message(sender_email, receiver_email, subject, email_content, email_content_html)
                
                # 이메일 전송 시도
                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, message.as_string())
                        print(f"{receiver_email}로 이메일 전송 성공")
                        # 별도의 로거를 사용하여 로그 기록 (수정된 부분)
                        email_logger.info(f"Email has been sent to {receiver_email} for file {file_name}")
                except Exception as e:
                    print(f"이메일 전송 실패: {e}")
                    # 별도의 로거를 사용하여 로그 기록 (수정된 부분)
                    email_logger.error(f"Failed to send email to {receiver_email}: {e}")