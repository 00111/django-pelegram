from django_pelegram.telegram import TelegramApi
import re
from django.http import JsonResponse


class Request(object):

    def __init__(self, payload):
        self.payload = payload
        if 'message' in self.payload.keys():
            self.data = self.message_request()
        elif 'edited_message' in self.payload.keys():
            self.data = self.edited_message_request()
        elif 'callback_query' in self.payload.keys():
            self.data = self.callback_query_request()

    def callback_query_request(self):
        data = {
            'text': self.payload['callback_query']['data'],
            'chat_id': self.payload['callback_query']['message']['chat']['id'],
            'callback_query_id': self.payload['callback_query']['id'],
            'user': self.payload['callback_query']['from']['id'],
            'type': 'callback_query',
            'testing_request': True if 'testing_request' in self.payload.keys() else False
        }
        return data

    def message_request(self):
        data = {
            'text': self.payload['message']['text'],
            'chat_id': self.payload['message']['chat']['id'],
            'user': self.payload['message']['from']['id'],
            'type': 'message',
            'testing_request': True if 'testing_request' in self.payload.keys() else False
        }
        return data

    def edited_message_request(self):
        data = {
            'text': self.payload['edited_message']['text'],
            'chat_id': self.payload['edited_message']['chat']['id'],
            'user': self.payload['edited_message']['from']['id'],
            'type': 'edited_message',
            'testing_request': True if 'testing_request' in self.payload.keys() else False
        }
        return data


class Response(object):

    def __init__(self):
        self._data = {"method": None, "body": None}

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, params):
        self._data['method'] = params['method']
        self._data['body'] = params['body']


class BotBasic(object):

    def __init__(self, payload=None, bot_token=None):
        self.telegram_api = TelegramApi(bot_token)
        self.request = Request(payload)
        self.response = Response()

    def get_command(self):
        re_command = re.match(r'^/\w+', self.request.data['text'])
        command = ""
        if re_command:
            command = re_command.group().replace('/', '')
        return command

    def send_message(self, message):
        self.telegram_api.send_message(self.request.data['chat_id'], message)

    def send_message_inline(self, message):
        if self.request.data['type'] == 'callback_query':
            self.telegram_api.send_message_inline(self.request.data['chat_id'], message,
                                                  self.request.data['callback_query_id'])
        else:
            self.telegram_api.send_message_inline(self.request.data['chat_id'], message)

    def send_photo(self, file_path):
        self.telegram_api.send_photo(self.request.data['chat_id'], file_path)

    def dont_understand_message(self):
        return "Bot don't understand your command ¯\_(ツ)_/"

    def json_response(self, data={}, status=200):
        return JsonResponse(data, status=status)

    def exception_occurred(self, err):
        self.send_message("Run-time error:{0}".format(err))

