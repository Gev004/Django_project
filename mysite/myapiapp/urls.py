from django.urls import path

from .views import *

app_name = "myapiapp"

urlpatterns = [
    path('hello/', hello_world_view, name='hello'),
]