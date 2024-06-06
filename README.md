<img src="http://github.com/lasarux/ooop/raw/master/artwork/ooop.png" width="150px" height="150px" />

**Warning: this is a very initial release.**


Contacting us:
--------------------

Discussion group:  [openerp-ooop](http://groups.google.es/group/openerp-ooop?hl=en&pli=1)
Post Issues on github: [GITHUB Issues](http://github.com/lasarux/ooop/issues)
  

How to install?
========================

***python***
<pre><code>
$ python setup.py install
</code></pre>

***jython***
<pre><code>
$ jython setup.py install
</code></pre>



Examples (python console):
========================

Connecting to server
--------------------
<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
</code></pre>


Retrieving all from model
-------------------------
<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> o.ResPartner.all()
</code></pre>

Retrieving 1 record from model
-------------------------

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.ResPartner.get(1)
</code></pre>

Accesing attributes
--------------------

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.ResPartner.get(1)
  >>> print n.name
</code></pre>

or in related objects:
  
<pre><code>
  >>> print len(n.address) 
  >>> print n.address[0].name 
</code></pre>

Deleting 1 record
--------
<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.ResPartner.get(1)
  >>> n.delete()
</code></pre>

Deleting multiple records
---------

**100 firsts**

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.ResPartner.all()
  >>> n[1:100].delete()
</code></pre>

**all**

<pre><code>
  >>> n.delete()
</code></pre>

Filtering
---------

You can extend arguments using **ne**, **lt**, **lte**, **gt**, **gte**, **like** and **ilike**:

<pre><code>
  >>> o.ResPartner.filter(name='Guido')
  >>> o.ResPartner.filter(name__ne='Guido')
  >>> o.ResPartner.filter(name__lt='Guido')
  >>> o.ResPartner.filter(name__lte='Guido')
  >>> o.ResPartner.filter(name__gt='Guido')
  >>> o.ResPartner.filter(name__gte='Guido')
  >>> o.ResPartner.filter(name__like='Guido')
  >>> o.ResPartner.filter(name__ilike='guido')
  >>> o.ResPartner.filter(id__in=[1,2,5,8])
  >>> o.ResPartner.filter(id__not_in=[1,2,5,8])
</code></pre>


Creating new
------------

<pre><code>
  >>> n = o.ResPartner.new()
  >>> n.name = 'Partner created with OOOP'
  >>> n.save()
</code></pre>

<pre><code>
  >>> n = o.ResPartner.new(name='Guido', active=True)
  >>> n.save()
</code></pre>

**with context**

To pass context in the call:

<pre><code>
  >>> n = o.ResPartner.new()
  >>> n.name = 'Partner created with OOOP'
  >>> n.save(context={'context-key':context-value})
</pre></code>

**with related objects**

To save all related objects of an object:

<pre><code>
  >>> n = o.ResPartner.new()
  >>> n.name = 'Partner created with OOOP'

  >>> addr = o.ResPartnerAddress.new()
  >>> addr.street = "Testing related objects"

  >>> n.address.append(addr)
  >>> n.save_all()
</pre></code>

<pre><code>
  >>> m = [o.ResPartnerAddress.new(name='New Address', street='New Street', active=True)]
  >>> n = o.ResPartner.new(name='Guido', address=m, active=True)
  >>> n.save_all()
</code></pre>
