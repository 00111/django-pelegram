import logging
from django.conf import settings
import requests

class TelegramApi(object):

    def __init__(self, api_token, use_logging=True):
        self.url = "{0}/bot{1}/".format(settings.API_URL, api_token)
        self.use_logging = use_logging
        if self.use_logging:
            self.logger = logging.getLogger('telegram_api_logs')

    def send_message(self, chat_id, message):
        telegram_request = requests.post(self.url + "sendMessage", data={"chat_id": chat_id, "text": message})
        if self.use_logging:
            self.logger.info(telegram_request.text)
