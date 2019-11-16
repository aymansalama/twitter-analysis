import factory
import factory.django
from .models import Tweet

class TweetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tweet

    text = factory.Faker('sentence')
    tweet_id = factory.Faker('random_number',digits=3,fix_len = False)
    keyword = factory.Faker('random_element',elements=('pizza','trump','bobo','drugs','wheat'))
    country = factory.Faker('name')

    