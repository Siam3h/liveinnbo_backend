from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .models import Event
from .serializers import EventSerializer
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Custom pagination for events
class EventPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

# List all events or create a new one
class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer
    pagination_class = EventPagination
    permission_classes = [AllowAny]


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    # Apply the cache_page decorator only to the GET method
    @method_decorator(cache_page(60 * 5))  # Cache the GET request for 5 minutes
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Events filtered by category
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 5)
def category_list(request, category):
    events = Event.objects.filter(category=category).order_by('-created_at')
    if not events:
        return Response({"message": f"No events found in category: {category}"}, status=status.HTTP_404_NOT_FOUND)
    
    paginator = EventPagination()
    paginated_events = paginator.paginate_queryset(events, request)
    serializer = EventSerializer(paginated_events, many=True)
    return paginator.get_paginated_response(serializer.data)

# Retrieve all distinct categories
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 10)
def categories_list(request):
    categories = Event.objects.values('category').distinct().order_by('category')
    return Response({'categories': list(categories)}, status=status.HTTP_200_OK)

# Search for events
@api_view(['GET'])
@permission_classes([AllowAny])
def search_events(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({"message": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)

    query_list = query.split()
    results = Event.objects.none()

    for word in query_list:
        results = results | Event.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word)
        ).order_by('-created_at')

    paginator = EventPagination()
    paginated_results = paginator.paginate_queryset(results, request)
    serializer = EventSerializer(paginated_results, many=True)

    if not results.exists():
        message = "Sorry, no results found for your search query."
    else:
        message = ""

    return paginator.get_paginated_response({"results": serializer.data, "message": message})

