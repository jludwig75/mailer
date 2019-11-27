import logging
import smtplib
import json
import os

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

def _load_mail_settings(settings_file_name):
    with open(settings_file_name, 'r') as f:
        settings = f.read()
    return json.loads(settings)

class Mailer:
    def __init__(self, settings_file_name, sender_name, sender_address):
        mail_settings = _load_mail_settings(settings_file_name)
        self._smtp_account_name = mail_settings['SMTP_ACCOUNT']
        self._smtp_account_password = mail_settings['SMTP_PASSWORD']
        self._smpt_server = mail_settings['SMTP_SERVER']
        self._smpt_port = mail_settings['SMTP_PORT']
        self._sender_name = sender_name
        self._sender_address = sender_address

    def _send_mail(self, to_address, msg):
        logging.info('Sending email from %s to %s' % (self._smtp_account_name, to_address))
        try:
            logging.info('Connecting to SMTP server')
            server = smtplib.SMTP_SSL(self._smpt_server, self._smpt_port)
            server.ehlo()
            logging.info('Logging into SMTP server as %s' % self._smtp_account_name)
            server.login(self._smtp_account_name, self._smtp_account_password)
            logging.info('Sending email to %s' % to_address)
            server.sendmail(self._sender_address, to_address, msg.as_string())    
            logging.info('Closing connection to SMTP server')
            server.close()
            return True
        except Exception as e:
            logging.error('Exception sending email: %s' % str(e))
            return False

    def send_mail(self, to_address, subject, message):
        try:
            msg = MIMEText(message)
            msg['From'] = '"%s" <%s>' % (self._sender_name, self._sender_address)
            msg['To'] = to_address
            msg['Subject'] = subject
            return self._send_mail(to_address, msg)
        except Exception as e:
            logging.error('Exception sending email: %s' % str(e))
            return False

    def send_mail_with_attached_file(self, to_address, subject, message, file_name):
        try:
            msg = MIMEMultipart(message)
            msg['From'] = '"%s" <%s>' % (self._sender_name, self._sender_address)
            msg['To'] = to_address
            msg['Subject'] = subject
            with open(file_name, 'rb') as fd:
                img = MIMEBase('video', 'x-matroska')
                img.set_payload(fd.read())
                encoders.encode_base64(img)
                img.add_header('Content-Disposition', 'attachment', filename=os.path.split(file_name)[-1])
                msg.attach(img)
            return self._send_mail(to_address, msg)
        except Exception as e:
            logging.error('Exception sending email with attachment %s: %s' % (file_name, str(e)))
            return False
