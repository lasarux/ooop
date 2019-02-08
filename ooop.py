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

try:
    import xmlrpclib
except:
    import xmlrpc.client as xmlrpclib
import time
import base64
import logging
from datetime import datetime, date

__author__ = "Pedro Gracia <pedro.gracia@impulzia.com>"
__license__ = "GPLv3+"
__version__ = "0.2.4"

logger = logging.getLogger(__name__)

OOOPMODELS = 'ir.model'
OOOPFIELDS = '%s.fields' % OOOPMODELS
OPERATORS = {
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
    'ne': '!=',
    'ne': '<>',
    'like': 'like',
    'ilike': 'ilike',
    'eq_like': '=like',
    'not_like': 'not like',
    'not_ilike':'not ilike',
    'in': 'in',
    'not_in': 'not in',
    'child_of': 'child of',
}

def remove(object):
    del object

# http://stackoverflow.com/questions/1305532/convert-python-dict-to-object (last one)
class dict2obj(dict):
    def __init__(self, dict_):
        super(dict2obj, self).__init__(dict_)
        for key in self:
            item = self[key]
            if isinstance(item, list):
                for idx, it in enumerate(item):
                    if isinstance(it, dict):
                        item[idx] = dict2obj(it)
            elif isinstance(item, dict):
                self[key] = dict2obj(item)

    def __getattr__(self, key):
        return self[key]


class OOOP:
    """ Main class to manage xml-rpc communication with odoo server """
    def __init__(self, user='admin', pwd='admin', dbname='odoo',
                 uri='http://localhost', port=8069, debug=False,
                 exe=False, active=True, readonly=False, **kwargs):
        self.user = user       # default: 'admin'
        self.pwd = pwd         # default: 'admin'
        self.dbname = dbname   # default: 'odoo'
        self.uri = uri
        self.port = port
        self.debug = debug
        self.exe = exe
        self.active = active
        self.commonsock = None
        self.objectsock = None
        self.reportsock = None
        self.uid = None
        self.models = {}
        self.fields = {}
        self.readonly = readonly

        self.connect()
        self.load_models()

    def connect(self):
        """login and sockets to xmlrpc services: common, object and report"""
        self.uid = self.login(self.dbname, self.user, self.pwd)
        self.objectsock = xmlrpclib.ServerProxy('%s:%i/xmlrpc/object' % (self.uri, self.port))
        self.reportsock = xmlrpclib.ServerProxy('%s:%i/xmlrpc/report' % (self.uri, self.port))

    def login(self, dbname, user, pwd):
        self.commonsock = xmlrpclib.ServerProxy('%s:%i/xmlrpc/common' % (self.uri, self.port))
        return self.commonsock.login(dbname, user, pwd)

    def execute(self, model, *args):
        if self.debug:
            logger.debug("[execute]: %s %s " % (model, args))
        if self.readonly:
            raise Exception('readonly connection')
        else:
            return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, *args)

    def create(self, model, data):
        """ create a new register """
        if self.debug:
            logger.debug("[create]: %s %s" % (model, data))
        if self.readonly:
            raise Exception('readonly connection')
        else:
            return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'create', data)

    def unlink(self, model, ids):
        """ remove register """
        if self.debug:
            logger.debug("[unlink]: %s %s" % (model, ids))
        if self.readonly:
            raise Exception('readonly connection')
        else:
            return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'unlink', ids)

    def write(self, model, ids, value):
        """ update register """
        if self.debug:
            logger.debug("[write]: %s %s %s" % (model, ids, value))
        if self.readonly:
            raise Exception('readonly connection')
        else:
            return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'write', ids, value)

    def read(self, model, ids, fields=[]):
        """ update register """
        if self.debug:
            logger.debug("[read]: %s %s %s" % (model, ids, fields))
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', ids, fields)

    def read_all(self, model, fields=[]):
        """ update register """
        if self.debug:
            logger.debug("[read_all]: %s %s" % (model, fields))
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', self.all(model), fields)

    def search(self, model, query):
        """ return ids that match with 'query' """
        if self.debug:
            logger.debug("[search]: %s %s" % (model, query))
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'search', query)

    # TODO: verify if remove this
    def custom_execute(self, model, ids, remote_method, data):
        if self.debug:
            logger.debug("DEBUG [custom_execute]: %s %s %s %s %s %s %s", self.dbname, self.uid, self.pwd, model, ids, remote_method, data)
        if self.readonly:
            raise Exception('readonly connection')
        else:
            return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, ids, remote_method, data)

    def all(self, model, query=[]):
        """ return all ids """
        if self.debug:
            logger.debug("[all]: %s %s" % (model, query))
        return self.search(model, query)

    def insert_items(self, model, data):
        """ insert items into database """
        for item in data:
            d = {'name': item}
            query = [('name', '=', item)]
            if not self.search(model, query): # check if it's already present
                self.create(model, d)
            else:
                logger.debug('Warning: %s already in %s model: %s' % (item, model, query))

    def load_models(self):
        models = self.read_all(OOOPMODELS)
        for model in models:
            self.models[model['model']] = model
            self.__dict__[self.normalize_model_name(model['model'])] = Manager(model['model'], self)

    def set_model(self, model, r={}, deep=None):
        """docstring for set_model"""
        if not model in r.keys():
            r[model] = {
                'name': self.normalize_model_name(model),
                'links': {},
                'fields': [] #TODO: storage i?
            }
            flds = self.read(OOOPFIELDS, self.models[model]['field_id'])
            for fld in flds:
                r[model]['fields'].append((fld["name"], fld["ttype"]))
                if fld["ttype"] in ('one2many', 'many2one', 'many2many'):
                    if deep > 0 and not r[model]['links'].has_key(fld['relation']):
                        r[model]['links'][fld['relation']] = fld['ttype']
                        r = self.set_model(fld["relation"], r, deep-1)

        return r

    def normalize_model_name(self, name):
        return "".join(["%s" % k.capitalize() for k in name.split('.')])

    def report(self, model, ref, report_type='pdf'):
        """ return a report """
        # TODO: test this function
        data = {'model': model, 'id': ref[0], 'report_type': report_type}
        id_report = self.reportsock.report(self.dbname, self.uid, self.pwd, model, ref, data)
        time.sleep(5)
        state = False
        attempt = 0
        while not state:
            report = self.reportsock.report_get(self.dbname, self.uid, self.pwd, id_report)
            state = report['state']
            if not state:
                time.sleep(1)
            attempt += 1
            if attempt > 200:
                logger.debug('Printing aborted, delay too long!')
                break

        if report_type == 'pdf':
            string_pdf = base64.decodestring(report['result'])
            return string_pdf
        else:
            return report['result']

# reference: http://www.java2s.com/Code/Python/Class/MyListinitaddmulgetitemlengetslice.htm
class List:
    """ An 'smart' list """
    #FIXME: reorder args
    #TODO: cache
    def __init__(self, manager, objects=None, parent=None,
                 low=None, high=None, data=None, model=None):
        self.manager = manager  # List or Manager instance
        if model:
            self.model = model
        else:
            self.model = self.manager._model
        if not objects:
            self.objects = []
        else:
            self.objects = objects
        self.parent = parent      # List instance
        self.low = low
        self.high = high
        self.data = data
        self.index = -1

    # python 3.x
    def __next__(self):
        self.index += 1
        if self.index == len(self.objects):
            self.index = -1
            raise StopIteration
        return self.__getitem__(self.index)
    
    # python 2.7.x
    def next(self):
        return self.__next__()

    # see next
    def __iter__(self):
        return self

    def delete(self):
        if self.parent:
            objects = self.parent.objects
            self.parent.objects = objects[:self.low] + objects[self.high:]
        return self.manager._ooop.unlink(self.model, self.objects)

    def append(self, value):
        if self.data:
            self.data.INSTANCES['%s:%s' % (self.model, value._ref)] = value
        self.objects.append(value)

    def __getslice__(self, low, high):
        return List(self.manager, self.objects[low:high], self, low, high, data=self.data, model=self.model)

    def __getitem__(self, offset):
        if not isinstance(self.objects[offset], int):
            return self.objects[offset]
        else:
            #if type(data) != Types.StringType: # data != model
            #    self.data.INSTANCES['%s:%s' % (self.data.model, self.objects[offset])] = instance # TODO: method to add instances
            self.objects[offset] = Data(self.manager, self.objects[offset], model=self.model)
            return self.objects[offset]

    def __len__(self):
        return len(self.objects)

    def __repr__(self):
        return '<Objects from %s> %i elements' % (self.model, len(self.objects))


class Manager:
    def __init__(self, model, ooop):
        self._model = model
        self._ooop = ooop

    def __getattr__(self, name):
        return lambda *a: self._ooop.execute(self._model, name, *a)

    def get(self, ref): # TODO: only ids?
        return Data(self, ref)

    def new(self, *args, **kargs):
        return Data(self, *args, **kargs)

    def copy(self, ref):
        return Data(self, ref, copy=True)

    def read(self, ids, fields=[]):
        data = self._ooop.read(self._model, ids, fields)
        res = []
        for item in data:
            row = {'id': item['id']}
            for i in fields:
                row[i] = item[i]
            res.append(dict2obj(row))
        return res

    def all(self, fields=[], offset=0, limit=999999, as_list=False):
        ids = self._ooop.all(self._model)
        if not ids: # TODO: check this
            return []
        data = self._ooop.read(self._model, ids[offset:limit], fields)
        if as_list:
            res = []
            for item in data:
                row = {'id': item['id']}
                for i in fields:
                    row[i] = item[i]
                res.append(dict2obj(row))
            return res
        return List(self, ids) #manager, object ids

    def filter(self, fields=[], as_list=False, **kargs):
        q = [] # query dict
        for key, value in kargs.items():
            if not '__' in key:
                op = '='
            else:
                i = key.find('__')
                op = OPERATORS[key[i+2:]]
                key = key[:i]
            q.append(('%s' % key, op, value))
        ids = self._ooop.search(self._model, q)
        if as_list:
            return self.read(ids, fields)
        return List(self, ids)

    def exclude(self, *args, **kargs):
        pass # TODO

    def __repr__(self):
        return '<%s> manager instance' % self._model


class Data(object):
    def __init__(self, manager, ref=None, model=None, copy=False, data=None, fields=[], *args, **kargs):
        if not model:
            self._model = manager._model # model name # FIXME!
        else:
            self._model = model
        self._manager = manager
        self._ooop = self._manager._ooop
        self._copy = copy
        self._data = data
        self._fields = fields
        self.INSTANCES = {}
        if ref:
            self._ref = ref
        else:
            self._ref = -id(self)

        self.INSTANCES['%s:%s' % (self._model, self._ref)] = self

        if self._model in self._ooop.fields.keys():
            self.fields = self._ooop.fields[self._model]
        else:
            fields = self._manager.fields_get()
            self.fields = {}
            for field_name, field in fields.items():
                field['name'] = field_name
                field['relation'] = field.get('relation', False)
                field['ttype'] = field['type']
                del field['type']
                self.fields[field_name] = field
            self._ooop.fields[self._model] = self.fields

        # get current data for this object
        if ref:
            self.get_values()
        else:
            # get default values
            default_values = {}
            field_names = self.fields.keys()
            default_values = self._manager.default_get(field_names)
            # convert DateTime instance to datetime.datetime object
            for i in default_values:
                if self.fields[i]['ttype'] == 'datetime':
                    t = default_values[i].timetuple()
                    default_values[i] = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            # active by default ?
            if self._ooop.active:
                default_values['active'] = True
            default_values.update(**kargs) # initial values from caller
            self.init_values(**default_values)
            if self._ooop.debug:
                logger.debug("default values: %s" % default_values)

    def init_values(self, *args, **kargs):
        """ initial values for object """
        keys = kargs.keys()
        for i in self.fields.values():
            name, ttype, relation = i['name'], i['ttype'], i['relation']
            if ttype in ('one2many', 'many2many'): # these types use a list of objects
                if name in keys:
                    self.__dict__[name] = List(Manager(relation, self._ooop), kargs[name], data=self, model=relation)
                else:
                    self.__dict__[name] = List(Manager(relation, self._ooop), data=self, model=relation)
            elif ttype == 'many2one':
                if name in keys and kargs[name]:
                    # manager, ref=None, model=None, copy=False
                    instance = Data(Manager(relation, self._ooop), kargs[name], relation)
                    self.INSTANCES['%s:%s' % (relation, kargs[name])] = instance
                    self.__dict__[name] = instance
                else:
                    self.__dict__[name] = None
            else:
                if name in keys:
                    self.__dict__[name] = kargs[name]
                else:
                    self.__dict__[name] = False # TODO: I prefer None here...

    def get_values(self):
        """ get values of fields with no relations """
        if not self._data:
            data = self._ooop.read(self._model, self._ref, self._fields)
            if not data:
                raise AttributeError('Object %s(%i) doesn\'t exist.' % (self._model, self._ref))
            else:
                self._data = data

        for i in self.fields.values():
            name, ttype, relation = i['name'], i['ttype'], i['relation']
            if not ttype in ('one2many', 'many2one', 'many2many'):
                hasattr(self,name) # use __getattr__ to trigger load
            else:
                pass # TODO: to load related fields as proxies to objects

    def __print__(self, sort=True):
        if sort:
            fields = sorted(self.fields)
        else:
            fields = self.fields
        for i in fields:
            logger.debug("%s: %s" % (i, self.__getattr__(i)))

    def __setattr__(self, field, value):
        if 'fields' in self.__dict__:
            if field in self.fields.keys():
                ttype = self.fields[field]['ttype']
                if value:
                    if ttype =='many2one':
                        if type(value) is int:
                            self.INSTANCES['%s:%s' % (self._model, value)] = value
                        else:
                            self.INSTANCES['%s:%s' % (self._model, value._ref)] = value
        self.__dict__[field] = value

    def __getattr__(self, field):
        """ put values into object dynamically """
        if field in self.__dict__.keys():
            return self.__dict__[field]

        try:
            data = {field: self._data[field]}
        except:
            if field in self.fields.keys():
                data = self._ooop.read(self._model, self._ref, [field])
            # Try a custom function
            if self._ooop.exe:
                return lambda *a: self._ooop.execute(
                    self._model, field, [self._ref], *a)
        try:
            name = self.fields[field]['name']
        except:
            raise NameError('field \'%s\' is not defined' % field)
        ttype = self.fields[field]['ttype']
        relation = self.fields[field]['relation']
        if ttype == 'many2one':
            if name in data: # TODO: review this
                self.__dict__['__%s' % name] = data[name]
                key = '%s:%i' % (relation, data[name][0])
                if key in self.INSTANCES.keys():
                    self.__dict__[name] = self.INSTANCES[key]
                else:
                    # TODO: use a Manager instance, not Data
                    instance = Data(Manager(relation, self._ooop),
                                    data[name][0], relation, data=self)
                    self.__dict__[name] = instance
                    self.INSTANCES[key] = instance
            else:
                self.__dict__[name] = None # TODO: empty odoo data object
        elif ttype in ('one2many', 'many2many'):
            if data[name]:
                self.__dict__['__%s' % name] = data[name]
                self.__dict__[name] = List(Manager(relation, self._ooop),
                                           data=self, model=relation)
                for i in range(len(data[name])):
                    key = '%s:%i' % (relation, data[name][i])
                    if key in self.INSTANCES.keys():
                        self.__dict__[name].append(self.INSTANCES['%s:%s' % (relation, data[name][i])])
                    else:
                        # TODO: use a Manager instance, not Data
                        instance = Data(Manager(relation, self._ooop),
                                        data[name][i], data=self,
                                        model=relation)
                        self.__dict__[name].append(instance)
                        #self.INSTANCES['%s:%s' % (relation, data[name][i])] = instance
            else:
                self.__dict__[name] = List(Manager(relation, self._ooop),
                                           data=self, model=relation)
        elif ttype == "datetime" and name in data:
            p1, p2 = data[name].split(".", 1)
            d1 = datetime.strptime(p1, "%Y-%m-%d %H:%M:%S")
            ms = int(p2.ljust(6,'0')[:6])
            d1.replace(microsecond=ms)
            self.__dict__[name] = d1
        elif ttype == "date" and name in data:
            self.__dict__[name] = date.fromordinal(datetime.strptime(data[name], "%Y-%m-%d").toordinal())
        else:
            # axelor conector workaround
            if isinstance(data, list):
                data = data[0]
            self.__dict__[name] = data[name]

        if self.__dict__[name]:
            return self.__dict__[name]

    def save(self):
        """ save attributes object data into odoo
            return: object id """

        data = {}
        for i in self.fields.values():
            name, ttype, relation = i['name'], i['ttype'], i['relation']
            if name in self.__dict__.keys(): # else keep values in original object
                if not '2' in ttype: # not one2many, many2one nor many2many
                    if ttype == 'date' and self.__dict__[name]:
                        #print name, ttype, relation
                        #print self.__dict__[name]
                        data[name] = date.strftime(self.__dict__[name], '%Y-%m-%d')
                    elif ttype == 'datetime' and self.__dict__[name]:
                        data[name] = datetime.strftime(self.__dict__[name], '%Y-%m-%d %H:%M:%S')
                    elif ttype in ('boolean', 'float', 'integer') or self.__dict__[name]:
                        data[name] = self.__dict__[name]
                elif ttype in ('one2many', 'many2many'):
                    if len(self.__dict__[name]) > 0:
                        data[name] = [(6, 0, [i.save() for i in self.__dict__[name]])]
                        # update __name and INSTANCES (cache)
                        self.__dict__['__%s' % name] = [i._ref for i in self.__dict__[name]] # REVIEW: two loops?
                        for i in self.__dict__[name]:
                            self.INSTANCES['%s:%s' % (relation, i._ref)] = i
                elif ttype == 'many2one':
                    if self.__dict__[name]:
                        if type(self.__dict__[name]) is int:
                            data[name] = self.__dict__[name]
                            # update __name and INSTANCES (cache)
                            self.__dict__['__%s' % name] = [self.__dict__[name], self.__dict__[name]]
                            self.INSTANCES['%s:%s' % (relation, self.__dict__[name])] = self.__dict__[name]
                        else:
                            data[name] = self.__dict__[name]._ref
                            # update __name and INSTANCES (cache)
                            self.__dict__['__%s' % name] = [self.__dict__[name]._ref, self.__dict__[name].name]
                            self.INSTANCES['%s:%s' % (relation, self.__dict__[name]._ref)] = self.__dict__[name]


        if self._ooop.debug:
            logger.debug("model: %s" % self._model)
            logger.debug("data: %s" % data)

        # create or write the object
        if self._ref > 0 and not self._copy: # same object
            self._ooop.write(self._model, self._ref, data)
        else:
            self._ref = self._ooop.create(self._model, data)

        # update cache
        self.INSTANCES['%s:%s' % (self._model, self._ref)] = self
        return self._ref


    def delete(self):
        if self._ref > 0:
            self._ooop.unlink(self._model, self._ref)
        #else:
        #    pass # TODO
        remove(self)

    # TODO: to develop a more clever save function
    def save_all(self):
        """ save related instances """
        for key, instance in self.INSTANCES.items():
            if instance != self: # save self at the end
                instance.save()
            # updating INSTANCES
            self.INSTANCES.pop(key)
            self.INSTANCES['%s:%s' % (instance._model, instance._ref)] = instance
        self.save()

    @property
    def id(self):
        return self._ref

    def __repr__(self):
        """ default representation: <model:id> """
        if self._ref < 0:
            return u'<%s> new data instance' % self._model
        try:
            return u'<%s:%s %r> data instance' % (self._model, self._ref, self.name)
        except:
            return u'<%s:%s> data instance' % (self._model, self._ref)
