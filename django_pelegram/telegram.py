import logging
from django.conf import settings
import requests
import json


class TelegramApi(object):

    def __init__(self, api_token, use_logging=True):
        self.url = "{0}/bot{1}/".format(settings.TELEGRAM_API_URL, api_token)
        self.use_logging = use_logging
        if self.use_logging:
            self.logger = logging.getLogger('telegram_api_logs')

    def request(self, method, **kwargs):
        telegram_request = requests.post(self.url + method, **kwargs)
        self.log(telegram_request.text)

    def log(self, data):
        if self.use_logging:
            self.logger.info(data)
