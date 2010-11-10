from ooop import OOOP
from datetime import datetime, timedelta

o = OOOP(dbname="optima")
# acumulated = timedelta()
# for i in range(100):
#     start = datetime.now()
#     o = OOOP(dbname="optima")
#     stop = datetime.now() -start
#     acumulated += stop
#     print stop
# print "avg:", stop/100


start_a = datetime.now()
x = o.OptimaReturnsQrenta.all()
for i in range(100):
    data = x[i] 
    print data.account.customers[0].customer_id.agent.name
stop_a = datetime.now() -start_a

# start_b = datetime.now()
# x = o.read_all('optima.returns.qrenta', []) 
# print x
# stop_b = datetime.now() -start_b
# 
print "a:", stop_a
# print "b:", stop_b


