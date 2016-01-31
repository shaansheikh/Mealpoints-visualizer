import flask
from flask import Flask,render_template,request,send_from_directory,session,flash,redirect
import requests
from lxml import html
import time
import datetime as dt

##########################################################
def readsaved():
	f = open('file.html', 'r')
	r = f.read()
	f.close()

	return r


def scrape(login,passwd):
	#get skey
	r = requests.get('https://services.jsatech.com/login.php?cid=129').text
	tree = html.fromstring(r)
	skey = tree.xpath('//form/input[@name="skey"]/@value')[0]

	#login
	payload = {"save":"1","skey":skey,"cid":"129","wason":"","loginphrase":login,"password":passwd}
	requests.post("https://services.jsatech.com/login.php?cid=129&skey=" + skey,data=payload)
	requests.get("https://services.jsatech.com/login.php?skey="+skey+"&cid=129&fullscreen=1&wason=")
	
	time.sleep(20)
	
	#get history
	payload = {"save":"1","skey":skey,"cid":"129","acctto":"5","month":"13"}
	r = requests.post("https://services.jsatech.com/statement.php?cid=129&skey=" + skey,data=payload).text

	return r


app = Flask(__name__)
app.secret_key="A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"

globaltree = None

def defaultdata():
	r = readsaved()
	tree = html.fromstring(r)
	data = tree.xpath('//table[@class="boxoutside"]//td/text()')
	data = [data[x: x+4] for x in xrange(0, len(data), 4)]
	global globaltree
	globaltree = tree
	return data

@app.route('/', methods=['GET', 'POST'])
def index():
	error= ""
	side = ""
	scraped = 0
	if request.method == 'POST':
		u = ("username" in request.form)
		p = ("password" in request.form)
		c = ("comment" in request.form)
		if (u and p and not c):
			r = scrape(request.form['username'],request.form['password'])
			tree = html.fromstring(r)
			global globaltree
			globaltree = tree
			data = tree.xpath('//table[@class="boxoutside"]//td/text()')
			data = [data[x: x+4] for x in xrange(0, len(data), 4)]
			print data
			scraped = 1
			if len(data) == 0:
				data = defaultdata()
				scraped = 0
				error = "Could not access any data. Double check your credentials."
				side = "1"
				return r

		elif (not u and not p and c):
			data = request.form["comment"] + "\n"
			data = data.splitlines()
			data = [x.split("\t") for x in data]
			scraped = 2
			if len(data) < 1 or len(data[0]) != 4:
				data = defaultdata()
				scraped = 0
				side = "2"
				error = "Could not parse data. Separate each transaction with a line break and each column with a tab"
		else:
			data = defaultdata()
			scraped = 0
			side = "0"
			error = "Please enter either your mealpoint account credentials or copy and paste your transaction history"
	else:
		data = defaultdata()
		scraped = 0

	info = [""]*7

	info[0] = "Unknown Name"
	if scraped < 2:
		global globaltree
		info[0] = globaltree.xpath('//table[@summary="Customer Information"]//b/text()')[0]
	



	for x in xrange(len(data)):
		if len(data[x]) == 4:
			data[x][3] = data[x][3].replace(",","")
			data[x][2] = data[x][2].replace(",","")

	if scraped==1:
		data = [x for x in data if len(x)==4 and int(x[0][:x[0].find("/")])>=8]
	else:
		data = [x for x in data if len(x)==4]

	#try:
	enddt = dt.datetime.strptime(data[-1][0][:data[-1][0].index(" ")],"%m/%d").replace(year=dt.datetime.now().year)
	while (enddt > dt.datetime.now()):
		enddt = enddt.replace(year = enddt.year-1)
	begindt = dt.datetime.strptime(data[0][0][:data[0][0].index(" ")],"%m/%d").replace(year=dt.datetime.now().year)
	while (begindt > enddt):
		begindt = begindt.replace(year = begindt.year-1)

	timespan = (enddt - begindt).days

	table = [[begindt + dt.timedelta(x),0.0] for x in range(timespan+1)]

	days = [["Sunday",0.0],["Monday",0.0],["Tuesday",0.0],["Wednesday",0.0],["Thursday",0.0],["Friday",0.0],["Saturday",0.0]]
	hours = [0.0]*24

	locCosts = [["West Side Dining",0.0],["SAC",0.0],["Roth",0.0],["Union",0.0],["Wang Center",0.0],["Tabler",0.0],["Unknown",0.0]]
	locFreq = [["West Side Dining",0],["SAC",0],["Roth",0],["Union",0],["Wang Center",0],["Tabler",0],["Unknown",0]]

	for x in range(len(data)):
		tempdt = dt.datetime.strptime(data[x][0],"%m/%d %I:%M %p").replace(year=begindt.year)
		if tempdt < begindt:
			tempdt = tempdt.replace(year=tempdt.year + 1)
		data[x][0] = tempdt.strftime("%m/%d/%Y %I:%M %p")

	for datum in data:
		if float(datum[2]) < 0:
			currdt = dt.datetime.strptime(datum[0],"%m/%d/%Y %I:%M %p")
			days[(currdt.weekday()+1)%7][1] = days[(currdt.weekday()+1)%7][1] - float(datum[2])
			hours[currdt.hour] = hours[currdt.hour] - float(datum[2])

			place = datum[1]

			if place[:3].lower() == "wsd":
				locCosts[0][1] = locCosts[0][1] - float(datum[2])
				locFreq[0][1] = locFreq[0][1] + 1
			elif place[:3].lower() == "sac":
				locCosts[1][1] = locCosts[1][1] - float(datum[2])
				locFreq[1][1] = locFreq[1][1] + 1
			elif place[:4].lower() == "deli" or place[:5].lower() == "union":
				locCosts[3][1] = locCosts[3][1] - float(datum[2])
				locFreq[3][1] = locFreq[3][1] + 1
			elif place[:7].lower() == "jasmine":
				locCosts[4][1] = locCosts[4][1] - float(datum[2])
				locFreq[4][1] = locFreq[4][1] + 1
			elif place[:6].lower() == "wendys" or place[:4].lower() == "roth" or place[:9].lower() == "s3 fusion" or place[:5].lower() == "red m"or place[:9].lower() == "market fr" or place[:9].lower() == "daily dis":
				locCosts[2][1] = locCosts[2][1] - float(datum[2])
				locFreq[2][1] = locFreq[2][1] + 1
			elif place[:6].lower() == "dunkin":
				locCosts[5][1] = locCosts[5][1] - float(datum[2])
				locFreq[5][1] = locFreq[5][1] + 1
			elif place[:20].lower() == "online deposit (jsa)":
				pass
			else:
				print place
				locCosts[6][1] = locCosts[6][1] - float(datum[2])
				locFreq[6][1] = locFreq[6][1] + 1


			loop = True
			i = 0
			while (loop and i<len(table)):
				if (currdt - table[i][0]).days == 0:
					table[i][1]=table[i][1]-float(datum[2])
					loop = False
				i = i+1

	info[1] = data[-1][-1]
	maxday = max(table, key=lambda x : x[1])
	info[2] = maxday[0].strftime("%A, %B %d")
	info[3] = '%.2f' % maxday[1]
	maxtrans =  max(data, key=lambda x: -1*float(x[2]))[:-1]
	while (maxtrans[1][-1].isdigit()):
		maxtrans[1] = maxtrans[1][:-1]
	maxtrans[0] = dt.datetime.strptime(maxtrans[0],"%m/%d/%Y %I:%M %p").strftime("%I:%M %p on %m/%d")
	maxtrans[2] = -1*float(maxtrans[2])
	info[4] = maxtrans
	justspent = [x[1] for x in table]
	exclusivejustspent = [x[1] for x in table if x[1]!=0]
	
	info[5] = '%.2f' % ((sum(justspent)*1.0)/len(justspent))
	info[6] = '%.2f' % ((sum(exclusivejustspent)*1.0)/len(exclusivejustspent))
	hourtimes = [str((x-1)%12 + 1)+y for y in [" AM"," PM"] for x in range(12)]
	hours = zip(hourtimes,hours)

	dateuse = [[tab[0].strftime("%m/%d"),int(tab[1]*1000)/1000.0] for tab in table]
	#except:
	#	flash("An unknown error occured. Please report this bug to shaan.sheikh@stonybrook.edu")
	#	return redirect("/")

	return render_template("page.html",data=data,dateuse=dateuse,days=days,hours=hours,loccost=locCosts,info=info,error=error,side=side)


def main():
	app.debug = True
	app.run(host='0.0.0.0', port=7000)
	print session

if __name__ == '__main__':
	main()
	pass

