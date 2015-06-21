import flask
from flask import Flask,render_template,request,send_from_directory,session
import requests
from lxml import html
import time
import datetime as dt

##########################################################
def scrape():
	
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
	data = tree.xpath('//table[@class="boxoutside"]//td/text()')
	return [data[x: x+4] for x in xrange(0, len(data), 4)]

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
	data = scrape()

	for x in xrange(len(data)):
		data[x][3] = data[x][3].replace(",","")

	enddt = dt.datetime.strptime(data[-1][0][:data[-1][0].index(" ")],"%m/%d").replace(year=2015)
	begindt = dt.datetime.strptime(data[0][0][:data[0][0].index(" ")],"%m/%d").replace(year=2015)

	timespan = (enddt - begindt).days

	table = [[begindt + dt.timedelta(x),0.0] for x in range(timespan+1)]

	days = [["Sunday",0.0],["Monday",0.0],["Tuesday",0.0],["Wednesday",0.0],["Thursday",0.0],["Friday",0.0],["Saturday",0.0]]
	hours = [ [x,0.0] for x in range(24)]


	for datum in data:
		currdt = dt.datetime.strptime(datum[0],"%m/%d %I:%M %p").replace(year=2015)
		days[(currdt.weekday()+1)%7][1] = days[(currdt.weekday()+1)%7][1] - float(datum[2])
		hours[currdt.hour][1] = hours[currdt.hour][1] - float(datum[2])
		loop = True
		i = 0
		while (loop and i<len(table)):
			if (currdt - table[i][0]).days == 0:
				table[i][1]=table[i][1]-float(datum[2])
				loop = False
			i = i+1


	dateuse = [[tab[0].strftime("%m/%d"),int(tab[1]*1000)/1000.0] for tab in table]

	return render_template("page.html",data=data,dateuse=dateuse)

@app.route('/d3')
def d3():
	return render_template("d3test.html")

@app.route('/<filename>')
def getfile(filename):
	return send_from_directory('.',
                               filename)

def main():
	app.debug = True
	app.run(host='0.0.0.0', port=80)
	print session

if __name__ == '__main__':
	main()
	pass
