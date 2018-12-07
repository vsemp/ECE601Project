# coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import logging


class Mailer:
    def __init__(self, receivers):
        self._host = 'smtp.partner.outlook.cn'
        self._port = 587
        self._user = 'noreply.gct_report@cootek.cn'
        self._password = '686d6sDL'
        self._sender = 'noreply.gct_report@cootek.cn'
        self._receivers = receivers

    def get_attach_from_file(self, filepath, attach_filename):
        att = MIMEText(open(filepath, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="%s"' % attach_filename
        return att

    def get_attach_from_str(self, str, attach_filename):
        att = MIMEText(str, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename="%s"' % attach_filename
        return att

    def send_mail(self, subject, text='', attach_list=(), region=None):
        if region:
            subject = '[' + region + '] ' + subject
        mail = self._generate_mail(subject, text, attach_list)
        self._send_mail(mail)

    def _send_mail(self, message):
        for i in range(10):
            # try:
            smtp = smtplib.SMTP()
            smtp.connect(self._host, self._port)
            smtp.starttls()
            smtp.login(self._user, self._password)
            smtp.sendmail(self._sender, self._receivers, message.as_string())
            logging.info(str(datetime.now().strftime('%Y-%m-%d %X')) + " 邮件发送成功")
            break
            # except smtplib.SMTPException:
            #     logging.error(str(datetime.now().strftime('%Y-%m-%d %X')) + " Error: 无法发送邮件")

    def _generate_mail(self, subject, text, attach_list):
        message = MIMEMultipart()
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(text, 'plain', 'utf-8'))
        for attach in attach_list:
            message.attach(attach)
        return message
