import json
import datetime
from juicer.hott_utils import HTML, normalize, Request, md5,\
extract_data, JuicerSpider, extract_list_data, get_nodes, re
from juicer.items import ProgramCrewItem, CrewItem
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ThemoviedbPersonsTerminal(JuicerSpider):
    name = 'themoviedb_crew_terminal'

    def __init__(self, *args, **kwargs):
        super(ThemoviedbPersonsTerminal, self).__init__(*args, **kwargs)

    def parse(self, response):
        sk = response.meta.get('data').get('program_sk','')
        program_type = response.meta.get('data').get('program_type','')
        url= response.meta.get('data').get('reference_url')
        rank = response.meta.get('data').get('person_rank','')
        data = json.loads(response.text)
        name = data.get('name','')
        gender = data.get('gender','')
        if gender == 0 or gender == 2:
            gen = "Male"
        elif gender == 1:
            gen = "Female"
        birthday = data.get('birthday','')
        biography = data.get('biography','').encode('utf-8').strip()
        place = data.get('place_of_birth','')
        death_date = data.get('deathday','')
        image_link = data.get('profile_path','')
	if image_link == None:
            image = ''
        else:
	     image = "https://image.tmdb.org/t/p/w300_and_h450_bestv2" + image_link
        crew_sk = str(data.get('id',''))
        known_Dept = data.get('known_for_department','')
        if known_Dept == 'Acting':
            dept = "Actor"
        elif known_Dept == 'Editing':
            dept = "Editor"
        elif known_Dept == 'Directing':
            dept = "Director"
        elif known_Dept == 'Writing':
            dept = "Writer"
        elif known_Dept == "Production":
            dept = "Producer"
        else:
            dept = known_Dept
 	crew_item = CrewItem()
        crew_item.update({'sk': crew_sk ,
                            'name': normalize(name),
			    'gender':gen,
			    'birth_date':birthday,
			    'birth_place':place,
                            'death_date':death_date,
			    'biography':normalize(biography),
                            'image':image,
                            'aux_info':response.url,
                            'reference_url': url})
	print crew_item
        yield crew_item

        programcrew_item = ProgramCrewItem()
        programcrew_item.update({'program_sk':sk,'program_type':program_type,'crew_sk':crew_sk,'role':normalize(dept),'rank':rank})
        print programcrew_item
        yield programcrew_item
