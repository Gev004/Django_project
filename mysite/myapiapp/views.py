from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view

@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({'hello': 'world'})