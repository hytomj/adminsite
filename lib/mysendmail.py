#!/usr/bin/python
#

import re
import os
import time
import smtplib
from email.mime.text import MIMEText

mail_host = 'smtp.exmail.qq.com'
mail_user = ''
mail_pass = ''
mail_postfix = '163.com'

def Time2str(format = "%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime())

def send_mail(to_list,subject,content):
    me = mail_user
    msg = MIMEText(content,_subtype='html', _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception,e:
        print str(e)
        return False
