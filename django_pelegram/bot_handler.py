from django.http import JsonResponse
from django.conf import settings
import requests
import re


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
            'testing_request': True if 'testing_request' in self.payload.keys() else False,
            'message_id': self.payload['callback_query']['message']['message_id']
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


class BotBasic(object):

    def __init__(self, payload=None, bot_token=None):
        self.bot_token = bot_token
        self.request = Request(payload)
        self.answer = {}

    def get_command(self):
        re_command = re.match(r'^/\w+', self.request.data['text'])
        command = ""
        if re_command:
            command = re_command.group().replace('/', '')
        return command

    def dont_understand_message(self):
        return "Bot don't understand your command ¯\_(ツ)_/"

    def json_response(self, data, status=200):
        return JsonResponse(data, status=status)

    def exception_template(self, err):
        return "Run-time error:\n{0}\n\nDELETE THIS OUTPUT FROM PRODUCTION!\n".format(err)

    def telegram_request(self, method, **kwargs):
        telegram_url = "{0}/bot{1}/".format(settings.TELEGRAM_API_URL, self.bot_token)
        telegram_response = requests.post(telegram_url + method, **kwargs)
        return telegram_response

    def answer_on_callback_query(self):
        if self.request.data['type'] == 'callback_query':
            if 'answer_callback' in self.answer:
                answer_callback_query_data = dict(callback_query_id=self.request.data['callback_query_id'],
                                                  **self.answer['answer_callback'])
            else:
                answer_callback_query_data = dict(callback_query_id=self.request.data['callback_query_id'],
                                                  text="Bot is typing")
            response = self.telegram_request("answerCallbackQuery", data=answer_callback_query_data)
        else:
            response = None
        return response

    def send_answer(self):
        answer_callback_response = self.answer_on_callback_query()
        if answer_callback_response is None:
            answer_responses = {}
        else:
            answer_responses = {"answer_callback": answer_callback_response}
        messages_response = []
        for message in self.answer['messages']:
            response = self.processing_message_action(message)
            messages_response.append(response)
        answer_responses['messages'] = messages_response
        return answer_responses

    def processing_message_action(self, message):
        handled_message = {'data': {}}
        for key in message['data'].keys():
            if key == 'file':
                handled_message['files'] = {'photo': open(message.data['file'], 'rb')}
            else:
                handled_message['data'][key] = message['data'][key]
        send_message_data = dict(chat_id=self.request.data['chat_id'], **handled_message['data'])
        if 'files' in handled_message.keys():
            response = self.telegram_request(message['action'], data=send_message_data, files=handled_message['files'])
        else:
            response = self.telegram_request(message['action'], data=send_message_data)
        return response
