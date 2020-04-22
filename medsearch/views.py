from django.shortcuts import render, redirect
from django.views import View
from QueryProcessing import search
from QueryProcessing.QueryProcessor import QueryProcessor


# Create your views here.


class SearchView(View):
    def get(self, request):
        return render(request, 'search.html')


class ResultsView(View):
    def post(self, request):
        query = str(request.POST["query"])
        proc = QueryProcessor(query)
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})
