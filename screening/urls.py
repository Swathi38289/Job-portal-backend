from django.urls import path

from .views import ScreenResumesAPIView


urlpatterns = [
    path("api/screen/", ScreenResumesAPIView.as_view(), name="screen-resumes"),
]
