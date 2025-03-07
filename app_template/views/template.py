
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class IndexView(TemplateView):
    template_name = "app_template/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre'] = 'PSM & BIO Sistema Informático'
        return context