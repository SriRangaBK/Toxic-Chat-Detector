from django.urls import path
from .views import check_comment

urlpatterns = [
    path('check/', check_comment),
]
