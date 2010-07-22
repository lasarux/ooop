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
  >>> o.res_partner.all()
</code></pre>

Retrieving 1 record from model
-------------------------

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.res_partner.get(1)
</code></pre>

Accesing attributes
--------------------

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.res_partner.get(1)
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
  >>> n = o.res_partner.get(1)
  >>> n.delete()
</code></pre>

Deleting multiple records
---------

**100 firsts**

<pre><code>
  >>> from ooop import OOOP
  >>> o = OOOP(dbname='demo')
  >>> n = o.res_partner.all()
  >>> n[1:100].delete()
</code></pre>

**all**

<pre><code>
  >>> n[:].delete()
</code></pre>

Filtering
---------

You can extend arguments using "__ne" ( != ), "__lt" ( < ) , "__lte" ( <= ), "__gt" ( > ), "__gte" ( >= ), "__like" ( SQL LIKE ), "__ilike" ( SQL_ILIKE ):

<pre><code>
  >>> o.res_partner.filter(name='Guido')
  >>> o.res_partner.filter(name__ne='Guido')
  >>> o.res_partner.filter(name__lt='Guido')
  >>> o.res_partner.filter(name__lte='Guido')
  >>> o.res_partner.filter(name__gt='Guido')
  >>> o.res_partner.filter(name__gte='Guido')
</code></pre>


Creating new
------------

<pre><code>
  >>> n = res_partner.new()
  >>> n.name = 'Partner created with OOOP'
  >>> n.save()
</code></pre>

**with related objects**

<pre><code>
  >>> n = res_partner.new()
  >>> n.name = 'Partner created with OOOP'

  >>> addr = res_partner_addres.new()
  >>> addr.street = "Testing related objects"
  >>> addr.save()

  >>> n.address = [addr]
  >>> n.save()
</code></pre>

Save object and relateds
------------------------

n.save_all() <- to save related objects



