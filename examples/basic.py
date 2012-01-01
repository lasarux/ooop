from ooop import OOOP

o = OOOP(dbname="testv6")
#Pyro Demo
#o = OOOP(user='admin',pwd='admin',dbname='zikzakmedia',uri='localhost',port=8071,protocol='pyro')
partners = o.ResPartner.all()
for partner in partners:
    print "id: %d, name: %s" % ( partner._ref, partner.name )
