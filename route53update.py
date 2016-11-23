import time
try:
    import route53
except:
    raise Exception("requires route53: (pip install route53, or git clone https://github.com/gtaylor/python-route53.git)")
try: 
    import secrets
except:
    raise Exception("create a secrets.py file with AWS_CREDS")
    # should be of form:
    # AWS_CREDS={ 'aws_access_key_id':'...',
    #             'aws_secret_access_key':'...'}
import urllib2
import json
DEBUG = False

def get_my_ip(IP_SERVERS=(('http://aislynn.net/ip.cgi', 'ip'), ('http://jsonip.com','ip'),('http://ip-api.com/json','query'),('http://api.ipify.org/?format=json','ip'),('http://wtfismyip.com/json',"YourFuckingIPAddress"))):
    for retries in xrange(4,0,-1):
        for url,attr in IP_SERVERS:
            try:
                if DEBUG: print "TRY", url                    
                httpResponse = urllib2.urlopen(urllib2.Request(url), timeout=5).read()
                break
            except:
                if DEBUG: print "RETRY", url
                time.sleep(0.50)
                continue
        if httpResponse is not None:
            break
    if httpResponse is None:
        raise Exception("could not find IP address from any server")
    jsonData = json.loads(httpResponse)
    current_ip = jsonData[attr]
    return current_ip
    

def find_host_byname(host, typ="A"):
    rs = []
    conn = route53.connect(**secrets.AWS_CREDS)
    for zone in conn.list_hosted_zones():
        for record_set in zone.record_sets:
            if (record_set.rrset_type == typ and
                record_set.name == host+"."):
                 rs.append(record_set)
    return rs
    
def update_host(host, new_ip):
    rs = find_host_byname(host)
    if len(rs) != 1:
        raise Exception("no unique record found",rs)
    rs = rs[0]
    if len(rs.records) != 1:
        raise Exception("not a single IP A rec",rs.records)
    if rs.records[0] != new_ip:
        print "Updated IP:",host,new_ip
        rs.records = (new_ip,)
        rs.save()
    else:
        print "No update necessary"

if __name__ == '__main__':
    import sys
    update_host(sys.argv[1],get_my_ip())
