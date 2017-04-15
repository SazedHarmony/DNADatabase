import sys
import traceback
import MySQLdb as mdb
import cMSharing as cms

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

def cMDescribe(chrList, startList, endList, RoHList):
	returnString = ""
	sumLength = 0
	anyRoH = False
	for i in range(len(startList)):
		if chrList[i] != "MT" and chrList[i] != "Y":
			end = int(endList[i])
			start = int(startList[i])
			length = end - start
			sumLength = sumLength + length
			if (RoHList[i] == "1"):
				anyRoH = True
	cmLength = sumLength / 1000000.0
	if (cmLength > 3000):
		returnString = "Parent/Child"
	elif (cmLength > 2000):
		returnString = "Siblings"
	elif (cmLength > 1700):
		returnString = "Grandparent/grandchild or aunt/uncle and niece/nephew or half-siblings"
	elif (cmLength > 750):
		returnString = "First cousins or equivalent"
	elif (cmLength > 350):
		returnString = "First cousins once removed or equivalent"
	elif (cmLength > 150):
		returnString = "Second cousins or equivalent"
	elif (cmLength > 75):
		returnString = "Second cousins once removed or equivalent"
	elif (cmLength > 35):
		returnString = "Third cousins or equivalent"
	elif (cmLength > 20):
		returnString = "Third cousins once removed or equivalent"
	elif (cmLength > 10):
		returnString = "Fourth cousins or equivalent"
	elif (cmLength > 5):
		returnString = "Fourth cousins once removed or equivalent"
	elif (cmLength > 2):
		returnString = "Fifth cousins or equivalent"
	elif (cmLength > 1):
		returnString = "Fifth cousins once removed or equivalent"
	elif (cmLength > 0.5):
		returnString = "Sixth cousins or equivalent"
	else:
		returnString = "Sixth cousins once removed or further"
	return returnString

#Default database login information
user_name = 'familinx'
password = 'familinx'
db_name = 'familinx'
db_connection = DBconnectBase(db_name, user_name, password)
if (len(sys.argv) <= 2):
	print "Invalid arguments"
else:
	if (sys.argv[1] == "-i" and len(sys.argv) >= 3):
		firstName = sys.argv[2]
		lastName = ""
		if (len(sys.argv) == 4):
			lastName = sys.argv[3]
		cur = db_connection.db_connection.cursor()
		cur.execute("SELECT Id FROM familinx.names WHERE GivenName = '" + firstName + "' AND Surname = '" + lastName + "'" )
		res = cur.fetchone()
		if res != None and res != ():
			res = res[0]
			print("Id = " + str(res))
		else:
			print("Person not found")
		cur.close()
	elif (sys.argv[1] == "-a" and len(sys.argv) >= 2):
		profileName = sys.argv[2]
		cur = db_connection.db_connection.cursor()
		cur.execute("SELECT Id FROM familinx.anonProfiles WHERE fileNameIn = '" + profileName + "'")
		res = cur.fetchone()
		if res != None and res != ():
			res = res[0]
			print("Id = " + str(res))
		else:
			print("Profile not found")
	elif (sys.argv[1] == "-c" and len(sys.argv) == 4):
		share = cms.cMShare()
		id1 = int(sys.argv[2])
		id2 = int(sys.argv[3])
		relationString = ""
		share.addIds(id1, id2)
		relationString = share.findIntermediateAncestors()
		dnaString = ""
		cur = db_connection.db_connection.cursor()
		cur.execute("SELECT chr, start, end, RoH FROM familinx.cMsharing WHERE (Id1 = " + str(id1) + " OR Id1 = " + str(id2) + ") AND (Id2 = " + str(id1) + " OR Id2 = " + str(id2) + ")")
		db_connection.db_connection.commit()
		res = cur.fetchall()
		if res != None and res != ():
			chrList = []
			startList = []
			endList = []
			RoHList = []
			for part in res:
				chrList.append(part[0])
				startList.append(part[1])
				endList.append(part[2])
				RoHList.append(part[3])
			dnaString = cMDescribe(chrList, startList, endList, RoHList)
		else:
			dnaString = "No DNA Connection"
		cur.close()
		print("Estimated pedigree relatedness: " + relationString)
		print("Estimated DNA relatedness: " + dnaString)
	elif (sys.argv[1] == "-r" and len(sys.argv) >= 3):
		rsid = sys.argv[2]
		isComplete = "1"
		if (len(sys.argv) == 4):
			if (sys.argv[3] == "-nc"):
				isComplete = "0"
		cur = db_connection.db_connection.cursor()
		if (isComplete == "0"):
			cur.execute("SELECT Id, FileName FROM familinx.genomes WHERE IsCouple = 0")
		else:
			cur.execute("SELECT Id, FileName FROM familinx.genomes WHERE IsCouple = 0 AND IsComplete = 1")
		db_connection.db_connection.commit()
		res = cur.fetchall()
		cur.close()
		idList = []
		fileList = []
		resultList = []
		if res != None and res != ():
			for part in res:
				idList.append(part[0])
				fileList.append(part[1])
			for File in fileList:
				openFile = open(File, 'r')
				found = False
				for line in openFile:
					if len(line) > len(rsid):
						if line[:len(rsid)] == rsid:
							line = line.strip()
							lineSet = line.split('\t')
							resultList.append(lineSet[3])
							found = True
							break
				if not found:
					resultList.append("")
				openFile.close()
			for i in range(len(resultList)):
				print("Id: " + str(idList[i]) + '\t' + "Result: " + resultList[i])
		else:
			print("No data found")
	elif (sys.argv[1] == "-p" and len(sys.argv) >= 5):
		position = sys.argv[2]
		if (sys.argv[3] == "-chr"):
			chrom = sys.argv[4]
			isComplete = "1"
			if (len(sys.argv) == 6):
				if (sys.argv[5] == "-nc"):
					isComplete = "0"
			cur = db_connection.db_connection.cursor()
			if (isComplete == "0"):
				cur.execute("SELECT Id, FileName FROM familinx.genomes WHERE IsCouple = 0")
			else:
				cur.execute("SELECT Id, FileName FROM familinx.genomes WHERE IsCouple = 0 AND IsComplete = 1")
			db_connection.db_connection.commit()
			res = cur.fetchall()
			cur.close()
			idList = []
			fileList = []
			resultList = []
			if res != None and res != ():
				for part in res:
					idList.append(part[0])
					fileList.append(part[1])
				for File in fileList:
					openFile = open(File, 'r')
					found = False
					for line in openFile:
						line = line.strip()
						lineSet = line.split('\t')
						if (lineSet[1] == chrom and lineSet[2] == position):
							resultList.append(lineSet[3])
							found = True
							break
					if not found:
						resultList.append("")
					openFile.close()
				for i in range(len(resultList)):
					print("Id: "  + str(idList[i]) + '\t' + "Result: " + resultList[i])
			else:
				print("No data found")
		else:
			print("Invalid arguments")
	elif (sys.argv[1] == "-h" and len(sys.argv) == 3):
		cur = db_connection.db_connection.cursor()
		cur.execute("SELECT Id1, Id2, chr, start, end, length, RoH FROM familinx.cMsharing WHERE Id1 = " + sys.argv[2] + " OR Id2 = " + sys.argv[2])
		db_connection.db_connection.commit()
		res = cur.fetchall()
		cur.close()
		if res != None and res != ():
			for part in res:
				print("Ids: " + str(part[0]) + " " + str(part[1]))
				print("Chromosome: " + part[2])
				print("Start position: " + str(part[3]))
				print("End position: " + str(part[4]))
				print("Total Length: " + str(part[5]))
				if (part[6] == 0):
					print("Not homozygous")
				else:
					print("Homozygous")
		else:
			print("No data found")
	elif (sys.argv[1] == "-d" and len(sys.argv) == 3):
		id1 = int(sys.argv[2])
		cur1 = db_connection.db_connection.cursor()
		cur1.execute("SELECT Id FROM familinx.genomes WHERE Id != " + str(id1) + " AND IsComplete = 1")
		db_connection.db_connection.commit()
		res1 = cur1.fetchall()
		if res1 != None and res1 != ():
			for part in res1:
				share = cms.cMShare()
				id2 = int(part[0])
				dnaString = ""
				cur = db_connection.db_connection.cursor()
				cur.execute("SELECT chr, start, end, RoH FROM familinx.cMsharing WHERE (Id1 = " + str(id1) + " OR Id1 = " + str(id2) + ") AND (Id2 = " + str(id1) + " OR Id2 = " + str(id2) + ")")
				db_connection.db_connection.commit()
				res = cur.fetchall()
				if res != None and res != ():
					chrList = []
					startList = []
					endList = []
					RoHList = []
					for part in res:
						chrList.append(part[0])
						startList.append(part[1])
						endList.append(part[2])
						RoHList.append(part[3])
					dnaString = cMDescribe(chrList, startList, endList, RoHList)
				else:
					dnaString = "No DNA Connection"
				cur.close()
				print("Estimated DNA relatedness to " + str(id2) + ": " + dnaString)
		cur1.close()

	else:
		print "Invalid arguments"			
