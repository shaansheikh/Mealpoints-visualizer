import requests
from lxml import html
import time

#
##get skey
#r = requests.get('https://services.jsatech.com/login.php?cid=129').text
#tree = html.fromstring(r)
#skey = tree.xpath('//form/input[@name="skey"]/@value')[0]
#
##login
#payload = {"save":"1","skey":skey,"cid":"129","wason":"","loginphrase":"109989123","password":"204c5abb"}
#requests.post("https://services.jsatech.com/login.php?cid=129&skey=" + skey,data=payload)
#requests.get("https://services.jsatech.com/login.php?skey="+skey+"&cid=129&fullscreen=1&wason=")
#
#time.sleep(20)
#
##get history
#payload = {"save":"1","skey":skey,"cid":"129","acctto":"3","month":"13"}
#r = requests.post("https://services.jsatech.com/statement.php?cid=129&skey=" + skey,data=payload).text

f = open('file.html', 'r')
r = f.read()
f.close()

tree = html.fromstring(r)
print tree.xpath('//table[@class="boxoutside"]//td/text()')