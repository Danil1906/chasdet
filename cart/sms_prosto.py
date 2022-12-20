import requests
from typing import Union
from requests.exceptions import HTTPError


class smsRequest:

    def __init__(self, login, password):
        self.login = login
        self.password = password

    # Проверка состояния счета
    def checkMoney(self):
        params = {'login': self.login,
                  'password': self.password}

        url = 'http://api.prostor-sms.ru/messages/v2/balance/'

        try:
            response = requests.get(url, params=params)

            # если ответ успешен, исключения задействованы не будут
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')

        return response.text

    # Проверка очереди отпарвлений
    def checkQueueSend(self, statusName: str, limit: int):
        # statusName - Название очереди статусов сообщений. Название очереди устанавливается при передаче
        # сообщения
        # limit - Количество запрашиваемых статусов из очереди (по умолчанию 1, макс. 1000)

        params = {'login': self.login,
                  'password': self.password,
                  'statusQueueName': statusName,
                  'limit': limit}

        url = 'http://api.prostor-sms.ru/messages/v2/statusQueue/'

        try:
            response = requests.get(url, params=params)

            # если ответ успешен, исключения задействованы не будут
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')

        return response.text

    # Проверка состояния отправленного сообщения. Можно указывать до 200 id в запросе одновременно
    # http: // api.prostor - sms.ru / messages / v2 / status /?id=A132571BC&id=A132571BD&id=A132571BE
    # Возвращает ответ вида
    # A132571BC; delivered
    # A132571BD; smsc submit
    # A132571BE; queued

    def checkStatusSend(self, id: Union[int, list]):
        params = {'login': self.login,
                  'password': self.password}
        params['id'] = id
        url = 'http://api.prostor-sms.ru/messages/v2/status/'

        try:
            response = requests.get(url, params=params)

            # если ответ успешен, исключения задействованы не будут
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')

        return response.text

    # Отправка сообщения
    # При успешном запросе ответ будет accepted;A132571BC
    # где до знака ; идет статус а после знака id запроса
    def send(self, phone, text, sender=None, queue=None, timer=None):
        # queue - Название очереди статусов отправленных сообщений, в случае, если вы хотите использовать
        # очередь статусов отправленных сообщений. От 3 до 16 символов, буквы и цифры (например
        # myQueue1)
        # sender - подпись отправителя
        # timer - Дата для отложенной отправки сообщения, в UTC (2008-07-12T14:30:01Z)

        params = {'login': self.login,
                  'password': self.password,
                  'phone': phone,
                  'text': text,
                  }

        url = 'http://api.prostor-sms.ru/messages/v2/send/'
        sending_id = None

        if sender:
            params['sender'] = sender

        if queue:
            params['scheduleTime'] = timer

        if timer:
            params['statusQueueName'] = queue

        # Выполнение запроса

        try:
            response = requests.get(url, params=params)

            # если ответ успешен, исключения задействованы не будут
            response.raise_for_status()
            response_return = response.text
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            response_return = http_err
        except Exception as err:
            print(f'Other error occurred: {err}')
            response_return = err
        else:
            print('Success!')

            succ = response.text
            succ = int(succ.split(';')[1])
            sending_id = succ

        return {'response': response_return, 'sending_id': sending_id}

# a = smsRequest('en141899', '978313')
# print(a.checkMoney())
