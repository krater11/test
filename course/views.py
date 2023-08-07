from rest_framework.decorators import api_view, authentication_classes,permission_classes
from .models import Course
from .serializers import CourseSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def generate_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# 函数式编程
@api_view(['GET', 'POST'])
@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def course_list(request):
    """
    获取所有课程信息或新增一个课程
    :param request:
    :return:
    """
    if request.method == "GET":
        s = CourseSerializer(instance=Course.objects.all(), many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        s = CourseSerializer(data=request.data)  # 部分更新用partial=True属性
        if s.is_valid():
            s.save(teacher=request.user)
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
    else:
        if request.method == "GET":
            s = CourseSerializer(instance=course)
            return Response(data=s.data, status=status.HTTP_200_OK)

        elif request.method == "PUT":
            s = CourseSerializer(instance=course, data=request.data)
            if s.is_valid():
                s.save()
                return Response(data=s.data, status=status.HTTP_200_OK)
            return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


# 类试图Class Based View
class CourseList(APIView):

    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        print(self.request.user, self.request.auth)
        print(type(self.request.user), type(self.request.auth))

        queryset = Course.objects.all()
        s = CourseSerializer(instance=queryset, many=True)
        return Response(s.data, status=status.HTTP_200_OK)

    def post(self, request):
        s = CourseSerializer(data=request.data)
        if s.is_valid():
            s.save(teacher=self.request.user)
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetail(APIView):

    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    @staticmethod
    def get_object(pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return

    def get(self, request, pk):
        obj = self.get_object(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(instance=obj)
        return Response(s.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = self.get_object(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(instance=obj, data=request.data)
        if s.is_valid():
            s.save()
            return Response(data=s.data, status=status.HTTP_200_OK)
        return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        obj = self.get_object(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(instance=obj, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(data=s.data, status=status.HTTP_200_OK)
        return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status.HTTP_204_NO_CONTENT)


# 通用类试图
class GCourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class GCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


# 视图集ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
