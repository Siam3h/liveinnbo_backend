from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Blog
from .serializers import BlogSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Custom pagination for blogs
class BlogPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100

# List all blogs or create a new one
class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.filter(is_approved=True).order_by('-time')
    serializer_class = BlogSerializer
    pagination_class = BlogPagination
    permission_classes = [AllowAny]

# Retrieve, update, or delete a blog by slug

class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.filter(is_approved=True)
    serializer_class = BlogSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

# Retrieve blogs filtered by category
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 20)
def category_list(request, category):
    blogs = Blog.objects.filter(category=category, is_approved=True).exclude(slug__isnull=True).exclude(slug__exact='').order_by('-time')
    if not blogs.exists():
        return Response({"message": f"No posts found in category: '{category}'"}, status=status.HTTP_404_NOT_FOUND)

    paginator = BlogPagination()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    serializer = BlogSerializer(paginated_blogs, many=True)
    return paginator.get_paginated_response(serializer.data)

# Retrieve all distinct categories
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 20)
def categories_list(request):
    categories = Blog.objects.values('category').distinct().order_by('category')
    return Response({'categories': list(categories)}, status=status.HTTP_200_OK)

# Search for blogs
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 20)
def search_blogs(request):
    query = request.GET.get('q', '')

    if query:
        query_list = query.split()
        results = Blog.objects.none()

        for word in query_list:
            results |= Blog.objects.filter(
                Q(title__icontains=word) | Q(content__icontains=word),
                is_approved=True
            ).order_by('-time')

        paginator = BlogPagination()
        paginated_results = paginator.paginate_queryset(results, request)
        serializer = BlogSerializer(paginated_results, many=True)

        message = "" if results.exists() else f"Sorry, no results found for '{query}'."
    else:
        message = "Please enter a search term."
        serializer = None

    return Response({
        "results": serializer.data if serializer else [],
        "query": query,
        "message": message
    })

# Retrieve blog details by slug with previous and next blog
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 20)
def blogpost_detail_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_approved=True)
    previous_blog = Blog.objects.filter(is_approved=True, time__lt=blog.time).order_by('-time').first()
    next_blog = Blog.objects.filter(is_approved=True, time__gt=blog.time).order_by('time').first()

    serializer = BlogSerializer(blog)
    previous_serializer = BlogSerializer(previous_blog) if previous_blog else None
    next_serializer = BlogSerializer(next_blog) if next_blog else None

    return Response({
        "blog": serializer.data,
        "previous_blog": previous_serializer.data if previous_serializer else None,
        "next_blog": next_serializer.data if next_serializer else None,
    })
