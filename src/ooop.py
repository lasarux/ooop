# -*- encoding: utf-8 -*-
########################################################################
#
#   OOOP, OpenObject On Python
#   Copyright (C) 2010 Pedro A. Gracia Fajardo. All Rights Reserved.
#   $Id$
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

import xmlrpclib

OOOPMODELS = 'ir.model'
OOOPFIELDS = '%s.fields' % OOOPMODELS
OPERATORS = {
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
    'ne': '!=',
    'like': 'like',
    'ilike': 'ilike',
}

class OOOP:
    """ Main class to manage xml-rpc comunitacion with openerp-server """
    def __init__(self, user='admin', pwd='admin', dbname='openerp', host='localhost'):
        self.user = user       # default: 'admin'
        self.pwd = pwd         # default: 'admin'
        self.dbname = dbname   # default: 'openerp'
        self.host = host
        self.commonsock = None
        self.objectsock = None
        self.printsock = None
        self.uid = None
        self.models = {}
        self.connect()
        self.load_models()

    def connect(self):
        """login and sockets to xmlrpc services: common, object and report"""
        self.commonsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/common' % self.host)
        self.uid = self.commonsock.login(self.dbname, self.user, self.pwd)
        self.objectsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/object' % self.host)
        self.printsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/report' % self.host)
        
    def create(self, model, data):
        """ create a new register """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'create', data)
        
    def unlink(self, model, ids):
        """ remove register """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'unlink', ids)

    def write(self, model, ids, value):
        """ update register """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'write', ids, value)

    def read(self, model, ids, fields=[]):
        """ update register """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', ids, fields)

    def read_all(self, model, fields=[]):
        """ update register """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', self.all(model), fields)

    def search(self, model, query):
        """ return ids that match with 'query' """
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'search', query)

    def all(self, model):
        """ return all ids """
        return self.search(model, [])

    def insert_items(self, model, data):
        """ insert items into database """
        for item in data:
            d = {'name': item}
            query = [('name', '=', item)]
            if not self.search(model, query): # check if it's already present
                self.create(model, d)
            else:
                print 'Warning: %s already in %s model: %s' % (item, model)

    def load_models(self):
        models = self.read_all(OOOPMODELS)
        for model in models:
            self.models[model['model']] = model
            self.__dict__[model['model'].replace('.', '_')] = Manager(model['model'], self)
        

class Manager:
    def __init__(self, model, ooop):
        self.model = model
        self.ooop = ooop
        self.INSTANCES = {}

    def get(self, id): # TODO: only ids?
        return Data(self.model, self, id)

    def new(self):
        return Data(self.model, self)

    def all(self):
        r = []
        for i in self.ooop.all(self.model):
            r.append(self.get(i))
        return r

    def filter(self, *args, **kargs):
        q = [] # query dict
        for key, value in kargs.items():
            if not '__' in key:
                op = '='
            else:
                i = key.find('__')
                op = OPERATORS[key[i+2:]]
                key = key[:i]
            q.append(('%s' % key, op, '%s' % value))
                    
        r = []
        for i in self.ooop.search(self.model, q):
            r.append(self.get(i))
        return r

    def exclude(self, *args, **kargs):
        pass # TODO


class Data:
    def __init__(self, model, manager, ref=None):
        self.model = model # model name # FIXME!
        self.__manager = manager
        self.__ooop = manager.ooop
        if ref:
            self.__ref = ref
        else:
            self.__ref = -id(self)
        
        self.__manager.INSTANCES['%s:%s' % (model, ref)] = self

        # dict fields # TODO: to use correct manager to get fields
        q = [('model','=',model)]
        model_id = self.__ooop.search(OOOPMODELS, q)
        model = self.__ooop.read(OOOPMODELS, model_id)[0]
        fields = self.__ooop.read(OOOPFIELDS, model['field_id'])
        self.fields = {}
        for field in fields:
            self.fields[field['name']] = field
        
        # get current data for this object
        if ref:
            self.get_values()
        else:
            self.init_values()

        
    def init_values(self):
        """ initial values for object """
        for name,ttype,relation in ((i['name'],i['ttype'],i['relation']) for i in self.fields.values()):
            self.__dict__[name] = None


    def get_values(self):
        """ put values into object using field names like attributes """
        data = self.__ooop.read(self.model, self.__ref)
        for name,ttype,relation in ((i['name'],i['ttype'],i['relation']) for i in self.fields.values()):
            if ttype == 'one2many' or ttype == 'many2one':
                if data[name]: # TODO: review this
                    if self.__manager.INSTANCES.has_key('%s:%i' % (relation, data[name][0])):
                        #print "***", self.model, name, ttype, relation
                        self.__dict__[name] = self.__manager.INSTANCES['%s:%s' % (relation, data[name][0])]
                    else:
                        # TODO: use a Manager instance, not Data
                        instance = Data(relation, self.__manager, data[name][0])
                        self.__dict__[name] = instance
                        self.__manager.INSTANCES['%s:%s' % (relation, data[name][0])] = instance
                else:
                    self.__dict__[name] = None # TODO: empty openerp data object
            else:
                self.__dict__[name] = data[name]
            
    def save(self):
        """ save attributes object data into openerp """
        data = {}
        for name,ttype,relation in ((i['name'],i['ttype'],i['relation']) for i in self.fields.values()):
            if not '2' in ttype and self.__dict__[name]: # one2one, many2one, one2many, many2many
                data[name] = self.__dict__[name]
            elif ttype == 'many2many': # TODO: to ckeck all possible cases
                if self.__dict__[name]:
                    data[name] = [(6, 0, self.__dict__[name])]
            #elif ttype == 'many2one' or ttype == 'one2many':
            #    if self.__dict__[name]: # REVIEW: to search save method ???
            #        self.__dict__[name].save()
        if self.__ref < 0: # new object
            self.__ooop.write(self.model, self.__ref, data)
        else:
            self.__ref = self.__ooop.create(self.model, data)
            
    def delete(self):
        if self.__ref > 0:
            self.__ooop.unlink(self.model, self.__ref)
        else:
            pass # TODO


    # TODO: to develop a more clever save function
    def save_all(self): 
        """ save related instances """
        for i in self.__manager.INSTANCES.values():
            i.save()

    def __repr__(self):
        """ default representation: <model:id> """
        try:
            return '<%s:%s "%s"> data instance' % (self.model, self.__ref, self.name)
        except:
            return '<%s:%s> data instance' % (self.model, self.__ref)
