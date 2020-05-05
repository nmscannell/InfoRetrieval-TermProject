from django.db import models

# Create your models here.


class Document(models.Model):
    docID = models.IntegerField(default=0)
    title = models.CharField(default=" ", max_length=150)
    url = models.CharField(default=" ", max_length=150)
    summary = models.TextField(default=" ")
    date = models.CharField(default=" ", max_length=10)
    type = models.CharField(default=" ", max_length=10)

