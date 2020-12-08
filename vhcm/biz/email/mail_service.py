# import the smtplib module. It should be included in Python by default
from smtplib import SMTPConnectError, SMTP
import os
# from asgiref.sync import sync_to_async
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from vhcm.common.utils.string import read_template
from vhcm.common.constants import PROJECT_ROOT, RESET_PASSWORD_MAIL_TEMPLATE


def send_reset_password_mail(mail, mail_password,  mail_content):
    # set up the SMTP server
    smtp_connection = None
    try:
        smtp_connection = SMTP(host='smtp.gmail.com', port=587)
        smtp_connection.starttls()
        smtp_connection.login(mail, mail_password)
        smtp_connection.send_message(mail_content)
    except SMTPConnectError as e:
        print(str(e))
    finally:
        if smtp_connection:
            smtp_connection.quit()


def run_send_mail_task(mail_content):
    from vhcm.common.config.config_manager import config_loader, SYSTEM_MAIL, SYSTEM_MAIL_PASSWORD
    mail = config_loader.get_setting_value(SYSTEM_MAIL)
    mail_password = config_loader.get_setting_value(SYSTEM_MAIL_PASSWORD)
    if not (mail and mail_password):
        raise KeyError('System email is not defined')

    p = Process(target=send_reset_password_mail, args=(mail, mail_password, mail_content,))
    p.start()


def create_reset_password_mail_template(send_from, send_to, receipt_name, uid, expire_time):
    message_template = read_template(os.path.join(PROJECT_ROOT, RESET_PASSWORD_MAIL_TEMPLATE))
    msg = MIMEMultipart()  # create a message

    # add in the actual person name to the message template
    message = message_template.substitute(
        PERSON_NAME=receipt_name,
        URL='https://www.vhcm.org/reset-password?uid={}'.format(uid),
        EXPIRE_TIME=expire_time
    )

    # setup the parameters of the message
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = "VirtualHCM - Thiết lập lại mật khẩu tài khoản"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    return msg
