from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = 123456   #Enter Your 6/7 Digit Telegram API ID.
api_hash = '8cd404221c510840bd37re98b21ac9d20'   #Enter Yor 32 Character API Hash.
phone = '+12345678910'   #Enter Your Mobile Number With Country Code.
client = TelegramClient(phone, api_id, api_hash)
client.connect()
client.send_code_request(phone)
client.sign_in(phone, input('Enter verification code: '))
print(StringSession.save(client.session))