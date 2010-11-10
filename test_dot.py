from ooop import OOOP
 
o = OOOP(dbname="optima")
# o.export(filename="test", filetype="jpg", model='res.partner', deep=2)
o.ResPartner.export(deep=1)