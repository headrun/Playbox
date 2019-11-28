import csv
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from juicer.utils import *
from crunchbase_xpaths import *

class CrunchbaseBrowse(JuicerSpider):
    name = 'crunchbase_browse'
    start_urls = []
    search_api = 'https://crunchbase.com/v4/data/autocompletes?query=%s&limit=25&source=topSearch'
    search_words = ['Fortis Hospitals', 'Apollo Healthcare', 'Rainbow Hospitals', 'Sankara Eyecare', 'Naraya Hrudayalaya', 'Lalpath Labs', 'Biocon', 'Cipla', 'Amity university', 'KL University', 'IMT Ghaziabad', 'PESIT', 'Deloitte', 'SS Kothari Mehta & Co.', 'Chandan Agarwal & Co', 'Vasudev Adigas', 'Cafe Coffeee Day', 'Devi Shetty', 'Naveen Tewari']
    for search_word in search_words:
        start_urls.append(search_api % search_word)
    #start_urls = ['https://crunchbase.com/organization/swiggy']
    
    def __init__(self, *args, **kwargs):
    	super(CrunchbaseBrowse, self).__init__(*args, **kwargs)
    	self.headers = ('search_word', 'organization_name', 'org_desc', 'org_location', 'categories', 'headquarters_regions', 'founded_date', 'founders', 'operating_status', 'funding_status', 'last_funding_type', 'number_of_employees', 'also_known_as', 'legal_name', 'hub_tags', 'ipo_status', 'company_type', 'website', 'facebook', 'linkedin', 'twitter', 'contact_email', 'phone_number', 'image', 'reference_url')
        excel_file_name = '%s_%s.csv' % (self.name, str(datetime.datetime.now().date()))
        self.output_file = open(excel_file_name, 'wb+')
        self.todays_excel_file  = csv.writer(self.output_file)
        self.todays_excel_file.writerow(self.headers)
    	dispatcher.connect(self._spider_closed, signals.spider_closed)

    def _spider_closed(self, spider, reason):
        self.output_file.close()

    def parse(self, response):
        json_data = json.loads(response.body)
        entities = json_data.get('entities', [])
        search_word = response.url.split('query=')[-1].split('&')[0].replace('%20', ' ')
        for entity in entities:
            entity_identifier = entity.get('identifier', {})
            entity_type = entity_identifier['entity_def_id']
            entity_id = entity_identifier['permalink']
            entity_url = 'https://crunchbase.com/%s/%s' % (entity_type, entity_id)
            if entity_type == 'organization':
                yield Request(entity_url, callback = self.parse_next, meta = {'search_word': search_word})
                break

    def parse_next(self, response):
        sel = HTML(response)
        search_word = response.meta['search_word']
        json_data = ''.join(sel.xpath('//script[@id="client-app-state"]/text()').extract())
        if json_data:
            json_data = json.loads(json_data.replace('&q;', '"'))
            data = json_data['HttpState'].values()[0]['data']['cards']
        org_name = extract(sel, org_name_xpath)
        org_desc = extract(sel, org_desc_xpath)
        org_location = ''.join(sel.xpath(org_location_xpath).extract()).strip()
        categories, headquarters_regions, founded_date, founders, operating_status, funding_status, last_funding_type, number_of_employees, also_known_as, legal_name, hub_tags, ipo_status, company_type, website, facebook, linkedin, twitter, contact_email, phone_number = [''] * 19
        field_labels = get_nodes(sel, '//span[contains(@class, "field-label flex-100")]')
        field_values = get_nodes(sel, '//span[contains(@class, "field-value flex-100")]')
        image = extract(sel, '//meta[@property="og:image"]/@content')
        if len(field_labels) != len(field_values):
            return "fields mis-match. Please check"

        for field_label, field_value in zip(field_labels, field_values):
            header = extract(field_label, './/text()')
            value = extract(field_value, './/text()')
            if value.startswith('View on '):
                value = extract(field_value, './/a/@href')
            check_key =  header.lower().replace(' ', '_')
            if check_key == 'categories':
                categories = value
            elif check_key == 'headquarters_regions':
                headquarters_regions = value
            elif check_key == 'founded_date':
                founded_date = value
            elif check_key == 'founders':
               	founders = value
            elif check_key == 'operating_status':
				operating_status = value
            elif check_key == 'funding_status':
				funding_status = value
            elif check_key == 'last_funding_type':
				last_funding_type = value
            elif check_key == 'number_of_employees':
				number_of_employees = value
            elif check_key == 'also_known_as':
				also_known_as = value
            elif check_key == 'legal_name':
				legal_name = value
            elif check_key == 'hub_tags':
				hub_tags = value
            elif check_key == 'ipo_status':
				ipo_status = value
            elif check_key == 'company_type':
				company_type = value
            elif check_key == 'website':
				website = value
            elif check_key == 'facebook':
				facebook = value
            elif check_key == 'linkedin':
				linkedin = value
            elif check_key == 'twitter':
				twitter = value
            elif check_key == 'contact_email':
				contact_email = value
            elif check_key == 'phone_number':
                phone_number = value
        output_tuple = (search_word, org_name, org_desc, org_location, categories, headquarters_regions, founded_date, founders, operating_status, funding_status, last_funding_type, number_of_employees, also_known_as, legal_name, hub_tags, ipo_status, company_type, website, facebook, linkedin, twitter, contact_email, phone_number, image, response.url)
        self.todays_excel_file.writerow(output_tuple)
        #print output_tuple
        output_dict = dict(zip(self.headers, output_tuple))
        #from pprint import pprint
        print(output_dict)
        pass
