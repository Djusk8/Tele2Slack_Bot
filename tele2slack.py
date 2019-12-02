from settings import *
from telethon import TelegramClient, events
from data_processor import *

# Create and start the client so we can make requests
client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start()

# client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start(bot_token=tele_token)
# client.start(bot_token=tele_token)+7
# client.start()
# await client.connect()
# await client.is_user_authorized()

# Listen Telegram chats for new messages
@client.on(events.NewMessage(chats=tele_chats))
async def new_message_handler(event):
    """ Handle new telegram messages, format it and send to slack """

    # sender = event.get_sender()
    # print(name, 'said\n', event.text, '\n----')
    print(event.text, '\n'+'-'*10)

    if event.text:
        formatted_text = text_to_slack_format(event.text)
    else:
        formatted_text = None

    # if event.message.file and event.message.file.mime_type in ('video/mp4', 'image/jpeg'):
    if event.message.file and event.message.file.mime_type == 'image/jpeg':
        file_name = await event.message.download_media()
        # sender = await event.get_sender()
        # url = ("https://t.me/" + str(sender.username) + "/" + str(event.message.id))
        # response = requests.get(url)
        # print(response)
    else:
        # todo make something with docs: doc, pdf and etc
        file_name = None

    json_data = prepare_json_data(formatted_text, file_name)
    send_data_to_slack(json_data)


def send_data_to_slack(data):
    """ Make POST request to send text message using Slack webhook """
    requests.post(slack_url, data=data)


with client:
    print('(Press Ctrl+C to stop this)\n'+'-'*10)
    client.run_until_disconnected()
