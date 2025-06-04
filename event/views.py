import uuid

# django imports
from django.utils import timezone

# Third-party imports
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response

# Local imports
from .serializes import (
    CreateEventSerializer,
    EventSerializer,
    CreateAttendeeSerializer,
    AttendeeSerializer
)
from .models import Event, Attendee
from common import WithExtraDetailPageNumberPagination


class EventView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """ Viewset for handling Event creation and listing."""

    pagination_class = WithExtraDetailPageNumberPagination

    def get_serializer_class(self):
        """ Returns the appropriate serializer class based on the request method."""
        if self.request.method == 'POST':
            return CreateEventSerializer
        return EventSerializer

    def get_queryset(self):
        """ Returns the queryset for Event instances."""
        return Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')

    def perform_create(self, data):
        """ Creates a new Event instance with a unique UUID."""
        return Event.objects.create(
            id=uuid.uuid4(),
            **data
        )

    def create(self, request, *args, **kwargs):
        """ Handles the creation of a new Event instance."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer.validated_data)
        response = EventSerializer(obj)
        return Response(response.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """ Handles the listing of all Event instances."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class AttendeesView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    """ Viewset for handling Attendees of an Event."""

    pagination_class = WithExtraDetailPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAttendeeSerializer
        return AttendeeSerializer

    def create_attendee(self, data, event):
        """ Creates a new Attendee instance."""
        return Attendee.objects.create(
            id=uuid.uuid4(),
            event=event,
            **data
        )

    def create(self, request, *args, **kwargs):
        """ Handles the creation of a new Attendee for a specific Event."""
        serializer = self.get_serializer(data=request.data, context={'event_id': kwargs.get('event_id')})
        serializer.is_valid(raise_exception=True)
        obj = self.create_attendee(serializer.validated_data, serializer.context['event'])
        response = AttendeeSerializer(obj)
        return Response(response.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """ Handles the listing of Attendees for a specific Event."""
        event_id = kwargs.get('event_id')
        if not event_id:
            return Response(
                {"error": "Event ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = event.attendees.all().order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
