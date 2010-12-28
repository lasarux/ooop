from ooop import OOOP
print "###################### START ###########################################"
O = OOOP(dbname="test", port=8050)
print O.ProductProduct.fields_get()
product = O.ProductProduct.get(1)
print product.name
print product.categ_id.name
print "###################### END #############################################"
