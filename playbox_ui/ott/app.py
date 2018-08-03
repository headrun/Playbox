from flask import Flask, request, render_template, jsonify
import requests
import json

app = Flask(__name__)
"""http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie"""
"""rn = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&item_type=movie&limit=100&offset=100&source_id=netflix')
 ra =requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&item_type=movie')"""
rn = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&id=80173524')
ra = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&id=B0747LHQYL')
"""rv = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=vudu&id=896126')"""

value = rn.json()['results']+ra.json()['results']
def result():
    return value

@app.route('/')
def index():
    x=[]
    y=""
    """r = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie')"""
    value =result()
    for i in range(len(value)):
        x.append(value[i]['image_url'])
        y+=" "+value[i]['url'][0:40]

    return render_template('gallery.html',image_url=x,len = len(x),image_index=y.split())

    """return render_template('gallery.html')"""
@app.route('/movies/')
def movies():
    x=[]
    y=""
    z=[]
    comon=[]
    """r = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie')"""
    value = result()
    for i in range(len(value)):
        x.append(value[i]['image_url'])
        y+=" "+value[i]['url'][0:40]
        z.append(value[i]['title'])

    """for i in range(len(z)):
        for j in range(i+1,len(z)):
            if z[i] == z[j]:
                comon.append(j)

    if len(comon) == 0:
        lp=1;
    else:
        lp=len(comon)    ,com = comon,lp=lp"""

    return render_template('gallery.html',image_url=x,len = len(x),image_index=y.split(),image_title=z,l=len(z))
@app.route('/shows/')
def shows():
    x=[]
    y=""
    z=[]
    """r = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie')"""
    value = result()
    for i in range(len(value)):

        x.append(value[i]['image_url'])
        y+=" "+value[i]['url'][0:40]
        z.append(value[i]['title'])

    return render_template('shows.html',image_url=x,len = len(x),image_index=y.split(),image_title = z)


@app.route('/sri/')
def inf():
    """value =result()
    x=[]
    for i in range(len(value)):
        x.append(value[i]['image_url'])"""

    return render_template('infor.html')

@app.route('/<int:id>/')
def info(id):
    x=[]
    z=[]
    d=""
    di=""
    di=[]
    ca=[]
    ge=[]
    src=[]
    comon=[]
    type=[]
    refurl =[]
    purchase=[]
    pu=[]
    dic={}
    """r = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie')"""
    value = result()
    for i in range(len(value)):
        if value[i]['image_url'] =="" :
            x.append(value[0]['image_url'])
        else:
            x.append(value[i]['image_url'])
        z.append(value[i]['title'])
        refurl.append(value[i]['url'])
        type.append(value[i]['item_type'])
        ge.append(value[i]['genres'].replace('"',''))
        d+=""+value[i]['description']+"#@"
        di.append(value[i]['directors'])
        if value[i]['cast'] =="" :
            ca.append("Details not avaialble")
        else:
            ca.append(value[i]['cast'].replace('"',''))
        src.append(value[i]['source_id'].upper())
        if value[i]['item_type'] =="movie":
            purchase.append(value[i]['purchase_info'])



    for i in range(len(z)):
        if z[i] == z[id]:
           if type[i] =="movie":
               comon.append(i)
    if len(comon) == 0:
        l=1;
    else:
        l=len(comon)

    for i in purchase:
        a=json.loads(i)
        pu.append(a)

    return render_template('info.html',image_url=x,id=id,image_title=z,description=d.split("#@"),di=di,ca=ca,ge=ge,src=src,com = comon,l=l,ref=refurl,pu=pu)


if __name__ == '__main__':
   app.run(debug = True)
