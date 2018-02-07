from pelegram.telegram import TelegramApi
import re
from django.http import JsonResponse

class BotBasic(object):

    def __init__(self, payload, bot_token):
        self.telegram_api = TelegramApi(bot_token)
        self.payload = payload
        try:
            self.message = payload['message']
        except KeyError:
            self.message = payload['edited_message']
        self.check_command()
        #self.register_user()

    def check_command(self):
        re_command = re.match(r'^/\w+', self.message['text'])
        self.command = ""
        if re_command:
            self.command = re_command.group().replace('/', '')
        self.has_requested_command = getattr(self, self.command, None)

    def send_message(self, message):
        self.telegram_api.send_message(self.message['chat']['id'], message)

    def dont_understand(self):
        self.send_message("Bot don't undestand your command ¯\_(ツ)_/¯")

    def telegram_response(self):
        return JsonResponse({}, status=200)

    def exception_occurred(self, err):
        self.send_message("Run-time error:{0}".format(err))
    """
    def register_user(self):
        user = Users.objects.get_or_create(identif=self.message['chat']['id'], password='123',)
        self.user = user
    """
