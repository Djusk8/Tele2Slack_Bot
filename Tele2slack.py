import requests
import json
import base64
import os
import re
import imageio
import time
from settings import *
from telethon import TelegramClient, events

# Create and start the client so we can make requests
client = TelegramClient(tele_session, tele_api_id, tele_api_hash).start()


# Listen 'tele_chats'for new messages
@client.on(events.NewMessage(chats=tele_chats))
async def new_message_handler(event):
    """ Handle new telegram messages, format it and send to slack """

    # sender = await event.get_sender()
    # sender = event.get_sender()
    # name = utils.get_display_name(sender)
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


def prepare_json_data(text, media):
    """" Prepare text and media for slack """

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
    """
    Upload provided image to imgbb.com hosting
    :param photo: name of image-file to upload
    :return: url for uploaded image
    """

    with open(photo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    response = requests.post(url=imgbb_api_url, data=({"key": imgbb_api_key, "image": encoded_string}))

    # If photo uploaded successfully, return link to photo
    if response.status_code == 200:
        json_data = response.json()
        photo_url = json_data['data']['display_url']

    # If photo can not be uploaded, wait 10 seconds and try again
    else:
        print(response.status_code, ": Uploading photo error ... waiting 10 sec and try again")
        time.sleep(10)
        photo_url = upload_photo_to_imgbb(photo)

    return photo_url


def convert_mp4_to_jpg(inputfile: str) -> str:
    """
    Extract first frame of the video file and save as jpg image. Image saved in working directory

    :param inputfile: name of mp4 file to extract frame
    :return: name of jpg-image file
    """

    outputfile = inputfile.split('.')[0] + ".jpg"
    reader = imageio.get_reader(inputfile)
    writer = imageio.get_writer(outputfile)

    for im in reader:  # extract the first frame of the video
        writer.append_data(im)
        break

    writer.close()

    return outputfile


def parse_hashtag(m) -> str:
    """ Surround string (hash-tag) by tildes """
    return '`' + m.group() + '`'


def parse_bold(m) -> str:
    """ Interchange '\n' and '*' """
    return m.group().replace("\n*", "*\n")


def parse_links(m):
    """
    Parse string to Slack url format: find 'name' block (surrounded by [square brackets] ) and 'url' block (surrounded
    by parenthesises) and return url-string using template "<url|name>"
    """
    name = re.search(r"\[.*?\]", m.group())     # find the name
    name = name.group()[1:-1]                   # remove the square brackets
    url = re.search(r"\(http.+?\)", m.group())  # find the url
    url = url.group()[1:-1]                     # remove parenthesises
    return "<" + url + "|" + name + ">"


def text_to_slack_format(text: str) -> str:
    """
    Prepare text for posting to slack:
        - #hashtags surrounds by apostrophes ` to highlight it
        - double asterisks (**) replaces with single asteriks (*) to make the text bold
        - double underscores (__) replaces with single underscore (_) to make the text italic
        - double tildes (~~) replaces with single tilde (~) to make the text strike
        - fixes situation when asterisk moved to next string by new line symbol (\n)
        - parse URL
    :param text: raw text
    :return: formatted text
    """

    if text:
        text = re.sub(r'#+\w+', parse_hashtag, text)                # highlight hash-tags
        text = text.replace("**", "*")                              # format telegram bold text to slack bold
        text = re.sub(r'\*.+\n\*', parse_bold, text)                # fix '\n*' situation
        text = text.replace("__", "_")                              # format telegram italic text to slack italic
        text = text.replace("~~", "~")                              # format telegram strike text to slack strike
        text = re.sub(r'\[.*?\]\(http.+?\)', parse_links, text)     # parse links
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

