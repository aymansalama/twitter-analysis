from django.shortcuts import render
from .twitter_cred import consumer_key, consumer_secret, access_token, access_token_secret
import tweepy

#twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Create your views here.
