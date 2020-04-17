from django.db import models

# Create your models here.


class Document(models.Model):
    docID = models.IntegerField(default=0)
    title = models.CharField(default=" ")
    url = models.CharField(default=" ")
    summary = models.CharField(default=" ")
    date = models.CharField(default=" ")
    type = models.CharField(default=" ")

