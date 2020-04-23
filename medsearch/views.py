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


class RadiationView(View):
    def get(self, request):
        proc = QueryProcessor("radiation effects")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})


class MicroView(View):
    def get(self, request):
        proc = QueryProcessor("microgravity")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})


class VisionView(View):
    def get(self, request):
        proc = QueryProcessor("Vision Loss")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})


class DystrophyView(View):
    def get(self, request):
        proc = QueryProcessor("muscular dystrophy")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})


class IsolationView(View):
    def get(self, request):
        proc = QueryProcessor("psychological effects of isolation")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})


class ReverseView(View):
    def get(self, request):
        proc = QueryProcessor("reverse blood flow")
        mes, results = proc.perform_search()
        return render(request, 'results.html', {"results": results})
