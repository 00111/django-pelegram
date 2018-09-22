from pelegram.telegram import TelegramApi
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
            'type': 'callback_query'
        }
        return data

    def message_request(self):
        data = {
            'text': self.payload['message']['text'],
            'chat_id': self.payload['message']['chat']['id'],
            'user': self.payload['message']['from']['id'],
            'type': 'message'
        }
        return data

    def edited_message_request(self):
        data = {
            'text': self.payload['edited_message']['text'],
            'chat_id': self.payload['edited_message']['chat']['id'],
            'user': self.payload['edited_message']['from']['id'],
            'type': 'edited_message'
        }
        return data


class BotBasic(object):

    def __init__(self, payload, bot_token):
        self.telegram_api = TelegramApi(bot_token)
        self.request = Request(payload)
        self.check_command()
        self.allow_access = self.check_access(self.request.data['user'])

    def check_command(self):
        re_command = re.match(r'^/\w+', self.request.data['text'])
        self.command = ""
        if re_command:
            self.command = "bot_" + re_command.group().replace('/', '')
        self.has_requested_command = getattr(self, self.command, None)

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

    def dont_understand(self):
        self.send_message("Bot don't understand your command ¯\_(ツ)_/¯")

    def telegram_response(self):
        return JsonResponse({}, status=200)

    def exception_occurred(self, err):
        self.send_message("Run-time error:{0}".format(err))

    def methods_bot(self):
        methods = []
        for attr in dir(self):
            if 'bot_' in attr:
                method = getattr(self, attr)
                methods.append("/{0} - {1}".format(attr.replace('bot_', ''), method.__doc__.strip(' \t\n\r')))
        return methods

    def check_access(self, from_id):
        return False if from_id != 199965779 else True

    def access_denied(self):
        self.send_message("Access denied")
