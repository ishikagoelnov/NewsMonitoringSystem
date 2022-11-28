from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.http import Http404


class StoryList(APIView):
    def get(self, request):
        is_staff = request.user.is_staff
        subscriber = Subscriber.objects.select_related('client',
                                                       'company_data').get(
            user=request.user.id)
        subcribed_client = subscriber.client
        print(request.user.id)
        print(subcribed_client)
        if is_staff:
            stories = Story.objects.select_related('tagged_client',
                                                   'source').prefetch_related(
                'tagged_company')

        else:
            stories = Story.objects.filter(
                tagged_client=subcribed_client).select_related('source',
                                                               'tagged_client').prefetch_related(
                'tagged_company')

        serialized_stories = Story_listing_Serializer(stories,
                                                      many=True)
        return Response(serialized_stories.data)

    def post(self, request):
        serializer = Story_listing_Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class StoryDetail(APIView):

    def get_object(self, request, pk):
        try:
            is_staff = request.user.is_staff
            subscriber = Subscriber.objects.select_related('client',
                                                           'company_data').get(
                user=request.user.id)
            subcribed_client = subscriber.client
            if is_staff:
                story = Story.objects.select_related('tagged_client',
                                                     'source').prefetch_related(
                    'tagged_company').get(id=pk)

            else:
                story = Story.objects.filter(
                    tagged_client=subcribed_client).select_related(
                    'source',
                    'tagged_client').prefetch_related(
                    'tagged_company').get(id=pk)

            return story
        except Story.DoesNotExist:
            return

    def get(self, request, pk):
        story = self.get_object(request, pk)
        if not story:
            return Response(f'Story with id {pk} does not found')
        serialized_stories = Story_listing_Serializer(story)
        return Response(serialized_stories.data)

    def put(self, request, pk):
        story = self.get_object(request, pk)
        if not story:
            return Response(f'Story with id {pk} does not found ')
        serializer = Story_listing_Serializer(story,
                                              data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        story = self.get_object(request, pk)
        if not story:
            return Response(f'Story with id {pk} does not found')
        story.delete()
        return Response(status=
                        status.HTTP_204_NO_CONTENT)
