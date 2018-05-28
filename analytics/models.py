from django.db import models


class AnalyticsRecord(models.Model):
    timestamp = models.DateTimeField(blank=True)
    path = models.TextField(blank=True)
    referer = models.TextField(blank=True)
    investigation_uuid = models.TextField(blank=True)
    domain = models.TextField(blank=True)
    user_agent = models.TextField(blank=True)
    method = models.TextField(blank=True)
    title = models.TextField(blank=True)
    visitor_uuid = models.TextField(blank=True)
    user_profile_uuid = models.TextField(blank=True)
