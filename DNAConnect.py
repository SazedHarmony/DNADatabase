import sys
import traceback
import MySQLdb as mdb
import cMSharing as cMS

#DBconnectBase and DBconnect classes used from Familinx pythonUI DBconnect.py

class DBconnectBase():
	def __init__(self, db_name=None, user_name=None, password=None):
		self.db_name=db_name
		self.user_name=user_name
		self.password=password
		self.db_connection = mdb.connect('localhost', user_name, password, db_name);
	def  __del__(self):
		if self.db_connection:
			self.db_connection.close()

class DBconnect(DBconnectBase):
	def tableLength(self, table_name):
		with self.db_connection:
			cur = self.db_connection.cursor()
			cur.execute("select count(*) from %s"%table_name)
			(number_of_rows,)=cur.fetchone()
			return number_of_rows

# Person class to hold information about people
class Person():
	def __init__(self):
		self.given_name = ""
		self.surname = ""
		self.sex = -1
		self.birth_year = "-1"
		self.birth_month = ""
		self.birth_day = ""
		self.death_year = "-1"
		self.death_month = ""
		self.death_day = ""
		self.birth_place = ""
		self.death_place = ""
		self.id = -1
		self.table_id = -1
		self.marriage_year = ""
		self.spouse_id = -1
		self.father_id = -1
		self.mother_id = -1
		self.spouse_family_number = ""
		self.child_family_number = ""
	def __str__(self):
		strReturn = "Person: " + self.given_name + " " + self.surname + "\n"
		strReturn += "Sex: "
		if (self.sex == 1):
			strReturn += "Male\n"
		else:
			strReturn += "Female\n"
		strReturn += "Birth Day: " + self.birth_day + " " + self.birth_month + " " + self.birth_year + "\n"
		strReturn += "Birth Place: " + self.birth_place + "\n"
		strReturn += "Death Day: " + self.death_day + " " + self.death_month + " " + self.death_year + "\n"
		strReturn += "Death Place: " + self.death_place + "\n"
		strReturn += "Spouse Family Number: " + self.spouse_family_number + "\n"
		strReturn += "Child Family Number: " + self.child_family_number + "\n"
		strReturn += "GED ID: " + str(self.id) + "\n"
		strReturn += "Table ID: " + str(self.table_id) + "\n"
		return strReturn
	def firstName(self):
		first = self.given_name
		first1 = first.split(' ')
		return first1[0]

def idFromLine(line):
	idNum = ""
	atCount = 0
	for char in line:
		if char == '@':
			atCount += 1
		else:
			if (atCount == 1 and (char != "I" and char != "F" and char != "P")):
				idNum += char
	return idNum

def parseDate(line):
	lineParts = line.split(" ")
	if (len(lineParts) > 2):
		return ' '.join(lineParts[2:])
	return ""

def addRelationships(personList):
	for i in range(len(personList)):
		for j in range(len(personList)):
			if (personList[i].spouse_family_number == personList[j].child_family_number and personList[i].spouse_family_number != ""):
				db_table_connection = DBconnectBase("familinx", "familinx", "familinx")
				cur = db_table_connection.db_connection.cursor()
				inputQuery = "INSERT INTO familinx.relationship (Child_id, Parent_id) VALUES (" + str(personList[j].table_id) + ", " + str(personList[i].table_id) + ")"
				cur.execute(inputQuery)
				cur.close()
	return

def addPersonIntoTable(person):
	db_table_connection = DBconnectBase("familinx", "familinx", "familinx")
	cur = db_table_connection.db_connection.cursor()
	namesQuery = "SELECT t1.Id FROM familinx.names t1 INNER JOIN familinx.years t2 WHERE t1.Id = t2.Id AND t1.Surname = '" + person.surname + "' AND t1.GivenName = '" + person.firstName() + "'"
	if (person.birth_year != "-1"):
		namesQuery += " AND t2.Byear = " + str(person.birth_year)
	if (person.death_year != "-1"):
		namesQuery += " AND t2.Dyear = " + str(person.death_year)
	cur.execute(namesQuery)
	db_table_connection.db_connection.commit()
	res = cur.fetchone()
	cur.close()
	if res != None and res != ():
		res = res[0]
		person.table_id = res
	else:
		cur = db_table_connection.db_connection.cursor()
		cur.execute("SELECT MAX(Id) FROM familinx.years")
		iD = cur.fetchone()
		iD = iD[0] + 1
		person.table_id = iD
		inputQuery1 = ""
		if (person.death_year != "-1"):
			inputQuery1 += "INSERT INTO familinx.years (Id, Byear, Dyear) VALUES (" + str(iD) + ", " + person.birth_year + ", " + person.death_year + ")"
		elif (person.birth_year != "-1"):
			inputQuery1 += "INSERT INTO familinx.years (Id, Byear) VALUES (" + str(iD) + ", " + person.birth_year +  ")"
		else:
			inputQuery1 += "INSERT INTO familinx.years (Id) VALUES (" + str(iD) + ")"
		cur.execute(inputQuery1)
		inputQuery2 = "INSERT INTO familinx.gender VALUES (" + str(iD) + ", " + str(person.sex) + ")"
		cur.execute(inputQuery2)
		inputQuery3 = "INSERT INTO familinx.names (Id, GivenName, Surname) VALUES (" + str(iD) + ", '" + person.firstName() + "', '" + person.surname + "')"
		cur.execute(inputQuery3)
		db_table_connection.db_connection.commit()
		cur.close()
	return person

#Default database login information
user_name = 'familinx'
password = 'familinx'
db_name = 'familinx'
db_connection = DBconnectBase(db_name, user_name, password)
cur = db_connection.db_connection.cursor()
cur.execute("SET sql_notes = 0")
cur.execute("CREATE TABLE IF NOT EXISTS familinx.names ( Id INT NOT NULL PRIMARY KEY, GivenName VARCHAR(30), Surname VARCHAR(30) )")
cur.execute("CREATE TABLE IF NOT EXISTS familinx.genomes ( Id INT NOT NULL PRIMARY KEY, FileName VARCHAR(40), IsCouple BOOL, IsComplete BOOL )")
cur.execute("CREATE TABLE IF NOT EXISTS familinx.cMsharing ( Id1 INT NOT NULL, Id2 INT NOT NULL, chr VARCHAR(4), start INT, end INT, length INT, RoH BOOL )")
cur.execute("CREATE TABLE IF NOT EXISTS familinx.anonProfiles (Id INT PRIMARY KEY NOT NULL, fileNameIn VARCHAR(60) )")
db_connection.db_connection.commit()
cur.close()

if (len(sys.argv) <= 2):
	print "Invalid arguments"
else:
	if (sys.argv[1] == "-p" and len(sys.argv) == 3):
		ped_file = open(sys.argv[2], 'r')
		lines = ped_file.readlines()
		ped_file.close()
		personList = []
		while(len(lines) > 0):
			line = lines[0].strip()
			if (len(line) < 4):
				del lines[0]
			else:
				lineCounter = 0
				currentLine = line
				if (currentLine[0:4] == "0 @I" or currentLine[0:4] == "0 @P"):
					person = Person()
					person.id = idFromLine(line)
					currentLine = lines[1].strip()
					while(currentLine[0:3] != "0 @"):
						if (currentLine[0:6] == "1 NAME"):
							nameSet = currentLine.split(' ')
							person.given_name = nameSet[2]
							surname = nameSet[-1]
							person.surname = surname[1:-1]
						if (currentLine[0:6] == "2 SURN"):
							person.surname = currentLine[7:]
						if (currentLine[0:6] == "2 GIVN"):
							person.given_name = currentLine[7:]
						if (currentLine[0:5] == "1 SEX"):
							if (currentLine[6] == "M"):
								person.sex = 1
							if (currentLine[6] == "F"):
								person.sex = 2
						if (currentLine[0:6] == "1 FAMS"):
							person.spouse_family_number = idFromLine(currentLine)
						if (currentLine[0:6] == "1 FAMC"):
							person.child_family_number = idFromLine(currentLine)
						if (currentLine[0:6] == "1 BIRT"):
							date = lines[lineCounter + 1].strip()
							place = lines[lineCounter + 2].strip()
							if (date[0:6] == "2 DATE" or place[0:6] == "2 DATE"):
								if (place[0:6] == "2 DATE"):
									date = place
								date = parseDate(date)
								datePart = date.split(' ')
								if (len(datePart) == 1):
									person.birth_year = datePart[0]
								if (len(datePart) == 2):
									person.birth_year = datePart[1]
									if (datePart[0].isdigit()):
										person.birth_day = datePart[0]
									else:
										person.birth_month = datePart[0]
								if (len(datePart) == 3):
									person.birth_day = datePart[0]
									person.birth_month = datePart[1]
									person.birth_year = datePart[2]
							if (date[0:6] == "2 PLAC" or place[0:6] == "2 PLAC"):
								if (date[0:6] ==" 2 PLAC"):
									place = date
								person.birth_place = place[7:]
						if (currentLine[0:6] == "1 DEAT"):
							date = lines[lineCounter + 1].strip()
							place = lines[lineCounter + 2].strip()
							if (date[0:6] == "2 DATE" or place[0:6] == "2 DATE"):
								if (place[0:6] == "2 DATE"):
									date = place
								date = parseDate(date)
								datePart = date.split(' ')
								if (len(datePart) == 1):
									person.death_year = datePart[0]
								if (len(datePart) == 2):
									person.death_year = datePart[1]
									if (datePart[0].isdigit()):
										person.death_day = datePart[0]
									else:
										person.death_month = datePart[0]
								if (len(datePart) == 3):
									person.death_day = datePart[0]
									person.death_month = datePart[1]
									person.death_year = datePart[2]
							if (date[0:6] == "2 PLAC" or place[0:6] == "2 PLAC"):
								if (date[0:6] == "2 PLAC"):
									place = date
								person.death_place = place[7:]
						lineCounter += 1
						currentLine = lines[lineCounter].strip()
					if (lineCounter > 1):
						lineCounter -= 1
					personList.append(person)
				del lines[:lineCounter + 1]
		counter = 0
		inputtedList = []
		tempInputtedList = []
		changed = False
		finishedList = []
		while len(personList) > 0:
			person = personList[counter]
			if (person.child_family_number == "" or person.child_family_number in inputtedList):
				changed = True
				newPerson = addPersonIntoTable(person)
				finishedList.append(newPerson)
				if (person.spouse_family_number in tempInputtedList):
					inputtedList.append(person.spouse_family_number)
				else:
					tempInputtedList.append(person.spouse_family_number)
				del personList[counter]
				counter -= 1
			counter += 1
			if counter == len(personList):
				if (not changed):
					counter = 0
					index = 0
					oldest = Person()
					oldest.birth_year = "2017"
					while(counter < len(personList)):
						if (personList[counter].birth_year != ""):
							if int(personList[counter].birth_year) < int(oldest.birth_year):
								oldest = personList[counter]
								index = counter
						counter += 1
					newPerson = addPersonIntoTable(oldest)
					finishedList.append(newPerson)
					inputtedList.append(oldest.spouse_family_number)
					del personList[index]
				counter = 0
				changed = False
		addRelationships(finishedList)
		ped_file.close()
	elif (sys.argv[1] == "-g"):
		inputFile = open(sys.argv[2], "r")
		iD = ""
		name = ""
		if (len(sys.argv) == 5):
			if (sys.argv[3] == "-i"):
				iD = sys.argv[4]
			else:
				print "Invalid arguments\nContinuing program"
		else:
			nameSet = sys.argv[2]
			nameSet = nameSet.split('.')
			name = nameSet[0]
			cur = db_connection.db_connection.cursor()
			cur.execute("SELECT MAX(Id) FROM familinx.names")
			res = cur.fetchone()
			res = res[0] + 1
			iD = str(res)
			cur.close()
			cur = db_connection.db_connection.cursor()
			cur.execute("INSERT INTO familinx.names (Id, GivenName) VALUES (" + iD + ", '" + name + "')")
			cur.execute("INSERT INTO familinx.anonProfiles (Id, fileNameIn) VALUES (" + iD + ", '" + sys.argv[2] + "')")
			db_connection.db_connection.commit()
			cur.close()
		outputFileName = iD + "genome.txt"
		outputFile = open(outputFileName, "w")
		for line in inputFile:
			line = line.strip()
			if (line[0] != "#"):
				lineType = line.split("\t")
				if (len(lineType) == 4):
					outputFile.write('\t'.join(lineType) + "\n")
				elif (len(lineType) == 5):
					genotype = '\t'.join(lineType[3:])
					outputFile.write(lineType[0] + '\t' + lineType[1] + '\t' + lineType[2] + '\t' + genotype + '\n')
		inputFile.close()
		outputFile.close()
		cmShareClass = cMS.cMShare()
		cmShareClass.createPersonRelatives(iD, outputFileName)
		cur = db_connection.db_connection.cursor()
		cur.execute("REPLACE INTO familinx.genomes (Id, FileName, IsCouple, IsComplete) VALUES (" + iD + ", '" + outputFileName + "', 0, 1)")
		db_connection.db_connection.commit()
		cur.close()
		cur = db_connection.db_connection.cursor()
		cur.execute("SELECT Id, FileName FROM familinx.genomes WHERE Id != " + str(iD) + " AND IsComplete = 1")
		db_connection.db_connection.commit()
		res = cur.fetchall()
		if res != None and res != ():
			for result in res:
				share = cMS.cMShare()
				share.addIds(iD, result[0])
				share.addFiles(outputFileName, result[1])
		cur.close()
	else:
		print "Invalid arguments"			

