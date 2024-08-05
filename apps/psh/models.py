from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class PSHConcept(MPTTModel):
    pshid = models.CharField(max_length=8, unique=True, primary_key=True)
    name_cs = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['name_cs']
