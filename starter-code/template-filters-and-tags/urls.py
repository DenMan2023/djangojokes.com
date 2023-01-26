from django.urls import path

from .views import FilterView, HomePageView, TagView

urlpatterns = [
    path('', HomePageView.as_view(), name='homepage'),
    path('filters/', FilterView.as_view(), name='filters'),
    path('tags/', TagView.as_view(), name='tags'),
]