from rest_framework import serializers
from models import ApiSectionstable 

class APiSectionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ApiSectionstable
        fields = ('id', 'wiki_id', 'imdb_id', 'source_id', 'season_id', 'series_id', 'item_type', 'title', 'episode_title', 'description', 'episode_number', 'season_number', 'release_year', 'release_date', 'expiry_date', 'genres', 'maturity_ratings', 'duration', 'purchase_info', 'url', 'image_url', 'directors', 'producers', 'writers', 'cast', 'categories', 'aux_info', 'created_at', 'modified_at')

