import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import boto3


# Boto3 클라이언트 초기화 및 S3 파일 읽기 함수
s3_client = boto3.client('s3')
bucket_name = 'weatherbasedcarecall'

def read_file_from_s3(bucket, key, encoding):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode(encoding)

# 로깅 기본 설정
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# 로그 사용 예시
logger = logging.getLogger()
logger.info("This is an information message")


# 이메일 발신 준비
credentials = read_file_from_s3(bucket_name, 'WeatherBasedCareCall/email/credentials.txt', 'cp949').splitlines()
receivers = read_file_from_s3(bucket_name, 'WeatherBasedCareCall/email/receivers.txt', 'cp949').splitlines()

# 문자열 데이터에서 직접 정보 추출
sender_email = credentials[0].strip()
password = credentials[1].strip()


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

# S3에서 특정 폴더의 파일 목록을 가져오는 함수 정의
def list_files_in_s3_folder(bucket, prefix, format):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith(format)]



def lambda_handler(event, context):
    try:
        report_files = list_files_in_s3_folder(bucket_name, 'WeatherBasedCareCall/data/report/', '.txt')

        for file_name in report_files:
            if file_name.endswith('.txt'):
                location, base_date, code = extract_info_from_filename(file_name)
                if not location or not code:
                    logger.error(f"Failed to extract location and code from file name: {file_name}")
                    continue

                subject = create_subject(location, base_date, code)
                if code != "000000":
                    email_content = read_file_from_s3(bucket_name, file_name, 'cp949')
                    email_content_html = email_content.replace('\n', '<br>')
                    for receiver_email in receivers:
                        message = create_message(sender_email, receiver_email, subject, email_content, email_content_html)
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                            server.login(sender_email, password)
                            server.sendmail(sender_email, receiver_email, message.as_string())
                            logger.info(f"Email sent to {receiver_email}")

        # S3 내 파일 이동 (복사 후 삭제)
        for file_key in report_files:
            destination_key = file_key.replace('data/report/', 'data/reported/')
            s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_key}, Key=destination_key)
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)

        return {
            'statusCode': 200,
            'body': json.dumps('Email processing completed successfully')
        }

    except Exception as e:
        logger.error(f"Error in lambda execution: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error occurred during lambda execution')
        }