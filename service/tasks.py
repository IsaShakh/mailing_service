import datetime
import pytz
import requests
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
import os
from core.celery import app
from requests import RequestException

from .models import *

load_dotenv()
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
TIME_FORMAT = "%Y-%m-%d - %H:%M:%S"
logger = get_task_logger(__name__)
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}


@app.task(bind=True, retry_backoff=True)
def send_mail(self, info, mailing_id, client_id, url=URL):
    client = Client.objects.get(pk=client_id)
    mailing = Mailing.objects.get(pk=mailing_id)
    timezone = pytz.timezone(client.timezone)
    actual_time = datetime.now(timezone)

    if actual_time.time >= mailing.starting_date and actual_time.time <= mailing.ending_date:
        try:
            requests.post(url + str(info['id']), headers=headers, json=info)
            logger.info('Сообщение отправлено!')
        except RequestException as e:
            logger.error(f'{info['id']} - Произошла ошибка ')
            raise self.retry(e=e)
        else:
            Message.objects.filter(pk=info['id']).update(status='Sent')
    else:
        time = 24 - (
                int(actual_time.time().strftime("%H:%M:%S")[:2])
                - int(mailing.starting_date.time().strftime("%H:%M:%S")[:2])
        )
        logger.info(
            f'Сообщение - {info['id']} \\ Время отправки еще не подошло.'
            f'Повторная попытка через {time * 60 * 60}'

        )
        return self.retry(countdown=time * 60 * 60)
