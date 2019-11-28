from analyze_tweets.models import Keyword

def search_list(request):
    # Generate counts of some of the main objects
    search_list = Keyword.objects.all()
    return {"search_list": search_list}