import sys
import ssl
import time
import imaplib

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(from_, to, subject, text, html, smtp_server, username, password):
    try:
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_
        msg['To'] = to

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        conn = SMTP(smtp_server)
        conn.set_debuglevel(False)
        conn.login(username, password)
        try:
            conn.sendmail(from_, to, msg.as_string())
        finally:
            conn.close()

    #except Exception, exc:
    #    sys.exit( "mail failed; %s" % str(exc) ) # give a error message
    except:
        return False

    conn = imaplib.IMAP4(smtp_server, port = 143)
    # Python 3.5
    #context = ssl.create_default_context()
    #conn.starttls(context=context)
    conn.starttls()
    r = conn.login(username, password)
    if r[0] != 'OK':
        return False
    r = conn.select('INBOX.Sent')
    if r[0] != 'OK':
        return False
    r = conn.append('INBOX.Sent', '', imaplib.Time2Internaldate(time.time()), msg.as_string().encode('utf-8'))
    if r[0] != 'OK':
        return False
        
    return True
