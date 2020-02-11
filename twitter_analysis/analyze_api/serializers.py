from rest_framework import serializers
from analyze_tweets.models import Tweet, Keyword, Job

class TweetSerializer(serializers.HyperlinkedModelSerializer):
    text = serializers.CharField(read_only=True)
    keyword = serializers.CharField(read_only=True)
    polarity = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    country = serializers.CharField(read_only=True)
    stored_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Tweet
        fields = ['text', 'keyword', 'polarity', 'country', 'stored_at']

class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']


class TweetAvgSerializer(serializers.HyperlinkedModelSerializer):
    keyword = serializers.CharField()
    class Meta:
        model = Tweet
        fields = ['keyword']
        