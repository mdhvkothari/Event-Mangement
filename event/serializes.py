import datetime

# Django imports
from django.utils import timezone

# Third-party imports
from rest_framework import serializers

# Local imports
from .utils import DATETIME_FORMAT
from .models import Event, Attendee


class CreateEventSerializer(serializers.Serializer):
    """ Serializer for creating an Event. """
    name = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    start_time = serializers.DateTimeField(required=True, format=DATETIME_FORMAT)
    end_time = serializers.DateTimeField(required=True, format=DATETIME_FORMAT)
    max_capacity = serializers.IntegerField(required=True)

    def validate_start_time(self, value):
        """ Validate the start time of the event. """
        if value < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past.")
        return value

    def validate_end_time(self, value):
        """ Validate the end time of the event. """
        start_time = self.initial_data.get('start_time')
        try:
            start_time = datetime.datetime.strptime(start_time, DATETIME_FORMAT)
        except Exception:
            raise serializers.ValidationError("Invalid start_time format. Use YYYY-MM-DD HH:MM:SS.")
        if value <= start_time:
            raise serializers.ValidationError("End time must be after start time.")
        return value

    def validate_max_capacity(self, value):
        """ Validate the maximum capacity of the event. """
        if value <= 0:
            raise serializers.ValidationError("Max capacity must be a greater than zero.")
        return value


class EventSerializer(serializers.ModelSerializer):
    """ Serializer for Event model. """
    class Meta:
        model = Event
        fields = ('id', 'name', 'location', 'start_time', 'end_time', 'max_capacity')


class CreateAttendeeSerializer(serializers.Serializer):
    """ Serializer for creating an Attendee for an Event. """
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, data):
        """ Validate the attendee data and check event context. """
        event_id = self.context.get("event_id")
        if not event_id:
            raise serializers.ValidationError("Event ID is missing from context.")

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")

        if Attendee.objects.filter(event=event, email__iexact=data['email']).exists():
            raise serializers.ValidationError("Attendee with this email already registered.")

        if event.attendees.count() >= event.max_capacity:
            raise serializers.ValidationError("Event is at full capacity.")

        if event.start_time < timezone.now():
            raise serializers.ValidationError("Cannot register for a past event.")

        self.context['event'] = event
        return data


class AttendeeSerializer(serializers.ModelSerializer):
    """ Serializer for Attendee model. """
    class Meta:
        model = Attendee
        fields = ('id', 'name', 'email')

