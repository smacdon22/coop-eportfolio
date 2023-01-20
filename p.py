import requests, urllib.parse, json, csv, datetime


class Policy:
    def __init__(self, version="", location="", embargo=datetime.timedelta(days=0)):
        self.version = version
        self.location = location
        self.embargo = embargo
        self.amount = 0
        self.units = ""
        self.passed = ""
        self.note = ""

    def setVersion(self, vers):
        if self.version != "":
            if vers in self.version:
                return
            elif self.version == "all":
                return
            else:
                self.version += " " + vers
                if "submitted" in self.version and "accepted" in self.version and "published" in self.version:
                    self.version = "all"
                return
        else:
            self.version = vers
            return

    def setLocation(self, loc):
        lociwant = ["any_website", "any_repository", "institutional_repository",
                    "non_commercial_institutional_repository", "non_commercial_repository"]
        if self.location != "" and loc in lociwant:
            if loc in self.location:
                return
            else:
                self.location += " " + loc
                return
        elif loc not in lociwant:
            return
        else:
            self.location = loc
            return

    def setEmbargo(self, a, u):
        self.amount = a
        if self.amount == 0:
            return
        self.units = u
        if self.units in "days":
            self.embargo = datetime.timedelta(days=self.amount)
        elif self.units in "weeks":
            self.embargo = datetime.timedelta(weeks=self.amount)
        elif self.units in "months":
            self.embargo = datetime.timedelta(days=self.amount * 30.45)
        elif self.units in "years":
            self.embargo = datetime.timedelta(days=self.amount * 365)
        return

    def setTime(self, dayte):
        cur_date = datetime.datetime.today()
        if self.units in "days":
            some_dates = datetime.timedelta(days=self.amount)
        elif self.units in "weeks":
            some_dates = datetime.timedelta(weeks=self.amount)
        elif self.units in "months":
            some_dates = datetime.timedelta(self.amount * 365 / 12)
        elif self.units in "years":
            datetime.timedelta(6 * 365)
        if cur_date.date() - dayte.date() >= some_dates:
            self.passed = "passed "
            return
        else:
            daysleft = (dayte.date() + some_dates)
            self.passed = "passes on " + str(daysleft) + " "
            return

    def setNotes(self, pnote):
        if self.note == "":
            self.note = pnote
        else:
            self.note += " " + pnote
        return

    def getPolicy(self):
        if "any_website" not in self.location and "institutional_repository" not in self.location and "any_repository" not in self.location and "non_commercial_institutional_repository" not in self.location and "non-commercial_repository" not in self.location:
            return 1
        elif self.embargo.days == 0:
            return (self.version, "none", "", self.note)
        else:
            aa = str(self.amount)
            return (self.version, str(aa + " " + self.units), self.passed, self.note)


class Publication:
    def __init__(self, jtitle="", issn="", open_access_prohibited="", pdate=datetime.datetime.now(), akey="",
                 rtitle=""):
        self.jtitle = jtitle
        self.issn = issn
        self.open_access_prohibited = open_access_prohibited
        self.pdate = pdate
        self.akey = akey
        self.rtitle = rtitle

    def getInfo(self):
        m = urllib.parse.unquote(self.jtitle)
        w = urllib.parse.unquote(self.issn)
        pd = self.pdate.date()
        d = datetime.date.strftime(pd, '%b-%d-%Y')
        return (m, w, self.rtitle, d)

    def getURL(self):
        thedata = ""
        filt = '"name_name","equals","Default Journal Name"'
        if "Conference" in self.issn:
            self.issn = self.issn.replace('qwerty', '')
            self.open_access_prohibited = self.open_access_prohibited.replace('eee', 'EEE')
            filt = '"name_name","contains%20word","' + urllib.parse.quote(self.open_access_prohibited) + '"'
            urlf = 'v2.sherpa.ac.uk/cgi/retrieve?item-type=publisher&api-key=' + self.akey + '&format=Json&filter=[[' + filt + ']]'
            url = requests.get('https://' + urlf)
            thedata = url.json()
            if type(thedata) != dict or len(thedata["items"]) == 0:
                return (self.getInfo(), "No policies from this publisher for conferences")
            elif filt == '"id","equals","38"':
                filt = '"type","equals","conference_proceedings"],["id","equals","3559"'
            else:
                pid = ""
                for i in thedata["items"][0]["publications"]:
                    if i["title"][0]["title"].upper() in self.jtitle.upper():
                        pid = i["id"]
                        filt = '"id","equals","' + str(pid) + '"'
                if pid == "":
                    pid = thedata["items"][0]["id"]
                    ptit = urllib.parse.quote(self.jtitle)
                    filt = '"type","equals","conference_proceedings"],["publisher_id","equals","' + str(pid) + '"'
        elif len(self.jtitle) > 2 and "qwerty" not in self.issn:
            filt = '"title_title","equals","' + urllib.parse.quote(self.jtitle) + '"'
        elif "qwerty" in self.issn:
            self.issn = self.issn.replace('qwerty', '')
            filt = '"name_name","equals","' + urllib.parse.quote(self.open_access_prohibited) + '"'
            urlf = 'v2.sherpa.ac.uk/cgi/retrieve?item-type=publisher&api-key=' + self.akey + '&format=Json&filter=[[' + filt + ']]'
            url = requests.get('https://' + urlf)
            thedata = url.json()
            if type(thedata) != dict or len(thedata["items"]) == 0:
                return (self.getInfo(), "Name not Recognized")
            else:
                pid = thedata["items"][0]["id"]
                filt = '"type","equals","conference_proceedings"],["publisher_id","equals","' + str(pid) + '"'
        else:
            filt = '"issn","equals","' + urllib.parse.quote(self.issn) + '"'
        urlf = 'v2.sherpa.ac.uk/cgi/retrieve?item-type=publication&api-key=' + self.akey + '&format=Json&filter=[[' + filt + ']]'
        url = requests.get('https://' + urlf)
        thedata = url.json()
        return (thedata)

    def giveMeInfo(self):
        pol = []
        thedata = ""
        data = self.getURL()
        if type(data) != dict or (type(data) == dict and len(data["items"]) == 0):
            if self.issn.count('-') < 1:
                self.issn += "qwerty"
                data = self.getURL()
                if type(data) != dict or (type(data) == dict and len(data) == 0):
                    return (self.getInfo(), "Name not Recognized")
        if self.issn.count("-") < 1:
            self.issn = ""
        pol.clear()
        if self.pdate == datetime.datetime.today().date:
            self.pdate = data["items"][0]["system_metadata"]["date_modified"]
        for q in data["items"]:
            if self.jtitle == "":
                self.jtitle = q["title"][0]["title"]
            for s in q["publisher_policy"]:
                self.open_access_prohibited = s["open_access_prohibited"]
                if self.open_access_prohibited == "yes" or self.open_access_prohibited == "y":
                    a = self.getInfo()
                    b = "open access is prohibited"
                    return (a, b)
                for n in s["permitted_oa"]:
                    p = Policy()
                    for c in n:
                        if c == "article_version":
                            for e in n["article_version"]:
                                p.setVersion(e)
                        if c == "location":
                            for h in n["location"]["location"]:
                                p.setLocation(h)
                        if c == "embargo":
                            am = n["embargo"]["amount"]
                            un = n["embargo"]["units"]
                            p.setEmbargo(am, un)
                            p.setTime(self.pdate)
                        if c == "public_notes":
                            for k in n["public_notes"]:
                                p.setNotes(k)
                        if c == "conditions":
                            for x in n["conditions"]:
                                p.setNotes(x)
                    pol.append(p)
        jt = self.getInfo()
        m = 0
        n = []
        n.clear()
        for d in pol:
            if d.getPolicy() == 1:
                m += d.getPolicy()
            else:
                n.append(d.getPolicy())
        if m >= len(pol) and len(pol) != 0:
            b = "Nothing available to you"
            return (jt, b)
        return (jt, n)


def getMyFiles(theIn, theOut, ke):
    titlefile = [theIn, theOut]
    words = ['an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'th', 'rd',
             'nd', 'st']
    with open(titlefile[0], 'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        inform = [['Original Title', 'Publication Title', 'ISSN', 'Date', 'Versions', 'Embargos', 'Passed', 'Notes']]
        counter = 0
        for row in readCSV:
            if counter == 0:
                counter += 1
            else:
                pn = row[35]
                ti = ""
                pi = []
                ti = row[9].split(' ')
                for word in ti:
                    if word.count('/') > 0:
                        word = word.split('/')
                        wi = []
                        for wo in word:
                            if wo.lower() in words or (
                                    (len(wo) == 4 or len(wo) == 3) and (wo[0].isdigit() == True) and (
                                    wo[-2:].lower() in words or wo[-1:].lower() in words)):
                                wo = wo.lower()
                            elif (len(wo) < 6 and wo.upper() in pn) or ((wo[0] == '(' or wo[-1] == ')') and (
                                    wo[1:].upper() in pn or wo[:-1].upper() in row[35])):
                                wo == wo.upper()
                            else:
                                wo = wo.title()
                            wi.append(wo)
                        word = '/'.join(wi)
                        if "'S" in word:
                            word = word.replace("'S", "'s")
                        pi.append(word)
                    else:
                        if word.lower() in words or (
                                (len(word) == 4 or len(word) == 3) and (word[0].isdigit() == True) and (
                                word[-2:].lower() in words or word[-1:].lower() in words)):
                            word = word.lower()
                        elif (len(word) < 6 and word.upper() in pn) or ((word[0] == '(' or word[-1] == ')') and (
                                word[1:].upper() in pn or word[:-1].upper() in pn)):
                            word == word.upper()
                        else:
                            word = word.title()
                        if "'S" in word:
                            word = word.replace("'S", "'s")
                        pi.append(word)
                ii = ' '.join(pi)
                if "ASSOC " in pn:
                    pn = pn.replace('ASSOC', 'ASSOCIATION')
                elif 'SPRINGER' in pn:
                    pn = 'Springer'
                elif 'IEEE' in pn:
                    pn = 'IEEE'
                else:
                    ti = pn.split(' ')
                    pi.clear()
                    for word in ti:
                        if word.lower() in words:
                            word = word.lower()
                        elif len(word) < 5:
                            word = word.upper()
                        else:
                            word = word.title()
                        pi.append(word)
                    pn = ' '.join(pi)
                if 'J' in row[0]:
                    e = datetime.datetime.today()
                    e = e.date()
                    if 'Early Access' in row[13]:
                        b = row[56] + "-1"
                        e = datetime.datetime.strptime(b, '%b-%y-%d')
                    d = row[43]
                    y = row[44]
                    if len(d) == 3 and d in ['WIN', 'SPR', 'SUM', 'AUT']:
                        if 'SUM' in d:
                            d = 'JUN 1'
                        elif 'SPR' in d:
                            d = 'APR 1'
                        elif 'WIN' in d:
                            d = 'DEC 1'
                        else:
                            d = 'SEP 1'
                    if len(y) > 4:
                        pass
                    elif len(d) > 3 and len(d) < 7 and len(y) > 1:
                        if d[:1].isdigit() == True:
                            d = d + '-' + y
                            e = datetime.datetime.strptime(d, '%d-%b-%Y')
                        else:
                            d = d + "-" + y
                            e = datetime.datetime.strptime(d, '%b %d-%Y')
                    elif len(d) == 3 and len(y) > 1:
                        d = "28-" + d + "-" + y
                        e = datetime.datetime.strptime(d, '%d-%b-%Y')
                    elif len(d) == 7 and len(y) > 1:
                        ex = "28-" + d[-3:] + "-" + y
                        e = datetime.datetime.strptime(ex, '%d-%b-%Y')
                    elif len(d) == 0 and len(y) > 1:
                        em = "31-Dec-" + y
                        e = datetime.datetime.strptime(em, '%d-%b-%Y')
                    elif len(y) < 4 and len(d) > 0:
                        ex = ""
                        while ex.count('-') < 2:
                            ex = input(
                                "The date provided is wrong and missing a year\n" + d + "\nRetype below (ex: 03-03-2020) if you don't want to retype, enter '--'\n")
                        if ex == '--':
                            e = e
                        else:
                            e = datetime.datetime.strptime(ex, '%d-%m-%Y')
                    l = ""
                    l = row[38]
                    if l == "ISSN":
                        pass
                    elif len(l) > 5:
                        pub = Publication(jtitle=ii, issn=l, rtitle=row[8], pdate=e, akey=ke)
                        inform.append(pub.giveMeInfo())
                    else:
                        pub = Publication(jtitle=ii, rtitle=row[8], pdate=e, akey=ke, open_access_prohibited=pn)
                        inform.append(pub.giveMeInfo())
                elif "T" in row[0]:
                    pass
                else:
                    e = datetime.datetime.today()
                    e = e.date()
                    cd = row[15]
                    if len(cd) < 10:
                        cd = '30 ' + cd
                        e = datetime.datetime.strptime(cd, '%d %b, %Y')
                    elif len(cd) < 16:
                        cd = cd[:4] + cd[-8:]
                        e = datetime.datetime.strptime(cd, '%b %d, %Y')
                    elif len(cd) < 20:
                        cd = cd[7:]
                        e = datetime.datetime.strptime(cd, '%b %d, %Y')
                    else:
                        cd = cd[7:-5]
                        e = datetime.datetime.strptime(cd, '%b %d, %Y')
                    l = ""
                    l = row[9]
                    if l == "ce Name" in row[14]:
                        pass
                    else:
                        pub = Publication(jtitle=ii, rtitle=row[8], pdate=e, akey=ke, issn="Conference",
                                          open_access_prohibited=pn)
                        inform.append(pub.giveMeInfo())
                    o = pub.giveMeInfo()
                    if o != None and type(o[1]) == list:
                        for c in o[1]:
                            if c[1] != 'none':
                                print(
                                    [o[0][2], o[0][1], o[0][3], c[0], c[1], c[2], c[3]])
                counter += 1
    csvfile.close()
    print("All done!")


getMyFiles("Mike Smit.csv", "cooloutputfile.csv", "0786F11C-C214-11EB-BADF-FDF73CE2659A")
print("Your results are in cooloutputfile.csv")
return "hi"
