from django.db import models


class AnalyticsRecord(models.Model):
    timestamp = models.DateTimeField(blank=True)
    path = models.TextField(null=True)
    referer = models.TextField(null=True)
    investigation_uuid = models.TextField(null=True)
    domain = models.TextField(null=True)
    user_agent = models.TextField(null=True)
    method = models.TextField(null=True)
    title = models.TextField(null=True)
    visitor_uuid = models.TextField(null=True)
    user_profile_uuid = models.TextField(null=True)
    visitor_id = models.TextField(null=True)
