from rest_framework import viewsets

from .serializers import AlephEntrySerializer
from .models import AlephEntry


class AlephEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows aleph entries to be viewed or edited.
    """

    queryset = AlephEntry.objects.all()
    serializer_class = AlephEntrySerializer
