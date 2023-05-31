from rest_framework.generics import (ListCreateAPIView, RetrieveAPIView)
from rest_framework.generics import (ListCreateAPIView, RetrieveAPIView)
from rest_framework.response import Response
from rest_framework.views import (APIView)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import (New, Category, Staff, Region)
from .serializers import (NewModelSerializer, CategoryModelSerializer, StaffModelSerializer, SendEmailSerializer,
                          RegionModelSerializer, LastBlogModelSerializer)
from .tasks import send_email_customer


# Post
class BlogModelViewSet(ModelViewSet):
    queryset = New.objects.all()
    serializer_class = NewModelSerializer


# PostDetail
class BlogDetailRetrieveAPIView(RetrieveAPIView):
    queryset = New.objects.all()
    serializer_class = NewModelSerializer

    def get_queryset(self):
        query = super().get_queryset().order_by('-views')
        return query


# LastNew
class LastBlogListModelViewSet(ReadOnlyModelViewSet):
    queryset = New.objects.all().order_by('-created_at')
    serializer_class = LastBlogModelSerializer


# StaffList
class StaffModelViewSet(ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffModelSerializer


# Region
class RegionModelViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionModelSerializer


# Category
class CategoryCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer


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


# Search
# class SearchAPIView(APIView):
#
#     @swagger_auto_schema(query_serializer=SearchSerializer)
#     def get(self, request):
#         q = request.GET.get('title', 'short_description', None)
#         posts = New.objects.filter(title__iexact=q, short_description__iexact=q)
#         serializer = NewModelSerializer(posts, many=True)
#         return Response(serializer.data)
