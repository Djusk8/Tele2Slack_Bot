import json
import base64
import re
import time
import requests

from settings import imgbb_api_url, imgbb_api_key


def prepare_json_data(text, media_url):
    """" Convert provided data to JSON format """

    json_str = list()
    json_str.append('{"blocks": [')

    # if text is provided add it to JSON
    if text:
        json_str.append('{"type": "section", "text": ')
        json_str.append(json.dumps({"type": "mrkdwn", "text": text, }))
        json_str.append('}, ')

    # if media_url is provided add link to JSON
    if media_url:

        media_url = upload_photo_to_imgbb(media)
        os.remove(media)

        json_str.append('{"type": "image",'
                        f'"image_url": "{media_url}",'
                        '"alt_text": "image"},')

    # add the divider to the end message
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


def parse_links(m):
    """
    Parse string to Slack url format: find 'name' block (surrounded by [square brackets] ) and 'url' block (surrounded
    by parenthesises) and return url-string using template "<url|name>"
    """

    name = re.search(r"\[.*?\n*\]", m.group())     # find the name
    name = name.group()[1:-1]                   # remove the square brackets

    new_line_sym = re.search(r"\n+", name)
    # if where are one or more new line symbols (\n) in the string, save and remove it
    if new_line_sym:
        name = name.replace(new_line_sym.group(), "")

    url = re.search(r"\(http.+?\)", m.group())  # find the url
    url = url.group()[1:-1]                     # remove parenthesises

    return "<" + url + "|" + name + ">" + (new_line_sym.group() if new_line_sym else "")


def parse_bold_lines(m):
    """

    """
    x = re.sub(r"(\n+)", "*\\1*", m.group())    # _______
    x = re.sub(r"\*\*", "", x)                  # remove double asterisks

    return x


def text_to_slack_format(txt: str) -> str:
    """
    Prepare text for posting to slack:
        - double underscores (__) replaces with single underscore (_) to make text italic
        - double tildes (~~) replaces with single tilde (~) to make text strike
        - parse asterisks to make text bold
        - #hashtags surrounds with apostrophes (`) to highlight it
        - parse URL from telegram to slack format
    :param txt: raw text
    :return: formatted text
    """

    if txt:
        txt = txt.replace("__", "_")    # format telegram italic text to slack italic
        txt = txt.replace("~~", "~")    # format telegram strike text to slack strike
        txt = txt.replace("**", "*")    # format telegram bold text to slack bold

        txt = re.sub(r'(?<!`)(#\w+)', '`\\1`', txt)                 # highlight hash-tags
        txt = re.sub(r'\[.*?\n*\]\(http.+?\)', parse_links, txt)    # find and parse links

        txt = re.sub(r'(\*.+)(\n+)\*', '\\1*\\2', txt)                  # fix '\n*' situation

        # for *bold* (surrounded by asterisks)  text if there is no whitespace before/after asterisk add it
        txt = re.sub(r'(\S)(\*.+\*)', '\\1 \\2', txt)
        txt = re.sub(r'(\*.+\*)(\S)', '\\1 \\2', txt)

        txt = re.sub(r'\*[^*]*\*', parse_bold_lines, txt)

    return txt


