from juicer.utils import *
from juicer.items import *

Domain = 'https://trakt.tv'
class TraktTvTerminal(JuicerSpider):
    name = 'trakttv_movie_terminal'
    #handle_httpstatus_list = ['404', '500']    
    def parse(self, response):
        handle_httpstatus_list = ['404', '500']
        sel = Selector(response)
        data = response.meta['data']
        category = data['category']
        aux_info = {}
        just_links = response.meta['sk']
        justwatch = 'https://www.justwatch.com/us/movie/%s'%just_links
        yield Request(justwatch, self.parse_justwatch)
        movie_id = extract_data(sel, '//div[@class="container"]//div/@data-spoiler-movie-id')
        sk = normalize(movie_id)
        title = extract_data(sel, '//div[@class="container"]//div[contains(@class, "mobile-title")]/h1/text()')
        desc = extract_data(sel, '//div[contains(@data-spoiler-movie-id, "%s")]/div[@itemprop="description"]/p/text()' %movie_id)
        tagline = extract_data(sel, '//div[contains(@data-spoiler-movie-id, "%s")]/div[@id="tagline"]/text()' %movie_id)
        rel_year = extract_data(sel, '//div[@class="container"]//div[contains(@class, "mobile-title")]//span[@class="year"]/text()')
        rel_date = extract_data(sel, '//li//span[@class="format-date"]//@data-date')
        if rel_year=='':
            rel_year = re.findall('\d{4}', rel_date)
        run_time = extract_data(sel, '//li//label[contains(text(), "Runtime")]//following-sibling::meta[@itemprop="duration"]/@content').strip('PM')
        duration = str(int(run_time)*60)
        country = extract_data(sel, '//li/label[contains(text(), "Country")]/following-sibling::text()')
        lang = extract_data(sel, '//li/label[contains(text(), "Language")]/following-sibling::text()')
        genre = '<>'.join(extract_list_data(sel, '//li/label[contains(text(), "Genres")]/following-sibling::span[@itemprop="genre"]//text()'))
        image = extract_data(sel, '//div[@class="mobile-poster"]//img[@itemprop="image"]/@data-original')
        video_link = extract_data(sel, '//div[@class="affiliate-links"]//div[contains(text(), "Videos")]/following-sibling::a[contains(@class, "popup-video")]/@href')
        video_link_type = extract_data(sel, '//div[@class="affiliate-links"]//div[@class="text"]/div[@class="site"]/text()')
        extra_links = extract_list_data(sel, '//ul[@class="external"]//li/a/@href')
        official_site = extract_data(sel, '//ul[@class="external"]//li/a[contains(text(), "Official Site")]/@href')
        for extr_link in extra_links:
            if 'imdb' in extr_link:
                imdb_link = extr_link
                imdb_id = imdb_link.split('/find?q=')[-1].split('&s=tt')[0].split('/title/')[-1]
            elif 'themoviedb' in extr_link:
                tmdb_link = extr_link
                tmdb_id = tmdb_link.split('/movie/')[-1]
            elif 'wikipedia' in extr_link:
                wiki_link = extr_link
            elif 'fanart' in extr_link:
                fanart_link = extr_link
                fanart_id = fanart_link.split('/movie/')[-1]
            elif 'justwatch' in extr_link:
                just_link = extr_link
        aux_info.update({'IMDB':normalize(imdb_link),'imdb_id':normalize(imdb_id), 'TMDB':normalize(tmdb_link), 'tmdb_id': normalize(tmdb_id), 'wiki':normalize(wiki_link),'Fanart': normalize(fanart_link),'fanart_id':normalize(fanart_id), 'Justwatch':normalize(just_link), 'tagline':normalize(tagline), 'official_site':normalize(official_site)})

        if 'http' not in image:
            image = Domain + image
        movie_item = MovieItem()
        movie_item.update({'sk':sk,
                            'title':normalize(title),
                            'description':normalize(desc),
                            'production_country':normalize(country),
                            'duration':duration,
                            'languages':normalize(lang.lower()),
                            'metadata_language':'english',
                            'category' : category,
                            'genres': normalize(genre),
                            'reference_url':response.url,
                            'aux_info': str(aux_info)})
        yield movie_item
        otherlinks_item = OtherLinksItem()
        otherlinks_item.update({'sk':md5(video_link),'program_sk':sk, 'program_type':'movie', 'url':normalize(video_link), 'url_type':normalize(video_link_type), 'domain':Domain})
        yield otherlinks_item
        richmedia_item = RichMediaItem()
        richmedia_item.update({'sk':md5(image),
                                'program_sk':sk,
                                'program_type':'movie',
                                'media_type':'image',
                                'image_type':'poster',
                                'image_url': normalize(image),
                                'reference_url':response.url})
        yield richmedia_item
        releases_item = ReleasesItem()
        releases_item.update({'program_sk':sk,
                                'program_type':'movie',
                                'release_year':str(rel_year),
                                'release_date':str(rel_date),
                                'country':normalize(country)})
        yield releases_item
        avail_stream_link = response.url + '/streaming_links?country=us'
        yield Request(avail_stream_link, self.availability, meta={'sk':sk, 'title':normalize(title), 'refer_url':response.url})

        direct_link = extract_list_data(sel, '//span[@itemprop="director"]/meta[@itemprop="url"]/@content')
        writer_link = extract_list_data(sel, '//span[@itemprop="writer"]/meta[@itemprop="url"]/@content')
        actor_link = extract_list_data(sel, '//li[@itemprop="actor"]/a/@href')
        crew_dict = {'directors':direct_link, 'writers':writer_link, 'actors':actor_link}
        rank = 0
        for key, value in crew_dict.iteritems():
            if "directors" in key:
                role_name = 'director'
            elif "writers" in key:
                role_name = 'writer'
            elif "actors" in key:
                role_name = 'actor'
            for crew_list in value:
                if crew_list:
                    rank = rank+1
                    if 'http' not in crew_list:
                        url = Domain + crew_list
                    else:
                        url = crew_list
                    yield Request(url, self.crew_details, dont_filter=True, meta = {'role_name' : role_name, 'program_sk':sk, 'rank':rank, 'refer_url':response.url})
    def crew_details(self, response):
        sel = Selector(response)
        refer_url = response.url #meta['refer_url']
        role_name = response.meta['role_name']
        program_sk = response.meta['program_sk']
        rank = response.meta['rank']
        crew_sk = (response.url).split('/')[-1]
        crew_name = extract_data(sel, '//div[contains(@class, "mobile-title")]/h1/text()')
        age = extract_data(sel, '//ul/li/label[contains(text(), "Age")]/following-sibling::text()')
        born_date = extract_data(sel, '//ul/li/label[contains(text(), "Born")]/following-sibling::span[@class="format-date"]/@data-date')
        birth_place = extract_data(sel, '//ul/li//span[@class="format-date"]/following-sibling::text()')
        image = extract_data(sel, '//div[@class="mobile-poster"]//img[@itemprop="image"]/@data-original')
        biogr = extract_data(sel, '//p[@id="biography"]/following-sibling::p/text()')
        death_date = extract_data(sel, '//ul/li/label[contains(text(), "Died")]/following-sibling::span[@class="format-date"]/@data-date')
        if 'http' not in image:
            image = Domain + image
        crew_item = CrewItem()
        crew_item.update({'sk':crew_sk+'-'+role_name,
                            'name': normalize(crew_name),
                            'age': str(age),
                            'biography':normalize(biogr),
                            'birth_place':normalize(birth_place),
                            'image':normalize(image),
                            'death_date':normalize(death_date),
                            'birth_date':normalize(born_date),
                            'reference_url': refer_url})
        prgcrew_item = ProgramCrewItem()
        prgcrew_item.update({'program_sk':program_sk,
                            'program_type':'movie',
                            'crew_sk': crew_sk+'-'+role_name,
                            'role':role_name,
                            'rank':rank})
        if crew_name:
            yield crew_item
            yield prgcrew_item

    def availability(self, response):
        sel = Selector(response)
        sk = response.meta['sk']
        title = response.meta['title']
        url = response.meta['refer_url']
        availitems = []
        type_ = 'movie'
        price_nodes =  get_nodes(sel, '//div[@class="streaming-links"]//div[@class="title"]')
        for node_ in price_nodes:
            nodes = get_nodes(node_, './/following-sibling::div[@class="section"]//a[@data-country="us"]')
            for node in nodes:
                '''watch_now = extract_data(node, './@href')
                if 'http' not in watch_now:
                    watch_now = Domain + watch_now
                    avail_sk = watch_now.split('/')[-1]
                    yield Request(watch_now, self.availability_details, meta={'sk':sk, 'title':title, 'url':url, 'type_':type_})'''
                price_ = extract_list_data(node, './/div[@class="price"]//text()')
                avail_portal = extract_data(node, './@data-source')
                watch_now = extract_data(node, './@href')
                if 'http' not in watch_now:
                    watch_now = Domain + watch_now
                    avail_sk = watch_now.split('/')[-1]
                for price_info in price_:
                    data_items = {}
                    if 'Included with' in price_info or 'Subscription' in price_info:
                        price_info = 'subscription'
                    if 'free' in price_info.lower():
                        pc_type = price_info
                        price = ''
                        price_type = 'free'
                        with_sub = 'false'
                        sub_type = ''
                    elif 'subscription' in price_info:
                        pc_type = ''
                        price = ''
                        price_type = ''
                        with_sub = 'true'
                        sub_type = 'addon_subscription'
                    elif 'Buy' in price_info or 'Rent' in price_info:
                        pc_type = price_info.split(':')[0]
                        price = (price_info.split(':')[-1]).strip()
                        price_type = 'known'
                        with_sub = 'false'
                        sub_type = ''
                    platform ='pc'
                    template_id = 'trakttv_' + avail_portal + '_movie'
                    char_sk = (response.url).split('/movies/')[-1].split('/')[0]
                    template_values = {'sk':avail_sk, 'char_sk':char_sk}
                    data_items = {
                    'title':title, 'platform_id': avail_portal,
                    'country_code':'us', 'template_id':template_id,
                    'template_values':template_values,
                    'last_refreshed_timestamp':'',
                    'program_type':type_,
                    'medium_type':'streaming',
                    'with_subscription':with_sub,
                    'subscription_type':sub_type,
                    'price':price.strip('$'), 'purchase_type':pc_type.lower(),
                    'price_currency':'usd', 'price_type':price_type,
                    'quality':'sd', 'scraper_args':'',
                    'duration':0, 'is_3d':'',
					'scraper_args':watch_now,
                    'reference_url':url,
                    'content_start_timestamp':'',
                    'content_expiry_timestamp':''
                    }
                    availitems.append(data_items)
                availitem = AvailItem()
                availitem.update({
            	'source_id':'trakttv', 'program_sk':sk,
                'source_availabilities':availitems,
                'source_program_id_space':''})
                yield availitem
                print url
                #yield Request(watch_now, self.availability_details, meta={'data_items':data_items, 'availitems':availitems})
    '''def availability_details(self, response):
        sel = Selector(response)
        import pdb;pdb.set_trace()
        availitems = response.meta['availitems']
        sk = response.meta['sk']
        data_items = response.meta['data_items']
        data_items.update({'scraper_args':response.url})
        availitems.append(data_items) 
        availitem = AvailItem()
        availitem.update({
            'source_id':'trakttv', 'program_sk':sk,
                'source_availabilities':availitems,
                'source_program_id_space':''})
        yield availitem
        print availitem'''
    def parse_justwatch(self, response):
        sel = Selector(response)
        import pdb;pdb.set_trace()
