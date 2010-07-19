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
import time
import base64

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
    def __init__(self, user='admin', pwd='admin', dbname='openerp', host='localhost', debug=False):
        self.user = user       # default: 'admin'
        self.pwd = pwd         # default: 'admin'
        self.dbname = dbname   # default: 'openerp'
        self.host = host
        self.debug = debug
        self.commonsock = None
        self.objectsock = None
        self.reportsock = None
        self.uid = None
        self.models = {}
        self.connect()
        self.load_models()

    def connect(self):
        """login and sockets to xmlrpc services: common, object and report"""
        self.uid = self.login(self.dbname, self.user, self.pwd)
        self.objectsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/object' % self.host)
        self.reportsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/report' % self.host)
    
    def login(self, dbname, user, pwd):
        self.commonsock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/common' % self.host)
        return self.commonsock.login(dbname, user, pwd)
        
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

    def report(self, model, ref, report_type='pdf'):
        """ return a report """
        # TODO: test this function
        data = {'model': model, 'id': ref[0], 'report_type': report_type}
        id_report = self.reportsock.report(dbname, uid, pwd, model, ref, data)
        time.sleep(5)
        state = False
        attempt = 0
        while not state:
            report = self.reportsock.report_get(dbname, uid, pwd, id_report)
            state = report['state']
            if not state:
                time.sleep(1)
            attempt += 1
            if attempt > 200:
                print 'Printing aborted, too long delay!'
                break
        
        if report_type == 'pdf':
            string_pdf = base64.decodestring()
            return string_pdf
        else:
            return report['result']

class Manager:
    def __init__(self, model, ooop):
        self.model = model
        self.ooop = ooop
        self.INSTANCES = {}

    def get(self, ref): # TODO: only ids?
        instance = Data(self.model, self, ref)
        self.INSTANCES['%s:%s' % (self.model, ref)] = instance
        return instance

    def new(self):
        return Data(self.model, self)
        
    def copy(self, ref):
        instance = Data(self.model, self, ref, copy=True)
        self.INSTANCES['%s:%s' % (self.model, ref)] = instance
        return instance

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
    def __init__(self, model, manager, ref=None, copy=False):
        self.model = model # model name # FIXME!
        self.__manager = manager
        self.__ooop = manager.ooop
        self.__copy = copy
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
            self.__dict__[name] = False # TODO: I prefer None here...


    def get_values(self):
        """ put values into object using field names like attributes """
        data = self.__ooop.read(self.model, self.__ref)
        self.__data = data # FIXME: only for debugging purposes
        for name,ttype,relation in ((i['name'],i['ttype'],i['relation']) for i in self.fields.values()):
            if ttype == 'many2one':
                if data[name]: # TODO: review this
                    self.__dict__['__%s' % name] = data[name]
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
            elif ttype in ('one2many', 'many2many'):
                if data[name]:
                    self.__dict__['__%s' % name] = data[name]
                    self.__dict__[name] = []
                    for i in xrange(len(data[name])):
                        if self.__manager.INSTANCES.has_key('%s:%i' % (relation, data[name][i])):
                            self.__dict__[name].append(self.__manager.INSTANCES['%s:%s' % (relation, data[name][i])])
                        else:
                            # TODO: use a Manager instance, not Data
                            instance = Data(relation, self.__manager, data[name][i])
                            self.__dict__[name].append(instance)
                            self.__manager.INSTANCES['%s:%s' % (relation, data[name][i])] = instance
                else:
                    self.__dict__[name] = None
            else:
                self.__dict__[name] = data[name]
    
    def save(self):
        """ save attributes object data into openerp """
        data = {}
        for name,ttype,relation in ((i['name'],i['ttype'],i['relation']) for i in self.fields.values()):
            if not '2' in ttype:
                if ttype == 'boolean' or self.__dict__[name]: # many2one, one2many, many2many
                    data[name] = self.__dict__[name]
            elif ttype in ('one2many', 'many2many'): # TODO: to ckeck all possible cases
                if self.__dict__[name]:
                    data[name] = [(6, 0, [i.__ref for i in self.__dict__[name]])]
                    # update __name and INSTANCES (cache)
                    self.__dict__['__%s' % name] = [i.__ref for i in self.__dict__[name]] # REVIEW: two loops?
                    for i in self.__dict__[name]:
                        self.__manager.INSTANCES['%s:%s' % (relation, i.__ref)] = i
            elif ttype == 'many2one':
                if self.__dict__[name]:
                    data[name] = self.__dict__[name].__ref
                    # update __name and INSTANCES (cache)
                    self.__dict__['__%s' % name] = [self.__dict__[name].__ref, self.__dict__[name].name]
                    self.__manager.INSTANCES['%s:%s' % (relation, self.__dict__[name].__ref)] = self.__dict__[name]

        if self.__ooop.debug:
            print ">>> data: ", data

        # create or write the object
        if self.__ref > 0 and not self.__copy: # same object
            self.__ooop.write(self.model, self.__ref, data)
        else:
            self.__ref = self.__ooop.create(self.model, data)
        
        # update cache
        self.__manager.INSTANCES['%s:%s' % (self.model, self.__ref)] = self
            
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
            return u'<%s:%s %r> data instance' % (self.model, self.__ref, self.name)
        except:
            return u'<%s:%s> data instance' % (self.model, self.__ref)
