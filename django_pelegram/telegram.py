import logging
from django.conf import settings
import requests
import json


class TelegramApi(object):

    def __init__(self, api_token, use_logging=True):
        self.url = "{0}/bot{1}/".format(settings.API_URL, api_token)
        self.use_logging = use_logging
        if self.use_logging:
            self.logger = logging.getLogger('telegram_api_logs')

    def request(self, method, **kwargs):
        telegram_request = requests.post(self.url + method, **kwargs)
        self.log(telegram_request.text)

    def log(self, data):
        if self.use_logging:
            self.logger.info(data)

    def send_message(self, chat_id, message):
        self.request("sendMessage", data={"chat_id": chat_id, "text": message})

    def send_photo(self, chat_id, file_path):
        files = {'photo': open(file_path, 'rb')}
        self.request("sendPhoto", data={"chat_id": chat_id}, files=files)

    def send_message_inline(self, chat_id, message, callback_query_id=False):
        keyboard = {"inline_keyboard": message['keyboard']}
        self.request("sendMessage",
                     data={"chat_id": chat_id, "text": message['text'], "reply_markup": json.dumps(keyboard)})
        if callback_query_id:
            self.request("answerCallbackQuery",
                         data={"callback_query_id": callback_query_id,
                               "text": "{0} processed".format(message['called_name'])})
