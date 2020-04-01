from django.shortcuts import render
from django.views import View
from medsearch.models import Document

# Create your views here.


class HomeView(View):

    def get(self):
        pass
    # return render('search.html')
    pass


class SearchResultsView(View):
    pass
