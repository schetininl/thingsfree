import logging
import os
import uuid
from time import sleep

import requests
from django.db import connection, transaction
from dotenv import load_dotenv

from .models import Region

load_dotenv()
logger = logging.getLogger(__name__)


class VkLoader:
    def __init__(self, url, api_version='5.92'):
        self.params = {
            'access_token': os.getenv('VK_TOKEN'),
            'v': api_version,
            'count': 1000
        }
        self.url = url

    def get_objects(self, **kwargs):
        self.params.update(kwargs)
        try:
            items = []
            total_count = 1
            offset = 0
            while offset < total_count:
                self.params['offset'] = offset
                response = requests.post(self.url, params=self.params)
                # API ВКонтакте не позволяет делать более 3-х запросов в секунду
                sleep(0.35)
                response.raise_for_status()
                response_body = response.json()['response']
                total_count = response_body['count']
                items.extend(response_body['items'])
                offset += self.params['count']
            return items

        except Exception as err:
            logger.error(
                f'Ошибка при вызове метода {self.url}: '
                f'{err}'
            )
            return []


@transaction.atomic
def load_geo_objects():
    """
    Функция выполняет загрузку регионов и населенных пунктов, используя
    API ВКонтакте.
    """
    country_loader = VkLoader('https://api.vk.com/method/database.getCountries')
    region_loader = VkLoader('https://api.vk.com/method/database.getRegions')
    city_loader = VkLoader('https://api.vk.com/method/database.getCities')

    new_cities = []

    vk_countries = country_loader.get_objects(code='RU')
    for vk_country in vk_countries:
        vk_regions = region_loader.get_objects(country_id=vk_country['id'])
        for vk_region in vk_regions:
            region, _ = Region.objects.get_or_create(name=vk_region['title'])
            vk_cities = city_loader.get_objects(
                country_id=vk_country['id'],
                region_id=vk_region['id']
            )
            new_cities.extend([
                (uuid.uuid4().hex, region.id.hex, vk_city['title'])
                for vk_city in vk_cities
            ])

    # Для ускорения загрузки большого количества городов используются "голые"
    # SQL запросы. Загрузка происходит в несколько этапов (в одной транзакции):
    # 1) Создается таблица tmp_city для временного хранения данных
    # 2) Все полученные через API данные о населенных пунктах загружаются
    #    в tmp_city
    # 3) Из tmp_city выбираются все населенные пункты, которые отсутствуют в
    #    таблице модели City - cities_city. Выбранные данные переносятся
    #    в cities_city.
    # 4) Уничтожается таблица tmp_city
    with connection.cursor() as cursor:
        cursor.execute((
            'CREATE TABLE IF NOT EXISTS tmp_city('
            'id char(32), '
            'region_id char(32), '
            'name varchar(50))'
        ))
        cursor.executemany((
            'INSERT INTO tmp_city(id, region_id, name) '
            'VALUES(%s, %s, %s)'),
            new_cities
        )
        # В следющем запросе используется группировка таблицы tmp_city,
        # поскольку в одном регионе могут находиться населенные пункты с
        # одинаковыми названиями
        cursor.execute((
            'INSERT INTO cities_city(id, region_id, name) '
            'SELECT max(tc.id), tc.region_id, tc.name '
            'FROM tmp_city tc '
            'LEFT JOIN cities_city c '
            'ON (tc.name = c.name AND tc.region_id = c.region_id) '
            'WHERE c.id IS NULL '
            'GROUP BY tc.region_id, tc.name'
        ))
        cursor.execute('DROP TABLE tmp_city')
