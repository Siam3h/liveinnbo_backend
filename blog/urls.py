from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlogListCreateView.as_view(), name='blog-list-create'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('category/<str:category>/', views.category_list, name='category-list'),
    path('categories/', views.categories_list, name='categories-list'),
    path('search/', views.search_blogs, name='blog-search'),
    path('detail/<slug:slug>/', views.blogpost_detail_view, name='blog-detail-view'),
]
