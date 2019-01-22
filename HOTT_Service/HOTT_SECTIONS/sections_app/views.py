from rest_framework import viewsets

from models import ApiSectionstable
from serializers import APiSectionsSerializer

class SectionsViewSet(viewsets.ModelViewSet):
    queryset = ApiSectionstable.objects.all()
    serializer_class = APiSectionsSerializer

    def get_queryset(self):
        print self.request.GET
        queryset = ApiSectionstable.objects.all()
        item_type = self.request.GET.get('item_type', '')
        source_id = self.request.GET.get('source_id', '')
        sort_by = self.request.GET.get('sort_by', True)
        id_ = self.request.GET.get('id', '')
        season_id_ = self.request.GET.get('season_id', '')
        crawled_date = self.request.GET.get('crawled_date', '')
        if crawled_date:
            created_at__gte = crawled_date + " 00:00:00"
            created_at__lte = crawled_date + " 23:59:59"
            created_at__range = [created_at__gte, created_at__lte]
            queryset = queryset.filter(created_at__range=created_at__range)
        if sort_by:
            queryset = queryset.order_by('-created_at')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if id_:
            queryset = queryset.filter(id=id_)
        if season_id_:
            queryset = queryset.filter(season_id=season_id_)
        return queryset

