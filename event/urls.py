from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('category/<str:category>/', views.category_list, name='category-list'),
    path('categories/', views.categories_list, name='categories-list'),
    path('search/', views.search_events, name='event-search'),
]
