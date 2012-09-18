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
import types
from datetime import datetime, date

# check if pydot is installed
try:
    import pydot
except:
    pydot = False

# check if pyro is installed
try:
    import Pyro.core
except:
    pyro = False

__author__ = "Pedro Gracia <pedro.gracia@impulzia.com>"
__license__ = "GPLv3+"
__version__ = "0.2.3"


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

class objectsock_mock():
    """mock for objectsock to be able to use the OOOP as a module inside of openerp"""
    def __init__(self, parent, cr):
        self.parent = parent
        self.cr = cr
    
    def execute(self, *args, **kargs):
        """mocking execute function"""
        if len(args) == 7:
            (dbname, uid, pwd, model, action, vals, fields) = args
        elif len(args) == 6:
            (dbname, uid, pwd, model, action, vals) = args
        elif len(args) == 5:
            (dbname, uid, pwd, model, action) = args
        
        _model = self.parent.pool.get(model)
        
        if action == 'create':
            return _model.create(self.cr, uid, vals)
        elif action == 'unlink':
            return _model.unlink(self.cr, uid, vals)
        elif action == 'write':
            return _model.write(self.cr, uid, vals, fields)
        elif action == 'read' and len(args) == 7:
            return _model.read(self.cr, uid, vals, fields)
        elif action == 'read':
            return _model.read(self.cr, uid, vals)
        elif action == 'search':
            return _model.search(self.cr, uid, vals)
        else:
            return getattr(_model, action)(self.cr, uid) # is callable
        

class OOOP:
    """ Main class to manage xml-rpc comunitacion with openerp-server """
    def __init__(self, user='admin', pwd='admin', dbname='openerp', 
                 uri='http://localhost', port=8069, protocol='xmlrpc', debug=False, 
                 exe=False, active=True, lang='en_US', **kwargs):
        self.user = user       # default: 'admin'
        self.pwd = pwd         # default: 'admin'
        self.dbname = dbname   # default: 'openerp'
        self.uri = uri
        self.port = port
        self.protocol = protocol   # default: 'xmlrpc'
        self.debug = debug
        self.exe = exe
        self.active = active
        self.commonsock = None
        self.objectsock = None
        self.reportsock = None
        self.uid = None
        self.models = {}
        self.fields = {}
        self.proxy = False
        self.lang = lang

        #has to be uid, cr, parent (the openerp model to get the pool)
        if len(kwargs) == 3:
            self.uid = kwargs['uid']
            self.objectsock = objectsock_mock(kwargs['parent'], kwargs['cr'])
        else:
            if protocol == 'pyro':
                self.connect_pyro()
            else:
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

    def connect_pyro(self):
        """login and sockets to pyro services: common, object and report"""
        url = 'PYROLOC://%s:%s/rpc' % (self.uri,self.port)
        self.proxy =  Pyro.core.getProxyForURI(url)
        self.uid = self.proxy.dispatch( 'common', 'login', self.dbname, self.user, self.pwd)
        self.reportsock = False

    def execute(self, model, *args):
        if self.debug:
            print "DEBUG [execute]:", model, args
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, *args)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, *args)
        return result

    def create(self, model, data):
        """ create a new register """
        context = {'lang':self.lang}
        if self.debug:
            print "DEBUG [create]:", model, data
        if 'id' in data:
            del data['id']
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'create', data, context)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'create', data, context)
        return result

    def unlink(self, model, ids):
        """ remove register """
        if self.debug:
            print "DEBUG [unlink]:", model, ids
        if isinstance(ids, int):
            ids = [ids]
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'unlink', ids)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'unlink', ids)
        return result

    def write(self, model, ids, value):
        """ update register """
        context = {'lang':self.lang}
        if self.debug:
            print "DEBUG [write]:", model, ids, value
        if isinstance(ids, int):
            ids = [ids]
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'write', ids, value, context)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'write', ids, value, context)
        return result

    def read(self, model, ids, fields=[]):
        """ update register """
        context = {'lang':self.lang}
        if self.debug:
            print "DEBUG [read]:", model, ids, fields
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'read', ids, fields, context)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', ids, fields, context)
        return result

    def read_all(self, model, fields=[]):
        """ update register """
        context = {'lang':self.lang}
        if self.debug:
            print "DEBUG [read_all]:", model, fields
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'read', self.all(model), fields, context)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'read', self.all(model), fields, context)
        return result

    def search(self, model, query, offset=0, limit=999, order=''):
        """ return ids that match with 'query' """
        context = {'lang':self.lang}
        if self.debug:
            print "DEBUG [search]:", model, query, offset, limit, order
        if self.protocol == 'pyro':
            result = self.proxy.dispatch( 'object', 'execute', self.dbname, self.uid, self.pwd, model, 'search', query, offset, limit, order, context)
        else:
            result = self.objectsock.execute(self.dbname, self.uid, self.pwd, model, 'search', query, offset, limit, order, context)
        return result
        
    # TODO: verify if remove this
    def custom_execute(self, model, ids, remote_method, data):
        if self.debug:
            print "DEBUG [custom_execute]:", self.dbname, self.uid, self.pwd, model, args
        return self.objectsock.execute(self.dbname, self.uid, self.pwd, model, ids, remote_method, data)

    def all(self, model, query=[]):
        """ return all ids """
        if self.debug:
            print "DEBUG [all]:", model, query
        return self.search(model, query)

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
        
    def export(self, filename, filetype, showfields=True, model=None, deep=-1):
        """Export the model to dot file"""
        #o2m 0..* m2m *..* m2o *..0
        
        if not pydot:
            raise ImportError('no pydot package found')
        
        if filename == "":
            raise TypeError('no filename')
        
        if not filetype in ('dot', 'png', 'jpg', 'svg'):
            raise TypeError('filetype only accept dot, png, jpg or svg types')

        graph = pydot.Dot(graph_type='digraph')
        graph.set_ratio('compress')
        
        HEADER = """<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR>
                <TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4">
                <FONT FACE="Helvetica Bold" COLOR="white">%s</FONT>
                </TD>
            </TR>
        """
        
        FIELD = """
            <TR><TD ALIGN="LEFT" BORDER="0"
            ><FONT FACE="Helvetica Bold">%s</FONT
            ></TD>
            <TD ALIGN="LEFT"
            ><FONT FACE="Helvetica Bold">%s</FONT
            ></TD></TR>
        """
        
        TAIL = """
        </TABLE>
        >"""
        
        r = {}
        if not model:
            models = self.read_all(OOOPMODELS)
        else:
            model_id = self.search(OOOPMODELS, [('model','=', model)])
            models = self.read(OOOPMODELS, model_id)

        for model in models:
            r = self.set_model(model['model'], r, deep)

        lines = ""
        for key, value in r.items():
            if showfields:
                fields = ''.join([FIELD % k for k in value['fields']])
            else:
                fields = ''
            label = HEADER % key + fields + TAIL
            node = pydot.Node(value['name'], label=label)
            node.set_shape('none')
            graph.add_node(node)
            for i in value['links'].keys():
                edge = pydot.Edge(value['name'], r[i]['name'])
                if value['links'][i] == 'one2many':
                    edge.set_headlabel('0..*')
                    edge.set_taillabel('*..0')
                elif value['links'][i] == 'many2one':
                    edge.set_headlabel('*..0')
                    edge.set_taillabel('0..*')
                elif value['links'][i] == 'many2many':
                    edge.set_headlabel("*..*")
                    edge.set_taillabel("*..*")
                
                graph.add_edge(edge)
                
        graph.set_fontsize('8.0')
        filename = '%s.%s' % (filename, filetype)
        if filetype == 'dot':
            graph.write_dot(filename)
        elif filetype == 'png':
            graph.write_png(filename)
        elif filetype == 'jpg':
            graph.write_jpg(filename)
        elif filetype == 'svg':
            graph.write_svg(filename)


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
                print 'Printing aborted, too long delay!'
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

    def __iter__(self):
        return self
 
    def next(self):
        self.index += 1
        if self.index == len(self.objects):
            self.index = -1
            raise StopIteration
        return self.__getitem__(self.index)
        
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
        if type(self.objects[offset]) != types.IntType:
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
        if not ids: # CHECKTHIS
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
        offset = 0
        limit = 999
        order = ''
        for key, value in kargs.items():
            if key == 'offset':
                if int(value):
                    offset = value
            elif key == 'limit':
                if int(value):
                    limit = value
            elif key == 'order':
                order = value
            elif '__' in key:
                i = key.find('__')
                op = OPERATORS[key[i+2:]]
                key = key[:i]
            	q.append(('%s' % key, op, value))
            else:
                op = '='
            	q.append(('%s' % key, op, value))
        ids = self._ooop.search(self._model, q, offset, limit, order)
        if as_list:
            return self.read(ids, fields)
        return List(self, ids)

    def exclude(self, *args, **kargs):
        pass # TODO

    def export(self, filename=None, filetype="jpg", deep=0):
        """docstring for export"""
        if not filename:
            filename = self._model
        self._ooop.export(filename=filename, filetype=filetype, model=self._model, deep=deep)

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
                    if isinstance(default_values[i], str):
                        t = datetime.strptime(default_values[i], "%Y-%m-%d %H:%M:%S").timetuple()
                    else:
                        t = default_values[i].timetuple()
                    default_values[i] = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            # active by default ?
            if self._ooop.active:
                default_values['active'] = True
            default_values.update(**kargs) # initial values from caller
            self.init_values(**default_values)

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
            print "%s: %s" % (i, self.__getattr__(i))

    def __setattr__(self, field, value):
        if 'fields' in self.__dict__:
            if field in self.fields.keys():
                ttype = self.fields[field]['ttype']
                if value:
                    if ttype =='many2one':
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
            if data[name]: # TODO: review this
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
                self.__dict__[name] = None # TODO: empty openerp data object
        elif ttype in ('one2many', 'many2many'):
            if data[name]:
                self.__dict__['__%s' % name] = data[name]
                self.__dict__[name] = List(Manager(relation, self._ooop),
                                           data=self, model=relation)
                for i in xrange(len(data[name])):
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
        elif ttype == "datetime" and data[name]:
            self.__dict__[name] = datetime.strptime(data[name], "%Y-%m-%d %H:%M:%S")
        elif ttype == "date" and data[name]:
            self.__dict__[name] = date.fromordinal(datetime.strptime(data[name], "%Y-%m-%d").toordinal())
        else:
            # axelor conector workaround
            if type(data) == types.ListType:
                data = data[0]
            self.__dict__[name] = data[name]

        if self.__dict__[name]:
            return self.__dict__[name]
    
    def save(self):
        """ save attributes object data into openerp
            return: object id """
        
        data = {}
        for i in self.fields.values():
            name, ttype, relation = i['name'], i['ttype'], i['relation']
            if name in self.__dict__.keys(): # else keep values in original object
                if not '2' in ttype: # not one2many, many2one nor many2many
                    if ttype == 'date' and self.__dict__[name]:
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
                    if self.__dict__[name] and 'name' in dir(self.__dict__[name]):
                        data[name] = self.__dict__[name]._ref
                        # update __name and INSTANCES (cache)
                        self.__dict__['__%s' % name] = [self.__dict__[name]._ref, self.__dict__[name].name]
                        self.INSTANCES['%s:%s' % (relation, self.__dict__[name]._ref)] = self.__dict__[name]

        if self._ooop.debug:
            print ">>> model:", self._model
            print ">>> data:", data

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
