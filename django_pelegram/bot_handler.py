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


class Answer(object):

    def __init__(self):
        self._data = {}
        self._action = None

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action_name):
        self._action = action_name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, params):
        self._data = params


class BotBasic(object):

    def __init__(self, payload=None, bot_token=None):
        self.telegram_api = TelegramApi(bot_token)
        self.request = Request(payload)
        self.answer = Answer()

    def get_command(self):
        re_command = re.match(r'^/\w+', self.request.data['text'])
        command = ""
        if re_command:
            command = re_command.group().replace('/', '')
        return command

    def prepare_request_data(self, **kwargs):
        return dict(**kwargs)

    def dont_understand_message(self):
        return "Bot don't understand your command ¯\_(ツ)_/"

    def json_response(self, data, status=200):
        return JsonResponse(data, status=status)

    def exception_template(self, err):
        return "Run-time error:\n{0}\n\nDELETE THIS OUTPUT FROM PRODUCTION!\n".format(err)

    def send_message(self):
        """

        requirement:
        message

        """
        send_message_data = self.prepare_request_data(chat_id=self.request.data['chat_id'],
                                                      **self.answer.data['message'])
        self.telegram_api.request("sendMessage", data=send_message_data)
        if self.request.data['type'] == 'callback_query':
            if 'answer_callback' in self.answer.data:
                answer_callback_query_data = self.prepare_request_data(
                    callback_query_id=self.request.data['callback_query_id'], **self.answer.data['answer_callback'])
            else:
                answer_callback_query_data = self.prepare_request_data(
                    callback_query_id=self.request.data['callback_query_id'], text="Request")
            self.telegram_api.request("answerCallbackQuery", data=answer_callback_query_data)

    def send_photo(self):
        """

        requirement:
        file - file object

        """
        self.telegram_api.request("sendPhoto", data={'chat_id': self.request.data['chat_id']},
                                  files=self.data['file'])
