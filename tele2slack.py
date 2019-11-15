import requests

from settings import *
from telethon import TelegramClient, events
from data_processor import *

# Create and start the client so we can make requests
client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start()


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

    if event.message.file and event.message.file.mime_type in ('video/mp4', 'image/jpeg'):
        file_name = await event.message.download_media()
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

# While you can not add gif attachment to slack using webhook this feature is disabled
# def convert_mp4_to_gif(inputfile):
#     """Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie"""
#
#     outputfile = inputfile.split('.')[0] + ".gif"
#     reader = imageio.get_reader(inputfile)
#     fps = reader.get_meta_data()['fps']
#     writer = imageio.get_writer(outputfile, fps=fps)
#     for im in reader:
#         writer.append_data(im)
#     writer.close()
#
#     return outputfile


    # if entities:
    #     for ent in reversed(entities):
    #
    #         # if 'MessageEntityHashtag' in str(ent):
    #         if ent.CONSTRUCTOR_ID == 1868782349:    # 'MessageEntityHashtag' type
    #             pass
    #         # elif 'MessageEntityBold' in str(ent):
    #         elif ent.CONSTRUCTOR_ID == 3177253833:  # 'MessageEntityBold' type
    #             # str = characterinsert(str, ent.length + ent.offset, '*')
    #             # str = characterinsert(str, ent.length, '*')
    #             # print(ent)
    #             pass

