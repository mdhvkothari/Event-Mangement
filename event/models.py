from django.db import models

from common import BaseTimeStampModel


class Event(BaseTimeStampModel):
    """ Model representing an Event. """
    id = models.UUIDField(primary_key=True, help_text="Unique identifier for the event")
    name = models.CharField(max_length=255, help_text="Name of the event")
    location = models.CharField(max_length=255, help_text="Location of the event")
    start_time = models.DateTimeField(help_text="Start time of the event")
    end_time = models.DateTimeField(help_text="End time of the event")
    max_capacity = models.PositiveIntegerField(help_text="Maximum capacity of the event")

    def __str__(self):
        return self.name


class Attendee(BaseTimeStampModel):
    """ Model representing an Attendee for an Event. """
    id = models.UUIDField(primary_key=True, help_text="Unique identifier for the attendee")
    event = models.ForeignKey(Event, related_name="attendees", on_delete=models.CASCADE,
                              help_text="Event the attendee is registered for")
    name = models.CharField(max_length=100, help_text="Name of the attendee")
    email = models.EmailField(help_text="Email address of the attendee")

    class Meta:
        unique_together = ('event', 'email')

