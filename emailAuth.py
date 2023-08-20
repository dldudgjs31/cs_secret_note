import smtplib
import string
import random

def generate_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))
def send_email(recipient, subject, message):
    smtp_server = 'smtp.gmail.com'  # 사용하는 메일 서비스에 따라 변경할 수 있습니다.
    smtp_port = 587
    sender_email = 'jsh940517@gmail.com'  # 본인의 이메일 주소로 변경하세요.
    sender_password = 'youdie18'  # 본인의 이메일 비밀번호로 변경하세요.

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, f"Subject: {subject}\n\n{message}")
        server.quit()
        print('이메일 인증 코드를 해당 이메일로 전송하였습니다.')
