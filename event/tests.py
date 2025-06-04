import uuid

# django imports
from django.utils import timezone
from django.urls import reverse

# Third-party imports
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from .models import Event, Attendee


class EventAPITestCase(APITestCase):
    def setUp(self):
        self.event_create_url = reverse('event-list')
        self.start_time = timezone.now() + timezone.timedelta(days=1)
        self.end_time = self.start_time + timezone.timedelta(hours=2)

    def test_create_event_success(self):
        payload = {
            "name": "Django Conference",
            "location": "Bangalore",
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "max_capacity": 100
        }
        response = self.client.post(self.event_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)

    def test_create_event_with_invalid_times(self):
        payload = {
            "name": "Invalid Event",
            "location": "Online",
            "start_time": "2020-01-01 10:00:00",  # in the past
            "end_time": "2020-01-01 12:00:00",
            "max_capacity": 50
        }
        response = self.client.post(self.event_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_events(self):
        Event.objects.create(
            id=uuid.uuid4(),
            name="Future Event",
            location="Delhi",
            start_time=self.start_time,
            end_time=self.end_time,
            max_capacity=30
        )
        response = self.client.get(self.event_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)


class AttendeeAPITestCase(APITestCase):
    def setUp(self):
        self.event = Event.objects.create(
            id=uuid.uuid4(),
            name="Test Event",
            location="Mumbai",
            start_time=timezone.now() + timezone.timedelta(hours=2),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            max_capacity=2
        )
        self.attendee_url = reverse('event-attendees-list', kwargs={'event_id': self.event.id})

    def test_register_attendee_success(self):
        payload = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        response = self.client.post(self.attendee_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendee.objects.count(), 1)

    def test_invalidate_list_event_id(self):
        invalid_event_id = uuid.uuid4()
        url = reverse('event-attendees-list', kwargs={'event_id': invalid_event_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_registration_fails(self):
        Attendee.objects.create(id=uuid.uuid4(), event=self.event, name="John", email="john@example.com")
        payload = {
            "name": "John",
            "email": "john@example.com"
        }
        response = self.client.post(self.attendee_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_event_full(self):
        Attendee.objects.create(id=uuid.uuid4(), event=self.event, name="A", email="a@example.com")
        Attendee.objects.create(id=uuid.uuid4(), event=self.event, name="B", email="b@example.com")

        payload = {"name": "C", "email": "c@example.com"}
        response = self.client.post(self.attendee_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_attendees(self):
        Attendee.objects.create(id=uuid.uuid4(), event=self.event, name="Alice", email="alice@example.com")
        response = self.client.get(self.attendee_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
