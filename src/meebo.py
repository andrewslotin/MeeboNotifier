'''
Created on 17.08.2010

@author: drone
'''

import json, urllib, urllib2

HOST = 'https://www.meebo.com/mcmd/'

class MeeboUser:
    username = None
    password = None
    network  = 'meebo'
    
    def __init__(self, login, password):
        self.username = login
        self.password = password

class MeeboAPI:
    __sessionKey = None
    __locationId = None
    __clientId   = None
    __cmdCounter = 0
    
    def __init__(self):
        pass
    
    def _call(self, action, data = {}, method = 'post'):
        method = method.lower()
        
        if action != 'start':
            if self.__sessionKey == None: self.startSession()
            data['sessionKey'] = self.__sessionKey
            data['locationId'] = self.__locationId
            data['locationId'] = self.__cmdCounter
            self.__cmdCounter += 1
        
        if method == 'get' and data:
            action += '?' + urllib.urlencode(data)
            data = {}
        
        data = data or None
        
        return urllib2.urlopen(HOST + action, data)
    
    def startSession(self):
        o = json.load(self._call('start'))
        self.__sessionKey = o['sessionKey']
        self.__locationId = o['locationId']
        self.__clientId   = o['clientId']
        self.__cmdCounter = 0
    
    def login(self, users, status = 'available'):
        if type(users) != list:
            users = [users]
        
        data = {
                'ssl':     True,
                'status':  status,
                'message': ''
                }
        
        i = 0
        for user in users:
            data.update({
                         'username%d' % i: user.username,
                         'password%d' % i: user.password,
                         'network%d'  % i: user.network
                         })
        
        return self._call('joinexisting', data)