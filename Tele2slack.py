import requests
import json
import base64
import os
import imageio
from settings import *
from telethon import TelegramClient, events


# Create and start the client so we can make requests (we don't here)
client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start()


@client.on(events.NewMessage(chats=tele_chats))
async def normal_handler(event):

    # sender = await event.get_sender()
    # sender = event.get_sender()
    # name = utils.get_display_name(sender)
    # print(name, 'said\n', event.text, '\n----')
    print(event.text, '\n'+'-'*10)

    formatted_text = None
    if event.text:
        formatted_text = format_telegram_text_entities_to_slack(event.text, event.message.entities)

    media_name = await event.message.download_media()

    json_data = prepare_json_data(formatted_text, media_name)
    send_data_to_slack(json_data)


def send_data_to_slack(data):
    # Function that send data in a string to your slack channel using incoming webhook
    requests.post(slack_url, data=data)


def prepare_json_data(text, media):
    # Prepare text and media to

    json_str = list()
    json_str.append('{"blocks": [')

    if text:

        json_str.append('{"type": "section", "text": ')
        json_str.append(json.dumps({"type": "mrkdwn", "text": text, }))
        json_str.append('}, ')

    if media:

        if ".mp4" in media:
            old_name = media
            # media = convert_mp4_to_gif(media)
            media = convert_mp4_to_jpg(media)
            os.remove(old_name)

        media_url = upload_photo_to_imgbb(media)
        os.remove(media)

        json_str.append('{"type": "image",'
                        f'"image_url": "{media_url}",'
                        '"alt_text": "image"},')

    json_str.append('{"type": "divider"}]}')

    return "".join(json_str)


def upload_photo_to_imgbb(photo: str) -> str:

    with open(photo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    response = requests.post(url=imgbb_api_url, data=({"key": imgbb_api_key, "image": encoded_string}))

    if response.status_code == 200:
        json_data = response.json()
        photo_url = json_data['data']['display_url']
    else:
        print(response.status_code)
        input()

    return photo_url


def convert_mp4_to_gif(inputfile):
    """Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie"""

    outputfile = inputfile.split('.')[0] + ".gif"
    reader = imageio.get_reader(inputfile)
    fps = reader.get_meta_data()['fps']
    writer = imageio.get_writer(outputfile, fps=fps)
    for im in reader:
        writer.append_data(im)
    writer.close()

    return outputfile


def convert_mp4_to_jpg(inputfile):
    """Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie"""

    outputfile = inputfile.split('.')[0] + ".jpg"
    reader = imageio.get_reader(inputfile)
    writer = imageio.get_writer(outputfile)

    for im in reader:  # extract the first frame of the video
        writer.append_data(im)
        break

    writer.close()

    return outputfile


def format_telegram_text_entities_to_slack(text: str, entities: list) -> str:

    if text:
        text = text.replace("**", "*")

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

    return text


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

