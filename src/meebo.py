'''
Created on 17.08.2010

@author: drone
'''

import json, urllib, urllib2, time

HOST = 'https://www.meebo.com'

class MeeboUser:
    username = None
    password = None
    network  = 'meebo'
    status   = 'available'
    
    _api = None
    __retryCount = 0
    
    def __init__(self, login, password, status = 'available', api = None):
        self._api = api or MeeboAPI()
        self.username = login
        self.password = password
        self.status   = status
        self._api.login(self)
    
    def events(self):
        self.__retryCount += 1
        return self._api.events(self.__retryCount)

class MeeboAPI:
    __sessionKey = None
    __clientId   = None
    __ip         = None
    __gmt        = -time.timezone / 60
    __cmdCounter = 0
    
    def __init__(self):
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.__opener)
        
        self.__ip = self._call('getip', 'cmd')
    
    def _call(self, action, service = 'mcmd', data = {}, method = 'post'):
        method = method.lower()
        
        print '>> %s/%s' % (service, action)
        
        if action != 'start' and action != 'mstart':
            data['sessionKey'] = self.__sessionKey
            data['clientId']   = self.__clientId
            if action != 'events': data['num'] = 1
            data['gmt'] = self.__gmt
        
        if method == 'get' and data:
            action += '?' + urllib.urlencode(data)
            data = {}
        
        data = data and urllib.urlencode(data) or None
        
        print data
        
        req = urllib2.Request('/'.join([HOST, service, action]), data, {'User-Agent': 'MeeboNotifier', 'Host': 'www.meebo.com'})
        response = self.__opener.open(req)
        d = response.read()
        print d
        response.close()
        
        try:
            return json.loads(d)
        except ValueError:
            return d
    
    def _serializeUsers(self, users):
        data = {}
        
        if type(users) != list: users = [users]
        
        i = 0
        for user in users:
            data.update({
                         'state%d'    % i: user.status,
                         'username%d' % i: user.username,
                         'password%d' % i: user.password,
                         'protocol%d' % i: user.network,
                         'network%d'  % i: user.network
                         })
        
        return data 
    
    def startSession(self, users):
        data = {
                'type': 'trayicon',
                'allowIPChange': 'true',
                'ip': self.__ip,
                }
        data.update(self._serializeUsers(users))
        
        o = self._call(action = 'mstart', service = 'cmd', data = data)
        
        self.__sessionKey = o['sessionKey']
        self.__clientId   = o['clientId']
        self.__cmdCounter = 0
    
    def login(self, users):
        if self.__sessionKey == None:
            self.startSession(users)
        
        data = {'gprefs': 'true'}
        data.update(self._serializeUsers(users))
        
        return self._call(action = 'login', data = data)
    
    def events(self, ret):
        data = {'ret': ret}
        
        return self._call(action = 'events', data = data, method = 'get')

if __name__ == '__main__':
    try:
        u = MeeboUser(login = '', password = '')
        print u.events()
    except urllib2.HTTPError, e:
        print 'Fail (code %d)' % e.code