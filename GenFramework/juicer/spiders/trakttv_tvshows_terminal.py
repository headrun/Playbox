from juicer.utils import *
from juicer.items import *
import re

Domain = 'https://trakt.tv'
class TraktTvTerminal(JuicerSpider):
    name = 'trakttv_tvshows_terminal'

    def parse(self, response):
        sel = Selector(response)
        data = response.meta['data']
        category = data['category']
        sk = normalize(extract_data(sel, '//div[@id="overview"]/@data-spoiler-show-id'))
        title = normalize(extract_data(sel, '//div[@class="container"]//div[contains(@class, "mobile-title")]/h1/text()'))
        relea_year = extract_data(sel, '//div[@class="container"]//div[contains(@class, "mobile-title")]//span[@class="year"]/text()')
        release_date = normalize(extract_data(sel, '//li/label[contains(text(), "Premiered")]/following-sibling::span/@data-date').replace('T', ' ').strip('Z'))
        if not relea_year:
            relea_year = str(re.findall('\d{4}', release_date))
        dura = extract_data(sel, '//li/label[contains(text(), "Runtime") and not(contains(text(), "Total Runtime"))]/following-sibling::text()').strip(' mins')
        duration = str(int(dura)*60)
        pro_country = normalize(extract_data(sel, '//li/label[contains(text(), "Country")]/following-sibling::text()'))
        lang = normalize(extract_data(sel, '//li/label[contains(text(), "Language")]/following-sibling::text()'))
        genre = normalize(extract_data(sel, '//li/label[contains(text(), "Genres")]//following-sibling::text()').replace(',', '<>'))
        desc = normalize(extract_data(sel, '//div[@id="overview"]/p/text()'))
        tvshow_item = TvshowItem()
        tvshow_item.update({'sk':sk, 'title':title, 'duration':duration, 'production_country':pro_country, 'languages':lang, 'description':desc, 'genres':genre, 'reference_url':response.url})
        yield tvshow_item
        nodes = get_nodes(sel, '//div[@id="seasons-episodes-sortable"]//div[@data-type="season"]')
        for node in nodes:
            season_id = extract_data(node, './@data-season-id')
            season_links = extract_data(node, './meta[@itemprop="url"]/@content')
            yield Request(season_links, self.parse_seasons, meta={'season_id':season_id, 'tvshow_sk':sk, 'production_country':pro_country, 'languages':lang, 'title':title})

    def parse_seasons(self, response):
        sel = Selector(response)
        season_id = response.meta['season_id']
        tvshow_sk = response.meta['tvshow_sk']
        pro_country = response.meta['production_country']
        lang = response.meta['languages']
        title = response.meta['title']
        sea_num = (response.url).split('/seasons/')[-1]
        sea_desc = normalize(extract_data(sel, '//div[@id="overview"]/p/text()'))
        sea_genre = normalize('<>'.join(extract_list_data(sel, '//li/label[contains(text(), "Genres")]//following-sibling::span/text()')))
        hrs = extract_data(sel, '//li/label[contains(text(), "Total Runtime")]/following-sibling::span[@class="number hours"]/text()')
        mins = extract_data(sel, '//li/label[contains(text(), "Total Runtime")]/following-sibling::span[@class="number minutes"]/text()')
        if hrs and mins:
            duration = str((int(hrs)*60*60)+int(mins)*60)
        else:
            dura = extract_data(sel, '//li/label[contains(text(), "Runtime")]/following-sibling::text()').strip(' mins')
            duration = str(int(dura)*60)
        season_item = SeasonItem()
        season_item.update({'sk':season_id, 'tvshow_sk':tvshow_sk, 'title':title, 'description':sea_desc, 'duration':duration,'season_number':sea_num, 'genres':sea_genre,'reference_url':response.url})
        yield season_item
        episode_nodes = get_nodes(sel, '//div[@id="seasons-episodes-sortable"]//div[contains(@data-season-number, "%s")]'%sea_num)
        for node in episode_nodes:
            epi_url = extract_data(node, './div/@data-url')
            if 'http' not in epi_url and epi_url:
                epi_url = Domain+epi_url
                episode_sk = epi_url.split('/episodes/')[-1]
                yield Request(epi_url, self.parse_episodes, meta={'tvshow_sk':tvshow_sk, 'season_sk':season_id, 'episode_sk':episode_sk, 'show_title':title, 'season_number':sea_num})
    def parse_episodes(self, response):
        sel = Selector(response)
        tvshow_sk = response.meta['tvshow_sk']
        season_sk = response.meta['season_sk']
        episode_sk = response.meta['episode_sk']
        show_title = response.meta['show_title']
        season_number = response.meta['season_number']
        episode_number = (response.url).split('/episodes/')[-1]
        epi_genre = normalize('<>'.join(extract_list_data(sel, '//li/label[contains(text(), "Genres")]//following-sibling::span/text()')))
        desc = normalize(extract_data(sel, '//div[@id="overview"]/p/text()'))
        produc_coun = normalize(extract_data(sel, '//li/label[contains(text(), "Country")]/following-sibling::text()'))
        dura = extract_data(sel, '//li/label[contains(text(), "Runtime")]/following-sibling::text()').strip(' mins')
        duration = str(int(dura)*60)
        epi_title = extract_data(sel, '//h1[@class="episode"]//span[contains(@data-spoiler-episode-id, "%s")]/text()' %episode_sk)
        episode_item = EpisodeItem()
        episode_item.update({'sk':episode_sk, 'tvshow_sk':tvshow_sk, 'season_sk':season_sk, 'title':epi_title,'show_title':show_title,'season_number':season_number, 'episode_number':episode_number, 'genres':epi_genre, 'description':desc, 'production_country':produc_coun, 'duration':duration,'metadata_language':'english', 'reference_url':response.url})
        print episode_item
        yield episode_item
