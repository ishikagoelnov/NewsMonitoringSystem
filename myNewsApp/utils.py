import feedparser
from dateutil.parser import parse
from myNewsApp.models import Story
from django.db import IntegrityError


def story_view(user_id=None, is_staff=False, stories=None):
    if stories:
        storyCount = stories.count()
        context = {
            'stories': stories,
            'storyCount': storyCount
        }
        return context


def update_summary(description):
    updated_description = ""
    if '<' in description:
        ed = description.rfind('>')
        updated_description += description[ed + 1:]
    else:
        updated_description += description
    return updated_description


def story_fetching(source, subscriber, stories):
    source_url = source.url
    news_fetching = feedparser.parse(source_url)
    allEntries = news_fetching.entries
    for entry in allEntries:
        title = entry.title
        description = entry.summary
        updated_description = update_summary(description)
        # parsing the published date to mm-dd-yy format
        entry1 = entry.published
        pub_date = parse(entry1)
        url = entry.link
        clientHere = source.sourced_client
        companyHere = subscriber.company_data  # company data
        if not stories.filter(url=url).exists():
            try:
                story_obj = Story.objects.create(title=title,
                                                 source=source,
                                                 pub_date=pub_date,
                                                 body_text=updated_description,
                                                 url=url,
                                                 tagged_client=clientHere)
                story_obj.save()
                story_obj.tagged_company.add(companyHere)
            except IntegrityError as e:
                continue


def check_rss(url):
    url_split = url.split('.')
    for i in url_split:
        if i == 'xml' or i == 'cms':
            return True
    return False
