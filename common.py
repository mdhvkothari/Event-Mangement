from collections import OrderedDict

# Django imports
from django.db import models

# Third-party imports
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BaseTimeStampModel(models.Model):
    """
    Base Time stamp model to add created and modified property to every model.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when object was created.")
    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when object was last updated.")

    class Meta:
        abstract = True


class WithExtraDetailPageNumberPagination(PageNumberPagination):
    """ Pagination class that adds extra details to the paginated response. """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data, extra_details=None):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('pageSize', self.page_size),
            ('showing', "Page {} of {}".format(self.page.number, self.page.paginator.num_pages)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))