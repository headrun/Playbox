from scrapy.exceptions import DropItem

from juicer.items import *


class ValidateRecordPipeline(object):

    def check_and_update_none_values(self, item):
        for k, v in item.iteritems():
            if v is None:
                item[k] = ''

        return item

    def check_movie_item(self, item):
        #if item.has_key('sk') and not item['sk']:
        if 'sk' in item and not item['sk']:
            raise DropItem('Movie Sk Missing: %s' % item)

        #if item.has_key('title') and not item['title']:
        if 'title' in item and not item['title']:
            raise DropItem('Movie Title Missing: %s' % item)

        return item

    def check_tvshow_item(self, item):
        #if item.has_key('sk') and not item['sk']:
        if 'sk' in item and not item['sk']:
            raise DropItem('Tvshow Sk Missing: %s' % item)

        #if item.has_key('title') and not item['title']:
        if 'title' in item and not item['title']:
            raise DropItem('Tvshow Title Missing: %s' % item)

        return item

    def check_season_item(self, item):
        #if not item.has_key('tvshow_sk'):
        if 'tvshow_sk' not in item:
            raise DropItem('Tvshow Sk Missing: %s' % item)

        #if item.has_key('sk') and not item['sk']:
        if 'sk' in item and not item['sk']:
            raise DropItem('Season Sk Missing: %s' % item)

        #if item.has_key('title') and not item['title']:
        if 'title' in item and not item['title']:
            raise DropItem("Season Title Empty for this item: %s" % item)

        return item

    def check_episode_item(self, item):
        #if not item.has_key('sk') or not item['sk']:
        if 'sk' in item and not item['sk']:
            raise DropItem("Episode Sk missing: %s" % item)

        #if not item.has_key('tvshow_sk') and not item.has_key('show_title'):
        if 'tvshow_sk' not in item and 'show_title' not in item:
            raise DropItem("Season Or Tvshow Sk missing: %s" % item)

        #if not item['tvshow_sk'] and not item['show_title']:
        if 'tvshow_sk' not in item and 'show_title' not in item:
            raise DropItem("Tvshow Sk and Season Sk Fields Don't have Values: %s" % item)

        #if item.has_key('title') and not item['title']:
           #raise DropItem("Episode/Clips Title missing for this item: %s" % item)


        return item

    def check_crew_item(self, item):
        if 'program_sk' in item and not item['program_sk']:
            raise DropItem("Crew Program Sk Missing For this Item: %s" % item)

        if 'person_id' in item and not item['person_id']:
            raise DropItem("Crew Person Id Missing For this Item: %s" % item)

        if 'name' in item and not item['name']:
            raise DropItem("Crew Person Id Missing For this Item: %s" % item)

        return item

    def check_related_program_item(self, item):
        #if item.has_key('program_sk') and not item['program_sk']:
        if 'program_sk' in item and not item['program_sk']:
            raise DropItem("In RelatedPrograms: Program Sk Missing For This Item: %s" % item)

        #if item.has_key('program_type') and not item['program_type']:
        if 'program_type' in item and not item['program_type']:
            raise DropItem("In RelatedPrograms: Program Type Missing For This Item: %s" % item)

        #if item.has_key('related_sk') and not item['related_sk']:
        if 'related_sk' in item and not item['related_sk']:
            raise DropItem("In RelatedPrograms: Related Sk Missing For This Item: %s" % item)

        return item

    def process_item(self, item, spider):
        if isinstance(item, MovieItem):
            item = self.check_movie_item(item)
            item = self.check_and_update_none_values(item)

        if isinstance(item, TvshowItem):
            item = self.check_tvshow_item(item)
            item = self.check_and_update_none_values(item)

        if isinstance(item, SeasonItem):
            item = self.check_season_item(item)
            item = self.check_and_update_none_values(item)

        if isinstance(item, EpisodeItem):
            item = self.check_episode_item(item)
            item = self.check_and_update_none_values(item)

        if isinstance(item, CrewItem):
            item = self.check_crew_item(item)
            item = self.check_and_update_none_values(item)

        if isinstance(item, RelatedProgramItem):
            item = self.check_related_program_item(item)

        return item
