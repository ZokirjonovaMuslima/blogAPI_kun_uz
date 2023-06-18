from django.core.cache import cache
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter
from rest_framework.generics import (ListAPIView, RetrieveAPIView)
from rest_framework.response import Response
from rest_framework.views import (APIView)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import (New, Category, Staff, Region)
from .serializers import (NewModelSerializer, CategoryModelSerializer, StaffModelSerializer, SendEmailSerializer,
                          RegionModelSerializer, LastBlogModelSerializer, SearchModelSerializer)
from .tasks import send_email_customer


# Post
class BlogModelViewSet(ModelViewSet):
    queryset = New.objects.all()
    serializer_class = NewModelSerializer
    permission_classes = [IsAdminUser]

    # cache

    def list(self, request, *args, **kwargs):
        if cache.get('data') is None:
            cache.set('data', self.get_queryset(), timeout=60)
            return Response(self.get_serializer(self.get_queryset(), many=True).data)
        else:
            return Response(self.get_serializer(cache.get('data'), many=True).data)


# PostDetail
class BlogDetailRetrieveAPIView(RetrieveAPIView):
    queryset = New.objects.all()
    serializer_class = NewModelSerializer
    permission_classes = [IsAdminUser]

    # view

    def retrieve(self, request, *args, **kwargs):
        self.get_queryset()
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = NewModelSerializer(instance)
        return Response(serializer.data)


# LastNew
class LastBlogListModelViewSet(ReadOnlyModelViewSet):
    queryset = New.objects.all().order_by('-created_at')
    serializer_class = LastBlogModelSerializer


# StaffList
class StaffModelViewSet(ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffModelSerializer
    permission_classes = [IsAdminUser]


# Region
class RegionModelViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionModelSerializer
    permission_classes = [IsAdminUser]


# Category
class CategoryCreateAPIView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer
    permission_classes = [IsAdminUser]


# Search
class SearchModelSearchAPIView(ListAPIView):
    queryset = New.objects.all()
    serializer_class = SearchModelSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'short_description']


# Send email


class SendMailAPIView(APIView):
    def post(self, request):
        try:
            serializer = SendEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            name = serializer.validated_data.get('name')
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            message = serializer.validated_data.get('message')
            send_email_customer.delay(name, email, phone, message)
        except Exception as e:
            return Response({'success': False, 'message': str(e)})

        return Response({'success': True, 'message': 'Email sent!'})
