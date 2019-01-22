from __future__ import unicode_literals

from django.db import models

class ApiSectionstable(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    wiki_id = models.CharField(max_length=100)
    imdb_id = models.CharField(max_length=100)
    source_id = models.CharField(max_length=100)
    season_id = models.CharField(max_length=100)
    series_id = models.CharField(max_length=100)
    item_type = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=200)
    episode_title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    episode_number = models.CharField(max_length=10)
    season_number = models.CharField(max_length=10)
    release_year = models.CharField(max_length=10)
    release_date = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.CharField(max_length=50, blank=True, null=True)
    genres = models.TextField(blank=True, null=True)
    maturity_ratings = models.CharField(max_length=50, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    purchase_info = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    directors = models.TextField(blank=True, null=True)
    producers = models.TextField(blank=True, null=True)
    writers = models.TextField(blank=True, null=True)
    cast = models.TextField(blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    aux_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    modified_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sections_api'
        unique_together = (('id', 'item_type', 'source_id'),)

