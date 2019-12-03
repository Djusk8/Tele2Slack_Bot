import os
from settings import *
from telethon import TelegramClient, events
from data_processor import *

# Create and start the client so we can listen for new messages
client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start()


@client.on(events.NewMessage(chats=tele_chats))
async def new_message_handler(event):
    """ Handle new telegram messages, format it and send to slack """

    print(event.text, '\n'+'-' * 10)

    # if telegram message has text convert it to slack format
    if event.text:
        formatted_text = text_to_slack_format(event.text)
    else:
        formatted_text = None

    # if telegram message has attached picture, download it and upload to imgbb
    if event.message.file and event.message.file.mime_type == 'image/jpeg':
        file_name = await event.message.download_media()
        media_url = upload_photo_to_imgbb(file_name)
        os.remove(file_name)
    else:
        # todo make something with docs: doc, pdf and etc
        media_url = None

    if event.text or media_url:
        json_data = prepare_json_data(formatted_text, media_url)
        send_data_to_slack(json_data)


def send_data_to_slack(data):
    """ Make POST request to send text message using Slack webhook """
    requests.post(slack_url, data=data)


if __name__ == "__main__":
    with client:
        print('(T2S-bot started ... Press Ctrl+C to stop this)\n' + '-'*50)
        client.run_until_disconnected()
