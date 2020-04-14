from django.shortcuts import render
from django.views import View
from medsearch.models import Document
import search

# Create your views here.


class HomeView(View):

    def get(self, request):
        return render(request, 'loginscreen.html')

    def post(self, request):
        query = str(request.POST["query"])
        results = search.perform_search(query)

        return render(request, 'results.html', {"results": results})
