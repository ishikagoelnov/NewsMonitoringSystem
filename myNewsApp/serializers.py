from myNewsApp.models import *
from rest_framework import serializers, permissions


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class Source_Serializer(serializers.ModelSerializer):
    sourced_client = serializers.CharField(read_only=True)

    class Meta:
        model = Source
        fields = ('id', 'name', 'url', 'sourced_client')


class Story_listing_Serializer(serializers.ModelSerializer):
    source_id = serializers.PrimaryKeyRelatedField(source='source', queryset=Source.objects.all())
    source=serializers.CharField(read_only=True)
    tagged_client_id = serializers.PrimaryKeyRelatedField(source='tagged_client', queryset=Company.objects.all())
    tagged_company = CompanySerializer(read_only=True, many=True)
    permission_classes = [permissions.IsAuthenticated]

    class Meta:
        model = Story
        fields = ('id', 'title', 'source_id', 'source', 'pub_date', 'body_text',
                  'url', 'tagged_client_id', 'tagged_company')

