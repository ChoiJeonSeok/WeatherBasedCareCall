import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 환경 변수를 사용하여 발신자 정보 불러오기
sender_email = os.environ.get('SENDER_EMAIL')
password = os.environ.get('EMAIL_PASSWORD')

# 수신자 이메일 주소 불러오기
with open('receivers.txt', 'r') as file:
    receiver_emails = file.read().splitlines()

# 이메일 본문 불러오기
with open('text.txt', 'r') as file:
    text_content = file.read()

with open('html.html', 'r') as file:
    html_content = file.read()

# 동적 이메일 제목 설정 (예시)
location = "서울"
weather_condition = "폭염"
subject = f"{location}에 {weather_condition} 발생 예정!"

# 각 수신자에게 이메일 전송
for receiver_email in receiver_emails:
    # 이메일 메시지 생성
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # 이메일 본문을 MIMEText 객체로 변환
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")

    # 메시지에 이메일 본문 추가
    message.attach(part1)
    message.attach(part2)

    # Gmail 서버를 이용해 이메일 보내기
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)  # Gmail 로그인
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )  # 이메일 전송
            print(f"{receiver_email}로 이메일 전송 성공")
    except Exception as e:
        print(f"{receiver_email}로 이메일 전송 실패: {e}")
