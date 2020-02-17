import requests
import json


class Genre(object):
    def main(self):
        print("started")
        genre_url = 'https://apis.justwatch.com/content/genres/locale/en_US'
        r = requests.get(genre_url)
        data = json.loads(r.text)
        genre_dict = {}
        for i in data:
            key = i.get('id', '')
            short_name = i.get('short_name', '')
            value = i.get('translation', '')
            internal_dict = {}
            internal_dict.update(
                {key: {'translation': value, 'short_name': short_name}})
            genre_dict.update(internal_dict)

        f = open('genre_dict', 'w+')
        f.write(json.dumps(genre_dict))
        f.close()


if '__main__' == __name__:
    Genre().main()
