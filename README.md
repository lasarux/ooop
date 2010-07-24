<img src="http://github.com/lasarux/ooop/raw/master/artwork/ooop.png" width="150px" height="150px" />

**Warning: this is a very initial release.**


Contacting us:
--------------------

Discussion group:  [openerp-ooop](http://groups.google.es/group/openerp-ooop?hl=en&pli=1)
Post Issues on github: [GITHUB Issues](http://github.com/lasarux/ooop/issues)
  

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

or in related objects
  
<pre><code>
  >>> print n.address.name
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
</code></pre>


Creating new
------------

<pre><code>
  >>> n = ResPartner.new()
  >>> n.name = 'Partner created with OOOP'
  >>> n.save()
</code></pre>

<pre><code>
  >>> n = ResPartner.new(name='Guido', active=True)
  >>> n.save()
</code></pre>

<pre><code>
  >>> m = [ResPartnerAddress.new(name='New Address', active=True)]
  >>> n = ResPartner.new(name='Guido', address=m, active=True)
  >>> n.save_all()
</code></pre>

**with related objects**

To save all related objects of an object:

<pre><code>
  >>> n = ResPartner.new()
  >>> n.name = 'Partner created with OOOP'

  >>> addr = ResPartnerAddress.new()
  >>> addr.street = "Testing related objects"

  >>> n.address.append(addr)
  >>> n.save_all()
</pre></code>

