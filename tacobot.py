from twython import TwythonStreamer, Twython
import requests
import os
import logging
from slughifi import slugify
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

APP_KEY = os.environ['TWITTER_API_KEY']
APP_SECRET = os.environ['TWITTER_API_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

tweeter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

class TacoStreamer(TwythonStreamer):
    def on_success(self, data):
        if data.get('text'):
            user = data.get('user')
            text = ' '.join(slugify(data.get('text')).split('_'))
            tweetback = False
            doc_url = 'https://docs.google.com/spreadsheet/ccc'
            params = {'key': '0Anp-zgGKPxl7dEd2TUpzSWQxWDR4UWFuWWxRc2RHbUE', 'output':'csv'}
            phrases = requests.get(doc_url, params=params)
            phrase_list = [slugify(p) for p in phrases.content.decode('utf-8').split('\n')]
            for phrase in phrase_list:
                if phrase in text:
                    tweetback = True
            if tweetback:
                screen_name = user.get('screen_name')
                recipe = requests.get('http://randomtaco.me/random/')
                if recipe.status_code is 200:
                    recipe = recipe.json()
                    logging.info(recipe)
                    base_layer = recipe['base_layer']['slug']
                    base_layer_name = recipe['base_layer']['name']
                    mixin = recipe['mixin']['slug']
                    mixin_name = recipe['mixin']['name']
                    condiment = recipe['condiment']['slug']
                    condiment_name = recipe['condiment']['name']
                    seasoning = recipe['seasoning']['slug']
                    seasoning_name = recipe['seasoning']['name']
                    shell = recipe['shell']['slug']
                    link = 'http://randomtaco.me/%s/%s/%s/%s/%s/' % (base_layer, mixin, condiment, seasoning, shell)
                    name = 'Your taco: %s, %s, %s, and %s' % (base_layer_name, mixin_name, condiment_name, seasoning_name)
                    trunc_idx = (len(name) - len(screen_name)) - 5
                    tweeter.update_status(status='@%s %s... %s' % (screen_name, name[:trunc_idx], link), in_reply_to_status_id=data.get('id'))

    def on_error(self, status_code, data):
        logging.error('Crud, got a %s, %s' % (status_code, data))

stream = TacoStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
stream.statuses.filter(track='@tacobot')
