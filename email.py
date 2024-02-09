import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 발신자 정보 불러오기
with open('credentials.txt', 'r') as file:
    sender_email = file.readline().strip()
    password = file.readline().strip()

# 수신자 이메일 주소 불러오기
with open('receivers.txt', 'r') as file:
    receiver_emails = file.read().splitlines()

# 이메일 본문 불러오기
with open('text.txt', 'r') as file:
    text = file.read()

with open('html.html', 'r') as file:
    html = file.read()

# 동적 이메일 제목 설정 (예시)
location = "서울"
weather_condition = "폭염"
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
