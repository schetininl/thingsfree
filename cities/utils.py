import os

import requests
from dotenv import load_dotenv

from .models import City, Region

load_dotenv()


class VkLoader:

    def __init__(self, url, api_version='5.92'):
        self.params = {
            'access_token': os.getenv('VK_TOKEN'),
            'v': api_version
        }
        self.url = url

    def get_objects(self, **kwargs):
        self.params.update(kwargs)
        try:
            response = requests.post(self.url, params=self.params)
            response.raise_for_status()
            return response.json()['response']['items']
        except Exception:
            return []


def load_geo_objects():
    City.objects.all().delete()
    Region.objects.all().delete()

    country_loader = VkLoader('https://api.vk.com/method/database.getCountries')
    region_loader = VkLoader('https://api.vk.com/method/database.getRegions')
    city_loader = VkLoader('https://api.vk.com/method/database.getCities')

    regions = []
    cities = []

    vk_countries = country_loader.get_objects(code='RU')
    for vk_country in vk_countries:
        vk_regions = region_loader.get_objects(country_id=vk_country['id'])
        for vk_region in vk_regions:
            regions.append(Region(name=vk_region['title']))
            vk_cities = city_loader.get_objects(
                country_id=vk_country['id'],
                region_id=vk_region['id']
            )
            for vk_city in vk_cities:
                cities.append(City(region=regions[-1], name=vk_city['title']))

    Region.objects.bulk_create(regions)
    City.objects.bulk_create(cities)
