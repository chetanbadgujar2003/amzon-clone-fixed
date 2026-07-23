from rest_framework import serializers


class SellerSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    business_name = serializers.CharField(max_length=255)
    owner_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, allow_blank=True, required=False)
    category_focus = serializers.CharField(max_length=100, allow_blank=True, required=False)
    registration_id = serializers.CharField(max_length=100, allow_blank=True, required=False)
    business_description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(read_only=True)
    is_flagged = serializers.BooleanField(read_only=True, required=False)
    flag_reason = serializers.CharField(read_only=True, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)


class SellerRegisterSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    owner_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)
    category_focus = serializers.CharField(max_length=100, allow_blank=True, required=False)
    registration_id = serializers.CharField(max_length=100, allow_blank=True, required=False)
    business_description = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs


class SellerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SellerProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(allow_blank=True, required=False)
    price = serializers.FloatField()
    image = serializers.CharField(allow_blank=True, required=False)
    stock = serializers.IntegerField(default=0)
