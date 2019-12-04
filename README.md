# Description

Simple bot to forward messages from telegram to slack
It can be useful especially if you have not access to telegram client or your company/government blocks telegram servers.

# How it works

Slack using [Incoming Webhooks](https://api.slack.com/messaging/webhooks) .........


# How to start the bot

* download or git clone this repository
* install all requirement modules manually or use ```pip install -r
  requirements.txt```
* --------- run python -m botname 

# Requirements:
 
* [telethon](https://github.com/LonamiWebs/Telethon) for
* [requests](https://requests.kennethreitz.org/en/master/) to send post's to Slack using Incoming Webhooks

# Limitations:

While Slack Incoming Webhooks can be used to send text messages only:
* it's impossible to attach any file to message. All images uploaded to [imgbb.com](https://imgbb.com/) photo hosting and added to message as url
* any other attachment won`t be added to Slack message
* if the original telegram message will be edited or deleted nothing happens with the appropriate slack message

# TODO

* Download all attachments, upload to file hosting and add it to slack message as link
* Change Slack WebHooks with Slack WebAPI to avoid limitations and have a lot new features
 