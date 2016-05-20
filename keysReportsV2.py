import requests, json, hashlib, time, urllib, masheryDate
# import masheryV2, masheryDate, urllib

apiHost = 'https://api.mashery.com'

def get(siteId, apikey, secret, resource, params):
    resourceEndpoint = '/v2/rest'
    url = apiHost + resourceEndpoint + '/' + siteId + resource + '?apikey=' + apikey + '&sig=' + hash(apikey, secret) + params

 #   print "Url in get reports is " + url
    response = requests.get(url)
    if (response.status_code == 200):
        return response.json()
    else:
        print response
        return None

def hash(apikey, secret):
    authHash = hashlib.md5();
    temp = str.encode(apikey + secret + repr(int(time.time())))
    authHash.update(temp)
    return authHash.hexdigest()

def activityByService(siteId, apikey, secret, startDate, endDate, serviceId):

#    print "in activityByService"
    apiHost = 'https://api.mashery.com'

    dates = masheryDate.daysToReportOn(startDate, endDate)

    results = []

    urlParams = '&start_date={startDate}&end_date={endDate}&format=json&limit=1000'.format(startDate= startDate, endDate= endDate)

#    print "Dates: " + str(dates)
    for date in dates:
        urlParams = '&start_date=' + urllib.quote_plus(date[0]) + '&end_date=' + urllib.quote_plus(date[1]) + '&format=json&limit=1000'

#        print "url is: " + str('/reports/calls/developer_activity/service/{serviceId}'.format(serviceId= serviceId))
#        print urlParams
        
        try:
          results.extend(get(siteId, apikey, secret, '/reports/calls/developer_activity/service/{serviceId}'.format(serviceId= serviceId), urlParams))

        except TypeError:
          print "TypeError was caught"
          pass

#    print results
#    print "end of activityByService"
    return results