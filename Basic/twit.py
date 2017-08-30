# sudo pip install twython
# contents of auth.py (replace with real keys)
# consumer_key        = 'ABCDEFGHIJKLKMNOPQRSTUVWXYZ'
# consumer_secret     = '1234567890ABCDEFGHIJKLMNOPQRSTUVXYZ'
# access_token        = 'ZYXWVUTSRQPONMLKJIHFEDCBA'
# access_token_secret = '0987654321ZYXWVUTSRQPONMLKJIHFEDCBA'

# Hello World tweet
from twython import Twython

from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
message = "Hello world!"
twitter.update_status(status=message)
print("Tweeted: {}".format(message))
