import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_weather_email(sender_email, password, receiver_emails, location, weather_condition):
    # 이메일 본문 템플릿 불러오기 및 포매팅
    with open('text.txt', 'r') as file:
        text_template = file.read()
    text = text_template.format(location=location, weather_condition=weather_condition)

    with open('html.html', 'r') as file:
        html_template = file.read()
    html = html_template.format(location=location, weather_condition=weather_condition)

    # 이메일 제목 설정
    subject = f"{location}에 {weather_condition} 발생 예정!"

    # 이메일 메시지 생성
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email

    # 이메일 본문을 MIMEText 객체로 변환
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # 메시지에 이메일 본문 추가
    message.attach(part1)
    message.attach(part2)

    # Gmail 서버를 이용해 이메일 보내기
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)  # Gmail 로그인
            for receiver_email in receiver_emails:
                message["To"] = receiver_email
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )  # 이메일 전송
                print(f"{receiver_email}로 이메일 전송 성공")
    except Exception as e:
        print(f"이메일 전송 실패: {e}")

# 사용예시
with open('credentials.txt', 'r') as file:
    sender = file.readline().strip()
    passw = file.readline().strip()

with open('receivers.txt', 'r') as file:
    receivers = file.read().splitlines()

send_weather_email(sender, passw, receivers, "서울", "폭염")