import factory
import factory.django
from .models import Tweet, Keyword

class TweetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tweet

    text = factory.Faker('sentence')
    tweet_id = factory.Faker('random_number',digits=3,fix_len = False)
    keyword = factory.Faker('random_element',elements=Keyword.objects.all())
    country = factory.Faker('name')

    