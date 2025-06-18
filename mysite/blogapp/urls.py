from django.urls import path

from .views import *

app_name = "blogapp"

urlpatterns = [
    path('', ArticleListView.as_view(), name='list'),
]
