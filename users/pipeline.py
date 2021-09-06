from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse

import requests
from django.conf import settings
from django.utils import timezone
from oauthlib import oauth2
from social_core.exceptions import AuthForbidden

from users.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'google-oauth2':
        return
    api_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json'
    print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        return
    data = response.json()['response'][0]
    print(f'===> {data}')

    if 'photo_max_orig' in data:
        photo_content = requests.get(data['photo_max_orig'])
        with open(f'{settings.MEDIA_ROOT}/users_avatar/{user.pk}.jpg', 'wb') as photo_file:
            photo_file.write(photo_content.content)

    if 'sex' in data:
        if data['sex'] == 1:
            user.shopuserprofile.gender = ShopUserProfile.FEMALE
        elif data['sex'] == 2:
            user.shopuserprofile.gender = ShopUserProfile.MALE

    if 'about' in data:
        user.shopuserprofile.aboutMe = data['about']

    if 'bdate' in data:
        bdate = datetime.strptime(data['bdate'], "%d.%m.%Y")
        age = datetime.now().year - bdate.year
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.google.GoogleOAuth2')
        user.age = age

    user.save()

# def save_user_profile(backend, user, response, *args, **kwargs):
#     if backend.name != 'google-oauth2':
#         return
#     api_url = urlunparse((
#         'https',
#         'api.google.com',
#         '/method/users.get',
#         None,
#         urlencode(OrderedDict(fields=','.join(('bdate', 'sex', 'about')),
#                               access_token=response['access_token'], v='5.92')), None))
#     resp = requests.get(api_url)
#     if resp.status_code != 200:
#         return
#
#     data = resp.json()['response'][0]
#     if data['sex']:
#         user.shopuserprofile.gender = ShopUserProfile.MALE if data['sex'] == 1 else ShopUserProfile.FEMALE
#
#     if data['about']:
#         user.shopuserprofile.aboutMe = data['about']
#
#     if data['tagline']:
#         user.shopuserprofile.tagline = data['tagline']
#
#     user.save()
#
