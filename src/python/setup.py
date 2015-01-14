import optparse
import urllib2
import time
import datetime

import os
import json
import httplib2

try:
    # Prefer lxml, if installed.
    from lxml import etree as ET
except ImportError:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        raise ImportError("No suitable ElementTree implementation was found.")


import traceback
import pysolr


def to_id(value, the_format='%Y_%m_%d_%H_%M_%S', the_input='%Y-%m-%d %H:%M:%S'):
    #2013-11-20T21:41:34.821Z
    return datetime.datetime.strptime(value, the_input).strftime(the_format)


# "2013-07-01 00:10:34"
def datetimeformatstr(value, the_format='%Y-%m-%dT%H:%M:%SZ', the_input='%Y-%m-%d %H:%M:%S'):
    #2013-11-20T21:41:34.821Z
    return datetime.datetime.strptime(value, the_input).strftime(the_format)


HTTP_CLIENT = httplib2.Http()

##
def get_env(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default

##
def parse_opts(args):
    data = {}
    for arg in args:
        key, val = arg.split('=', 1)

        # make a list out of any key specified more then once
        if key in data:
            oldval = data[key]
            if type(oldval) is list:
                oldval.append(val)
            else:
                data[key] = [oldval, val]
        else:
            data[key] = val
    return data


##
def json_http(url, method='GET', data=None):
    body = None;
    if (data): body = json.dumps(data)

    resp, content = HTTP_CLIENT.request(
        url, method=method, body=body,
        headers={'Content-Type':'application/json'})

    # fail if not status 2xx
    if 0 != str(resp.status).find('2'):
        err = content
        try:
            err = pretty_json(json.loads(content))
        except:
            # IGNORE, use the raw error instead
            pass
        raise Exception(method+' '+url+' => '+str(resp.status)+"\n"+err)

    if 204 == resp.status: return None
    if content:
        return json.loads(content)
    else:
        return None

##
def pretty_json(data, indent=''):
    pretty = json.dumps(data,indent=2)
    return pretty.replace("\n","\n"+indent)

##

def index(input_file):
    i = 0
    buffer = []
    for line in open(input_file):
        if line.startswith("\"tripduration"):
            continue
        if line.startswith("#") == False:
            vals = line.strip().split(",")
            id = to_id(vals[1].replace("\"", "")) +"_" + to_id(vals[2].replace("\"", "")) + "_" + vals[3].replace("\"", "") + vals[7].replace("\"", "")
            gender = vals[14].replace("\"", "")

            if gender == "0":
                gender = "NA"
            elif gender == "1":
                gender = "M"
            else: #2
                gender = "F"

            items = {"id": id,
                     "tripduration_i": vals[0].replace("\"", ""),
                     "starttime_dt": datetimeformatstr(vals[1].replace("\"", "")),
                     "stoptime_dt": datetimeformatstr(vals[2].replace("\"", "")),
                     "start_station_id_i": vals[3].replace("\"", ""),
                     "start_station_name": vals[4].replace("\"", ""),
                     "start_station_name_txt_en": vals[4].replace("\"", ""),
                     "start_station_location_p": vals[5].replace("\"", "") + "," + vals[6].replace("\"", ""),
                     "end_station_id_i": vals[7].replace("\"", ""),
                     "end_station_name": vals[8].replace("\"", ""),
                     "end_station_name_txt_en": vals[8].replace("\"", ""),#we could copy field this, but it is small so not a big deal
                     "end_station_location_p": vals[9].replace("\"", "") + "," + vals[10].replace("\"", ""),
                     "bikeid_i": vals[11].replace("\"", ""),
                     "user_type_s": vals[12].replace("\"", ""),
                     "birth_year_i": vals[13].replace("\"", "").replace("\\N", "-1"),
                     "gender_s": gender
            }
            buffer.append(items)
            i += 1
            if i % 10000 == 0:
                print "Indexing row: " + str(i)
                add(solr, buffer, id, commit=False)
                buffer = []
            #print items
    add(solr, buffer, None, commit=False)


def add(solr, docs, dsId, commit=True, boost=None, commitWithin="1000", waitFlush=None, waitSearcher=None):
    """
    Adds or updates documents.
    Requires ``docs``, which is a list of dictionaries. Each key is the
    field name and each value is the value to index.
    Optionally accepts ``commit``. Default is ``True``.
    Optionally accepts ``boost``. Default is ``None``.
    Optionally accepts ``commitWithin``. Default is ``None``.
    Optionally accepts ``waitFlush``. Default is ``None``.
    Optionally accepts ``waitSearcher``. Default is ``None``.
    Usage::
        solr.add([
                            {
                                "id": "doc_1",
                                "title": "A test document",
                            },
                            {
                                "id": "doc_2",
                                "title": "The Banana: Tasty or Dangerous?",
                            },
                        ])
    """
    start_time = time.time()
    #self.log.debug("Starting to build add request...")
    message = ET.Element('add')

    if commitWithin:
        message.set('commitWithin', commitWithin)

    for doc in docs:
        message.append(solr._build_doc(doc, boost=boost))

    # This returns a bytestring. Ugh.
    m = ET.tostring(message, encoding='utf-8')
    # Convert back to Unicode please.
    m = pysolr.force_unicode(m)
    #print "Indexing to: " + dsId
    end_time = time.time()
    #self.log.debug("Built add request of %s docs in %0.2f seconds.", len(message), end_time - start_time)
    return update(solr, m, dsId, commit=commit, waitFlush=waitFlush, waitSearcher=waitSearcher)


def update(solr, message, dsId, clean_ctrl_chars=True, commit=True, waitFlush=None, waitSearcher=None):
    """
    Posts the given xml message to http://<self.url>/update and
    returns the result.

    Passing `sanitize` as False will prevent the message from being cleaned
    of control characters (default True). This is done by default because
    these characters would cause Solr to fail to parse the XML. Only pass
    False if you're positive your data is clean.
    """
    path = 'update/'

    # Per http://wiki.apache.org/solr/UpdateXmlMessages, we can append a
    # ``commit=true`` to the URL and have the commit happen without a
    # second request.
    query_vars = []

    if commit is not None:
        query_vars.append('commit=%s' % str(bool(commit)).lower())

    if waitFlush is not None:
        query_vars.append('waitFlush=%s' % str(bool(waitFlush)).lower())

    if waitSearcher is not None:
        query_vars.append('waitSearcher=%s' % str(bool(waitSearcher)).lower())
    if dsId is not None:
        query_vars.append("lucidworks_fields=true")
        #query_vars.append("fm.ds=" + dsId)
    if query_vars:
        path = '%s?%s' % (path, '&'.join(query_vars))

    # Clean the message of ctrl characters.
    if clean_ctrl_chars:
        message = pysolr.sanitize(message)

    return solr._send_request('post', path, message, {'Content-type': 'text/xml; charset=utf-8'})



p = optparse.OptionParser()
p.add_option("-i", "--input", action="store", dest="input")
p.add_option("--api_host", action="store", dest="host", default="localhost")
p.add_option("--api_port", action="store", dest="api_port", default="8983")
p.add_option("-l", "--collection", action="store", dest="collection", default="citi") #name the collection

opts, args = p.parse_args()


COLLECTION = opts.collection
LWS_URL = "http://" + opts.host + ":" + opts.api_port
SOLR_URL = LWS_URL + "/solr/" + COLLECTION


solr = pysolr.Solr(SOLR_URL, timeout=10)
index(opts.input)
