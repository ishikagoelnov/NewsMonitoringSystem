from myNewsApp.models import *
from rest_framework import serializers, permissions
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


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
    source_id = serializers.PrimaryKeyRelatedField(source='source',
                                                   queryset=Source.objects.all())
    source = serializers.CharField(read_only=True)
    tagged_client_id = serializers.PrimaryKeyRelatedField(
        source='tagged_client', queryset=Company.objects.all())
    tagged_company = CompanySerializer(read_only=True, many=True)
    permission_classes = [permissions.IsAuthenticated]

    class Meta:
        model = Story
        fields = (
            'id', 'title', 'source_id', 'source', 'pub_date',
            'body_text',
            'url', 'tagged_client_id', 'tagged_company')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom class
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'first_name': {'required': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscriberSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()  # create method call  data pass

    class Meta:
        model = Subscriber
        fields = '__all__'
        extra_fields = ['user']

    def create(self, validated_data):
        # instance of user
        request = self.context.get('request')
        company_id = request.POST.get('company')
        company_instance = Company.objects.get(id=company_id)
        client_id = request.POST.get('client')
        client_instance = Company.objects.get(id=client_id)
        subscribed_user = Subscriber.objects.create(user=self.user,
                                                    company_data=company_instance,
                                                    client=client_instance)
        subscribed_user.save()
        return subscribed_user
