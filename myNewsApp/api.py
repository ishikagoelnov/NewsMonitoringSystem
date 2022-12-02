from .serializers import *
from django.http import JsonResponse
from myNewsApp.models import *
from django.views.decorators.csrf import csrf_exempt


def StoryList(request):
    if request.method == 'GET':
        is_staff = request.user.is_staff
        subscriber = Subscriber.objects.select_related('client',
                                                       'company_data').get(
            user=request.user.id)
        subscribed_client = subscriber.client
        if is_staff:
            stories = Story.objects.select_related('tagged_client',
                                                   'source').prefetch_related(
                'tagged_company')

        else:
            stories = Story.objects.filter(
                tagged_client=subscribed_client).select_related('source',
                                                               'tagged_client').prefetch_related(
                'tagged_company')

        serialized_stories = Story_listing_Serializer(stories,
                                                      many=True)
        return JsonResponse(serialized_stories.data, safe=False, status=200)

    if request.method == 'POST':
        serializer = Story_listing_Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)


@csrf_exempt
def StoryDetail(request, pk):
    try:
        is_staff = request.user.is_staff
        subscriber = Subscriber.objects.select_related('client',
                                                       'company_data').get(
            user=request.user.id)
        subscribed_client = subscriber.client
        if is_staff:
            story = Story.objects.select_related('tagged_client',
                                                 'source').prefetch_related(
                'tagged_company').get(id=pk)

        else:
            story = Story.objects.filter(
                tagged_client=subscribed_client).select_related(
                'source',
                'tagged_client').prefetch_related(
                'tagged_company').get(id=pk)

    except Story.DoesNotExist:
        message = f'Story with id {pk} does not found '
        return JsonResponse({"Success": "False",
                             "Message": message}, safe=False, status=404)

    if request.method == 'GET':
        serialized_stories = Story_listing_Serializer(story)
        return JsonResponse(serialized_stories.data,safe=False, status=200)

    if request.method == 'PUT':
        serializer = Story_listing_Serializer(story,
                                              data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,safe=False, status=201)
        return JsonResponse(serializer.errors,safe=False, status=400)

    if request.method == 'DELETE':
        story.delete()
        return JsonResponse({"Message": "Story Deleted Successfully"},safe=False, status=204)
