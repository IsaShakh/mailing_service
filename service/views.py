import os
from datetime import datetime
import requests
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from requests import RequestException
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from celery.utils.log import get_task_logger
from .models import *
from .serializers import *




class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MailingServiceViewSet(viewsets.ModelViewSet):
    serializer_class = MailingSerializer
    queryset = Mailing.objects.all()

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        queryset_mailing = Mailing.objects.all()
        get_object_or_404(queryset_mailing, pk=pk)
        queryset = Message.objects.filter(mailing_id=pk).all()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def full_desc(self, request):
        mailing = Mailing.objects.values("id")
        count_of_mailings = Mailing.objects.count()

        content = {
            "Количество рассылок": count_of_mailings,
            "Количество отправленных сообщений": "",
        }
        result = {}

        for m in mailing:
            res = {"Всего сообщений": 0, "Отправлено": 0, "Не отправлено": 0}
            mail = Message.objects.filter(mailing_id=m["id"]).all()
            group_sent = mail.filter(sending_status="Sent").count()
            group_no_sent = mail.filter(sending_status="No sent").count()
            res["Всего сообщений"] = len(mail)
            res["Отправлено"] = group_sent
            res["Не отправлено"] = group_no_sent
            result[m["id"]] = res

        content["Количество отправленных сообщений"] = result
        return Response(content)









