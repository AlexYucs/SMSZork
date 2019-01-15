import smtplib
import email
from bs4 import BeautifulSoup
from imapclient import IMAPClient
import dfrotzWrapper
import time

class Game():
    def __init__(self):
        self.frotz = dfrotzWrapper.Wrapper()

        #dfrotz interpreter
    def process(self, command):
        self.frotz.send('%s\r\n' % command)

    def receive(self):
        return self.frotz.get()


#email send/rec
def sendEmail(recip,msg):
    Mserver = smtplib.SMTP('smtp.gmail.com:587')
    Mserver.starttls()
    Mserver.login(username , password)
    Mserver.sendmail("GmailFrom" , recip , msg)
    Mserver.quit()
def handleEmail(game):
    Locserver = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
    Locserver.login(username, password)
    Locselect_info = Locserver.select_folder('Inbox')
    messages = Locserver.search('UNSEEN')
    for uid, message_data in Locserver.fetch(messages, 'RFC822').items():
        email_message = email.message_from_bytes(message_data[b'RFC822'])
        html = email_message.get_payload(0).get_payload(0).get_payload(0).get_payload()
        soup = BeautifulSoup(html, 'html.parser')
        parsed_message = soup.td.get_text().strip().lower()
        game.process(parsed_message)
        time.sleep(1)
        #print(soup.td.get_text().strip())
        sendEmail(email_message.get('From'),game.receive().strip())
    Locserver.logout()
    return "ok"
def changeState(server):
    server.idle_done()
    return "recieved"

username = 'username'
password = 'pass'

server = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
server.login(username, password)
select_info = server.select_folder('Inbox')

game = Game()
# Start IDLE mode
server.idle()
print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

while True:
    try:
        # Wait for up to 30 seconds for an IDLE response
        responses = server.idle_check(timeout=60)
        print("Server sent:", changeState(server) if responses else "nothing")
        if responses:
            handleEmail(game)
            server.idle()
    except KeyboardInterrupt:
        break

server.idle_done()
print("\nIDLE mode done")
server.logout()
