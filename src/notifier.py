'''
Created on 17.08.2010

@author: drone
'''

from meebo import MeeboAPI, MeeboUser

if __name__ == '__main__':
    u = MeeboUser('', '')
    api = MeeboAPI()
    for line in api.login(u):
        print line