import pytz
from django.core.validators import RegexValidator
from django.db import models

from service import utils




class Mailing(models.Model):
    text = models.TextField(verbose_name="Text of message", max_length=500)
    starting_date = models.DateTimeField(verbose_name="Starting date")
    ending_date = models.DateTimeField(verbose_name="Ending date")
    tag = models.CharField(max_length=50, verbose_name="Filter tag", null=True, blank=True)

    def __str__(self):
        return self.starting_date

    class Meta:
        verbose_name = "Mailing"
        verbose_name_plural = "Mailings"


class Client(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(choices=TIMEZONES, default='UTC', max_length='50', verbose_name="Timezone")
    regex = RegexValidator(
        regex=r"^7\d{10}$",
        message="Phone should be in format 7xxxxxxxxx"
    )
    phone_number = models.CharField(
        validators=[regex],
        max_length=11,
        verbose_name="Phone"
    )
    mobile_code = models.CharField(max_length=2, verbose_name="Mobile code")
    tag = models.CharField(max_length=50, verbose_name="Filter tag", null=True, blank=True)

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=utils.STATUS_CHOICES, verbose_name="Status")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="message")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="message")

    def __str__(self):
        return self.created_at

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
