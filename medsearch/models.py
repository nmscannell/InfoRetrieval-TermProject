from django.db import models

# Create your models here.


class Document(models.model):
    docID = models.IntegerField(default=0)
    title = models.CharField(default=" ")
    author = models.CharField(default=" ")
    summary = models.CharField(default=" ")
    source = models.CharField(default=" ")
    publication_month = models.IntegerField(default=1)
    publication_day = models.IntegerField(default=1)
    publication_year = models.IntegerField(default=2000)
