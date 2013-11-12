from twython import TwythonStreamer, Twython
import requests
import os

APP_KEY = os.environ['TWITTER_API_KEY']
APP_SECRET = os.environ['TWITTER_API_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

tweeter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

class TacoStreamer(TwythonStreamer):
    def on_success(self, data):
        user = data.get('user')
        if user:
            screen_name = user.get('screen_name')
            recipe = requests.get('http://randomtaco.me/random/')
            if recipe.status_code is 200:
                recipe = recipe.json()
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
                name = '%s %s %s %s' % (base_layer_name, mixin_name, condiment_name, seasoning_name)
                tweeter.update_status(status='@%s %s %s' % (screen_name, name, link))

    def on_error(self, status_code, data):
        print status_code

stream = TacoStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
stream.statuses.filter(track='@tacobot')
