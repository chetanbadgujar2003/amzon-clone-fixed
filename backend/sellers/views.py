from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.utils import IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.serializers import UserSerializer
from core.permissions import IsSuperAdminUser
from products.models import Category, Product
from products.serializers import ProductSerializer, ProductListSerializer

from .models import Seller
from .serializers import (
    SellerSerializer,
    SellerRegisterSerializer,
    SellerLoginSerializer,
    SellerProductCreateSerializer,
)


def _get_seller_for_user(user):
    return Seller.objects.filter(user_id=user.id).first()


class SellerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SellerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data.pop('password2')
        password = data.pop('password')
        email = data['email']

        if User.objects.filter(username=email).exists() or Seller.objects.filter(email=email).first():
            return Response(
                {'detail': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(username=email, email=email, password=password)

        seller = Seller(
            user_id=user.id,
            business_name=data['business_name'],
            owner_name=data['owner_name'],
            email=email,
            phone=data.get('phone', ''),
            category_focus=data.get('category_focus', ''),
            registration_id=data.get('registration_id', ''),
            business_description=data.get('business_description', ''),
            status='pending',
        )
        try:
            seller.save()
        except IntegrityError:
            user.delete()
            return Response(
                {'detail': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if data.get('category_focus'):
            cat_name = data['category_focus']
            if not Category.objects.filter(name=cat_name).first():
                Category(name=cat_name, slug=slugify(cat_name)).save()

        refresh = RefreshToken.for_user(user)
        refresh['role'] = 'seller'
        return Response({
            'seller': SellerSerializer(seller).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class SellerLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SellerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        seller = _get_seller_for_user(user)
        if not seller:
            return Response({'error': 'No seller account found for this login.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        refresh['role'] = 'seller'
        return Response({
            'seller': SellerSerializer(seller).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class SellerMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seller = _get_seller_for_user(request.user)
        if not seller:
            return Response({'error': 'Not a seller account.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(SellerSerializer(seller).data)


class SellerMeProductsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seller = _get_seller_for_user(request.user)
        if not seller:
            return Response({'error': 'Not a seller account.'}, status=status.HTTP_403_FORBIDDEN)
        products = Product.objects.filter(seller=seller).order_by('-created_at')
        return Response(ProductListSerializer(products, many=True).data)

    def post(self, request):
        seller = _get_seller_for_user(request.user)
        if not seller:
            return Response({'error': 'Not a seller account.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SellerProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        category_name = validated.pop('category', None)
        category = None
        if category_name:
            category = Category.objects.filter(name=category_name).first()
            if not category:
                category = Category(name=category_name, slug=slugify(category_name))
                category.save()

        base_slug = slugify(validated['name'])
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product(
            category=category,
            seller=seller,
            slug=slug,
            **validated,
        )
        product.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class SellerMeProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_owned_product(self, request, product_id):
        seller = _get_seller_for_user(request.user)
        if not seller:
            return None, Response({'error': 'Not a seller account.'}, status=status.HTTP_403_FORBIDDEN)
        product = Product.objects.filter(id=product_id, seller=seller).first()
        if not product:
            return None, Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        return product, None

    def patch(self, request, product_id):
        product, error = self._get_owned_product(request, product_id)
        if error:
            return error
        for field in ('price', 'stock', 'description', 'name', 'is_active'):
            if field in request.data:
                setattr(product, field, request.data[field])
        product.save()
        return Response(ProductSerializer(product).data)

    def delete(self, request, product_id):
        product, error = self._get_owned_product(request, product_id)
        if error:
            return error
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Admin-only seller management
# ---------------------------------------------------------------------------

class AdminSellerListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        query = Seller.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            query = query.filter(status=status_filter)
        return Response(SellerSerializer(query, many=True).data)


class AdminSellerVerifyView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
        seller.status = 'verified'
        seller.save()
        return Response(SellerSerializer(seller).data)


class AdminSellerRejectView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
        seller.status = 'rejected'
        seller.save()
        return Response(SellerSerializer(seller).data)


class AdminSellerFlagView(APIView):
    """Regular Admin can red-flag a seller (e.g. suspected fraud) but cannot
    remove them — only a SuperAdmin can act on a flag."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
        seller.is_flagged = True
        seller.flag_reason = request.data.get('reason', '')
        seller.save()
        return Response(SellerSerializer(seller).data)


class AdminSellerUnflagView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
        seller.is_flagged = False
        seller.flag_reason = ''
        seller.save()
        return Response(SellerSerializer(seller).data)


class AdminSellerDetailView(APIView):
    """SuperAdmin-only: permanently remove a (typically flagged) seller and
    cascade-delete everything they own."""
    permission_classes = [IsSuperAdminUser]

    def delete(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)

        # cascade: remove their products, then their linked Django user, then the seller doc
        Product.objects.filter(seller=seller).delete()
        User.objects.filter(id=seller.user_id).delete()
        seller.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminSellerProductsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, seller_id):
        seller = Seller.objects.filter(id=seller_id).first()
        if not seller:
            return Response({'error': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
        products = Product.objects.filter(seller=seller).order_by('-created_at')
        return Response(ProductListSerializer(products, many=True).data)
