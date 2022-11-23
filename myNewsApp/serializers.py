from myNewsApp.models import *
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class Story_listing_Serializer(serializers.ModelSerializer):
    source = serializers.CharField(read_only=True)
    tagged_client = serializers.CharField(read_only=True)
    tagged_company = CompanySerializer(read_only=True, many=True)

    class Meta:
        model = Story
        fields = ('id', 'title', 'source', 'pub_date', 'body_text',
                  'url', 'tagged_client', 'tagged_company')
