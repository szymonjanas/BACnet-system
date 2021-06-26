        
import BAC0
# import time 
bacnet = BAC0.connect(ip='127.0.0.10/8')

# bacnet.whois()

# print(bacnet.devices)

# print(bacnet.discover(networks=[47808]))
# print(bacnet.devices)
# print()
# b = bacnet.whois()

# print(b)
# print(bacnet.read('1:10 device 47808 1'))

rep = bacnet.whohas(object_name='get_dusk#1')

print(rep)

req = bacnet.read('{} 19 1 presentValue'.format(rep[0][0]))

print(req)