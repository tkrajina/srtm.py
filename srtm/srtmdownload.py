

import requests

# overriding requests.Session.rebuild_auth to mantain headers when redirected
class EarthDataSession(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)
 
   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return
 
  
 
# create session with the user credentials that will be used to authenticate access to the data
username = "ptolemytemp"
password= "Srtmpass1"
#session = EarthDataSession(username, password)
 
# the url of the file we wish to retrieve
#url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD17A3H.006/2009.01.01/MYD17A3H.A2009001.h12v05.006.2015198130546.hdf.xml"
url = "http://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11/N03E021.SRTMGL1.hgt.zip"
 
# extract the filename from the url to be used when saving the file
filename = url[url.rfind('/')+1:]  
 
try:
    # submit the request using the session
    response = EarthDataSession(username, password).get(url, stream=True)
    print(response.status_code)

    # raise an exception in case of http errors
    response.raise_for_status()  
 
    # save the file
    with open(filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024*1024):
            fd.write(chunk)
 
except requests.exceptions.HTTPError as e:
    # handle any errors here
    print(e)
