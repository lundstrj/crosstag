# -*- encoding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from server_helper_scripts.get_inactive_members import get_inactive_members


def latecomers_mail():
    inactive_users = get_inactive_members()
    sender = "eric.sj11@hotmail.se"
    reciver = "ej222pj@student.lnu.se"
    msg = MIMEMultipart("alternative")
    part1 = ""

    for user in inactive_users:
        temp_msg = user['user'].name + ' \r\n ' + \
                   user['user'].email + ' \r\n Telefon: ' + \
                   user['user'].phone + ' \r\n Adress: ' + \
                   user['user'].address + ' \r\n Taggade senast: ' + \
                   user['event'] + ' \r\n ' + \
                   str(user['days']) + ' dagar sedan senaste taggningen.'

        part1 = temp_msg + "\r\n\r\n" + part1

        # Converts string to UTF-8
        msg.attach(MIMEText(u'' + part1 + '', "plain", "utf-8"))

    msg.as_string().encode('ascii')

    msg['From'] = sender
    msg['To'] = reciver
    msg['Subject'] = "Medlemmar som inte har taggat på 2 veckor!"

    s = smtplib.SMTP("smtp.live.com", 587)
    # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.ehlo()
    # Puts connection to SMTP server in TLS mode
    s.starttls()
    s.ehlo()
    s.login(sender, 'Battle93net11')

    s.sendmail(sender, reciver, msg.as_string())

    s.quit()
