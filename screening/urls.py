from django.urls import path

from .views import ScreenResumesAPIView, screening_home


urlpatterns = [
    path("", screening_home, name="screening-home"),
    path("api/screen/", ScreenResumesAPIView.as_view(), name="screen-resumes"),
]
