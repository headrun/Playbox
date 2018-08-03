from flask import Flask, request, render_template, jsonify
import requests
import json

app = Flask(__name__)
"""http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&item_type=movie"""
rn = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&id=B0049VZ222&item_type=season')
"""ra =requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&id=B0049VZ222&item_type=season')"""
"""rn = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=netflix&id=80173524')
    ra = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&id=B0747LHQYL')"""
"""rv = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=vudu&id=896126')"""
ri=requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=itunes&id=395373961&item_type=season')

value = rn.json()['results']+ri.json()['results']
r = requests.get('http://data.headrun.com/api/?dead_sort_by=True&format=json&is_valid=1&source_id=amazon&season_id=B0049VZ222&item_type=episode')
val = r.json()['results']
def result():
    return value
def epi():
    return val


@app.route('/movies/')
def movies():
    x=[]
    y=""
    z=[]
    comon=[]
    value = result()
    for i in range(len(value)):
        x.append(value[i]['image_url'])
        y+=" "+value[i]['url'][0:40]
        z.append(value[i]['title'])

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
    ide=[]
    xe=[]
    ze=[]
    snum=[]
    sid=[]
    etitle=[]
    etitlesp=[]
    xesp=[]
    senum=[]
    senumsp=[]
    rdate=[]
    rdatesp=[]
    snumsp=[]
    eurl=[]
    eurlsp=[]

    value = result()
    val=epi()

    for i in range(len(value)):
        if value[i]['image_url'] =="" :
            x.append(value[0]['image_url'])
        else:
            x.append(value[i]['image_url'])
        ide.append(value[i]['id'])
        z.append(value[i]['title'])
        refurl.append(value[i]['url'])
        type.append(value[i]['item_type'])
        ge.append(value[i]['genres'].replace('"',''))
        d+=""+value[i]['description']+"#@"
        di.append(value[i]['directors'].replace('"',''))
        if value[i]['cast'] =="" :
            ca.append("Details not avaialble")
        else:
            ca.append(value[i]['cast'].replace('"',''))
        src.append(value[i]['source_id'].upper())
        if value[i]['item_type'] =="movie":
            purchase.append(value[i]['purchase_info'])

    ip=ide[id]


    for i in range(len(val)):
        if val[i]['image_url'] =="" :
            xe.append(val[0]['image_url'])
        else:
            xe.append(val[i]['image_url'])
        ze.append(val[i]['title'])
        etitle.append(val[i]['episode_title'])
        snum.append(val[i]['season_number'])
        sid.append(val[i]['season_id'])
        senum.append(val[i]['episode_number'])
        rdate.append(val[i]['release_date'])
        eurl.append(val[i]['url'])



    for i in range(len(ze)):
        if z[id] == ze[i] :
            etitlesp.append(etitle[i])
            xesp.append(xe[i])
            senumsp.append(senum[i])
            snumsp.append(snum[i])
            rdatesp.append(rdate[i])
            eurlsp.append(eurl[i])

    senumsp.reverse()
    etitlesp.reverse()
    snumsp.reverse()
    rdatesp.reverse()
    xesp.reverse()
    eurlsp.reverse()

    for i in range(len(z)):
        if z[i] == z[id]:
           if type[i] =="season":
               comon.append(i)
    if len(comon) == 0:
        l=1;
    else:
        l=len(comon)

    for i in purchase:
        a=json.loads(i)
        pu.append(a)

    return render_template('inforsample.html',image_url=x,id=id,image_title=z,description=d.split("#@"),di=di,ca=ca,ge=ge,src=src,com = comon,l=l,ref=refurl,pu=pu,lp=len(val),et=etitlesp,xesp=xesp,en=senumsp,sn=snumsp,dt=rdatesp,eurl=eurlsp)


if __name__ == '__main__':
   app.run(debug = True)
