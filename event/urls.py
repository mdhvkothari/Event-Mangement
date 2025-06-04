# Django imports
from django.urls import path, include


# Local imports
from .utils import Router
from .views import EventView, AttendeesView


router = Router()
router.register('', EventView, basename='event')
router.register('(?P<event_id>[0-9a-f-]+)/attendees', AttendeesView, basename='event-attendees')


# The urlpatterns list routes URLs to views.
urlpatterns = [
    path('', include(router.urls)),
]
