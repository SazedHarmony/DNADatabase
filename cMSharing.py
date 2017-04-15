import sys
import traceback
import MySQLdb as mdb

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

class PedigreePerson():
	def __init__(self):
		self.user_name = 'familinx'
		self.password = 'familinx'
		self.db_name = 'familinx'
		self.db_connection = DBconnectBase(self.db_name, self.user_name, self.password)
		self.gen0 = 0;
		self.gen1 = [];
		self.gen2 = [];
		self.gen3 = [];
		self.gen4 = [];
		self.gen5 = [];
		self.gen6 = [];
		self.gen7 = [];
		self.gen8 = [];
		self.gen9 = [];
		self.gen10 = [];
		self.genDict = {1: self.gen1, 2: self.gen2, 3: self.gen3, 4: self.gen4, 5: self.gen5, 6: self.gen6, 7: self.gen7, 8: self.gen8, 9: self.gen9, 10: self.gen10}
	
	def getGenerations(self, iD):
		self.gen0 = iD
		self.genDict[0] = [iD]
		i = 0
		while (i != 11):
			i += 1
			if (i == 1):
				cur = self.db_connection.db_connection.cursor()
				cur.execute("SELECT Parent_id FROM familinx.relationship WHERE Child_id = " + str(iD))
				self.db_connection.db_connection.commit()
				res = cur.fetchall()
				cur.close()
				if res != ():
					for tup in res:
						self.genDict[1].append(tup[0])
				else:
					break
			else:
				totalList = []
				for person in self.genDict[i - 1]:
					cur = self.db_connection.db_connection.cursor()
					cur.execute("SELECT Parent_id FROM familinx.relationship WHERE Child_id = " + str(person))
					self.db_connection.db_connection.commit()
					res = cur.fetchall()
					cur.close()
					if res != ():
						for tup in res:
							totalList.append(tup[0])
				self.genDict[i] = totalList
	
	def getGeneration(self, gen):
		return self.genDict[gen]

class cMShare():
	def __init__(self):
		self.user_name = 'familinx'
		self.password = 'familinx'
		self.db_name = 'familinx'
		self.db_connection = DBconnectBase(self.db_name, self.user_name, self.password)
		self.file1Name = ""
		self.file2Name = ""
		self.id1 = 0
		self.id2 = 0
	
	def addIds(self, id1, id2):
		self.id1 = id1
		self.id2 = id2

	def addFiles(self, fileName1, fileName2):
		self.file1Name = fileName1
		self.file2Name = fileName2
		self.checkSharing()

	def getStatus(self, genotype):
		outputString = ""
		if (len(genotype) == 1):
			outputString = "hem" + genotype
		else:
			if (genotype[0] == genotype[1]):
				outputString = "hom" + genotype[0]
			else:
				outputString = genotype + genotype[::-1]
		return outputString

	def getPaths(self, visited, currentNodePaths):
		currentVisited = []
		toAddPaths = []
		for path in currentNodePaths:
			cur = self.db_connection.db_connection.cursor()
			cur.execute("SELECT Parent_id, Child_id FROM familinx.relationship WHERE Parent_id = " + str(path[-1]) + " OR Child_id = " + str(path[-1]))
			self.db_connection.db_connection.commit()
			res = cur.fetchall()
			if res != None and res != ():
				for part in res:
					parent = part[0]
					child = part[1]
					if parent == path[-1]:
						if child not in visited:
							newPath = []
							for iD in path:
								newPath.append(iD)
							newPath.append(child)
							currentVisited.append(child)
							if newPath not in toAddPaths:
								toAddPaths.append(newPath)
					else:
						if parent not in visited:
							newPath = []
							for iD in path:
								newPath.append(iD)
							newPath.append(parent)
							currentVisited.append(parent)
							if newPath not in toAddPaths:
								toAddPaths.append(newPath)
			cur.close()
		for part in toAddPaths:
			currentNodePaths.append(part)
		for visit in currentVisited:
			visited.append(visit)
		return (visited, currentNodePaths)

	def getPedigreePath(self):
		cur = self.db_connection.db_connection.cursor()
		cur.execute("SELECT * FROM familinx.anonProfiles WHERE Id = " + str(self.id1) + " OR Id = " + str(self.id2))
		self.db_connection.db_connection.commit()
		res = cur.fetchall()
		cur.close()
		if res != ():
			return []
		visited = [long(self.id1)]
		startList = [long(self.id1)]
		paths = [startList]
		counter = 0
		while self.id2 not in visited and counter < 15:
			tuples = self.getPaths(visited, paths)
			visited = tuples[0]
			paths = tuples[1]
			counter += 1
		if counter == 15:
			return []
		pathsToReturn = []
		for path in paths:
			if (path[0] == long(self.id1) and path[-1] == long(self.id2)) or (path[0] == long(self.id2) and path[-1] == long(self.id1)):
				pathsToReturn.append(path)
		return pathsToReturn

	def findIntermediateAncestors(self):
		person1 = PedigreePerson()
		person2 = PedigreePerson()
		person1.getGenerations(self.id1)
		person2.getGenerations(self.id2)
		i = 0
		connections = []
		while (i < 11):
			geni = person1.getGeneration(i)
			for j in range(11):
				genj = person2.getGeneration(j)
				for genIDi in geni:
					for genIDj in genj:
						if genIDi == genIDj:
							connections.append((genIDi, i, j))
							break
			i += 1
		if len(connections) == 0:
			return "No Relations"
		result = connections[0]
		i = result[1]
		j = result[2]
		if i == 0 and j == 1:
			return "Parent"
		if i == 1 and j == 0:
			return "Child"
		if i == 0 and j == 2:
			return "Grandparent"
		if i == 2 and j == 0:
			return "Grandchild"
		if i == 1 and i == 1:
			return "Siblings"
		if i == 2 and j == 1:
			return "Aunt/Uncle"
		if i == 1 and j == 2:
			return "Niece/Nephew"
		if i == 0:
			return str(j - 2) + " Great-grandparent"
		if j == 0:
			return str(i - 2) + " Great-grandchild"
		cousinNumber = min(i, j) - 1
		removed = abs(i - j)
		returnStrings = str(cousinNumber) + " cousins"
		if (removed != 0):
			returnStrings = str(returnStrings) +  " " + str(removed) + " times removed"
		return returnStrings

	def addParentalHaplotype(self, parentId, lines, gender):
		parentGenome = str(parentId) + "genome.txt"
		parentFile = open(parentGenome, "a+")
		totalLines = parentFile.readlines()
		if (len(totalLines) == 0):
			for line in lines:
				parentFile.write(line)
		parentFile.close()
		cur = self.db_connection.db_connection.cursor()
		cur.execute("REPLACE INTO familinx.genomes (Id, FileName, IsCouple, IsComplete) VALUES (" + str(parentId) + ", '" + parentGenome + "', 0, 0)")
		self.db_connection.db_connection.commit()
		cur.close()
		cur = self.db_connection.db_connection.cursor()
		cur.execute("SELECT Parent_id FROM familinx.relationship t1 INNER JOIN familinx.gender t2 WHERE t1.Child_id = " + str(parentId) + " AND t1.Parent_id = t2.Id AND t2.Gender = " + str(gender))
		res = cur.fetchone()
		if res != None and res != ():
			newParentId = res[0]
			self.addParentalHaplotype(newParentId, lines, gender)
		cur.close()
		return


	def createPersonRelatives(self, iD, filename):
		selfGender = 0
		cur = self.db_connection.db_connection.cursor()
		cur.execute("SELECT Gender FROM familinx.gender WHERE Id = " + str(iD))
		self.db_connection.db_connection.commit()
		res = cur.fetchone()
		if res != None and res != ():
			selfGender = res[0]
		cur.close()
		cur = self.db_connection.db_connection.cursor()
		cur.execute("SELECT Parent_id, Gender FROM familinx.relationship t1 INNER JOIN familinx.gender t2 WHERE t1.Child_id = " + str(iD) + " AND t1.Parent_id = t2.Id")
		self.db_connection.db_connection.commit()
		res = cur.fetchall()
		parents = []
		genders = []
		parentFiles = []
		files = []
		cur.close()
		if res != None and res != ():
			for part in res:
				parents.append(part[0])
				genders.append(part[1])
				parentFile = str(part[0]) + "genome.txt"
				parentFiles.append(parentFile)
		else:
			parents.append(str(int(iD) + 1))
			parents.append(str(int(iD) + 2))
			genders = [1, 2]
			parentFile1 = parents[0] + "genome.txt"
			parentFile2 = parents[1] + "genome.txt"
			parentFiles = [parentFile1, parentFile2]
			cur = self.db_connection.db_connection.cursor()
			cur.execute("INSERT INTO familinx.names (Id, GivenName, Surname) VALUES (" + str(int(iD) + 1) + ", '" + iD + "Father', '" + iD + "')")
			cur.execute("INSERT INTO familinx.names (Id, GivenName, Surname) VALUES (" + str(int(iD) + 2) + ", '" + iD + "Mother', '" + iD + "')")
			cur.execute("INSERT INTO familinx.years (Id) VALUES (" + str(int(iD) + 1) + ")")
			cur.execute("INSERT INTO familinx.years (Id) VALUES (" + str(int(iD) + 2) + ")")
			cur.execute("INSERT INTO familinx.gender (Id, Gender) VALUES (" + str(int(iD) + 1) + ", 1)")
			cur.execute("INSERT INTO familinx.gender (Id, Gender) VALUES (" + str(int(iD) + 2) + ", 2)")
			cur.execute("INSERT INTO familinx.relationship (Child_id, Parent_id) VALUES (" + iD + ", " + str(int(iD) + 1) + ")")
			cur.execute("INSERT INTO familinx.relationship (Child_id, Parent_id) VALUES (" + iD + ", " + str(int(iD) + 2) + ")")
			self.db_connection.db_connection.commit()
			cur.close()
		file1 = open(filename, 'r')
		yChromLines = []
		mtLines = []
		for line in file1:
			line = line.strip()
			set1 = line.split('\t')
			rsid = set1[0]
			chrom = set1[1]
			posit = set1[2]
			genotype = set1[3]
			status = self.getStatus(genotype)
			if status[:3] == "hom":
				for file2 in parentFiles:
					filew = open(file2, 'a')
					filew.write(rsid + '\t' + chrom + '\t' + posit + '\t' + status[3] + '\n')
					filew.close()
			if chrom == "MT":
				for i in range(len(parents)):
					if (genders[i] == 2):
						filew = open(parentFiles[i], 'a')
						mtString = rsid + '\t' + chrom + '\t' + posit + '\t' + status[3] + '\n'
						mtLines.append(mtString)
						filew.write(mtString)
						filew.close()
			if chrom == "Y" and selfGender == 1:
				for i in range(len(parents)):
					if (genders[i] == 1):
						filew = open(parentFiles[i], 'a')
						yString = rsid + '\t' + chrom + '\t' + posit + '\t' + status[3] + '\n'
						yChromLines.append(yString)
						filew.write(yString)
						filew.close()
			if chrom == "X" and status[:3] == "hem":
				for i in range(len(parents)):
					if (genders[i] == 2):
						filew = open(parentFiles[i], 'a')
						filew.write(rsid + '\t' + chrom + '\t' + posit + '\t' + status[3] + '\n')
						filew.close()
		cur = self.db_connection.db_connection.cursor()
		for i in range(len(parentFiles)):
			cur.execute("REPLACE INTO familinx.genomes (Id, FileName, IsCouple, IsComplete) VALUES (" + str(parents[i]) + ", '" + parentFiles[i] + "', 0, 0)")
		self.db_connection.db_connection.commit()
		cur.close()
		for i in range(len(parentFiles)):
			if (genders[i] == 1) and selfGender == 1:
				cur = self.db_connection.db_connection.cursor()
				cur.execute("SELECT Parent_id FROM familinx.relationship t1 INNER JOIN familinx.gender t2 WHERE t1.Child_Id = " + str(parents[i]) + " AND t1.Parent_id = t2.Id AND t2.Gender = 1")
				self.db_connection.db_connection.commit()
				res = cur.fetchone()
				cur.close()
				if res != None and res != ():
					self.addParentalHaplotype(res[0], yChromLines, 1)
			if (genders[i] == 2):
				cur = self.db_connection.db_connection.cursor()
				cur.execute("SELECT Parent_id FROM familinx.relationship t1 INNER JOIN familinx.gender t2 WHERE t1.Child_Id = " + str(parents[i]) + " AND t1.Parent_id = t2.Id AND t2.Gender = 2")
				self.db_connection.db_connection.commit()
				res = cur.fetchone()
				cur.close()
				if res != None and res != ():
					self.addParentalHaplotype(parents[i], mtLines, 2)
	
	def checkSharing(self):
		file1 = open(self.file1Name, 'r')
		file2 = open(self.file2Name, 'r')
		line1 = file1.readline()
		line2 = file2.readline()
		roh = False
		cMshareList = []
		currentRun = 0
		rohRun = 0
		startPosition = 0
		currentChr = "1"
		paths = self.getPedigreePath()
		fileShareSet = []
		commitShareSet = []
		discordantAllowed = 0
		while line1 and line2:
			line1 = line1.strip()
			line2 = line2.strip()
			line1set = line1.split('\t')
			line2set = line2.split('\t')
			if (currentChr != line1set[1] and line1set[1] == line2set[1]):
				if (currentRun >= 100):
					if rohRun >= 100:
						roh = True
					distance = int(line1set[2]) - startPosition
					addTuple = (currentChr, startPosition, int(line2set[2]), currentRun, distance, roh)
				currentChr = line1set[1]
				rohRun = 0
				currentRun = 0
				startPosition = 0
				roh = False
			if (line1set[1] == line2set[1] and len(line1set) == 4 and len(line2set) == 4 and line1set[2] != '' and line2set[2] != ''):
				currentChr = line1set[1]
				if (int(line1set[2]) == int(line2set[2])):
					line1 = file1.readline()
					line2 = file2.readline()
					status1 = self.getStatus(line1set[3])
					status2 = self.getStatus(line2set[3])
					if (status1[:3] == "hom" and status2[:3] == "hom" and status1[3] != status2[3]):
						if (currentRun >= 100) and discordantAllowed == 1:
							if rohRun >= 100:
								roh = True
							distance = int(line1set[2]) - startPosition
							addTuple = (line1set[1], startPosition, int(line1set[2]), currentRun, distance, roh)
							cMshareList.append(addTuple)
							discordantAllowed = 0
							for lineShare in fileShareSet:
								commitShareSet.append(lineShare)
						elif discordantAllowed == 0:
							discordantAllowed += 1
						del fileShareSet[:]
						rohRun = 0
						currentRun = 0
						startPosition = 0
						roh = False
					elif (status1[:3] == "hem" and (status2[:3] == "hem" or status2[:3] == "hom") and status1[3] != status2[3]):
						if (currentRun >= 100) and discordantAllowed == 1:
							if rohRun >= 100:
								roh = True
							distance = int(line1set[2]) - startPosition
							addTuple = (line1set[1], startPosition, int(line1set[2]), currentRun, distance, roh)
							cMshareList.append(addTuple)
							discordantAllowed = 0
							for lineShare in fileShareSet:
								commitShareSet.append(lineShare)
						elif discordantAllowed == 0:
							discordantAllowed += 1
						del fileShareSet[:]
						rohRun = 0
						currentRun = 0
						startPosition = 0
						roh = False
					elif (status1[:3] == "hom" and status2[:3] == "hem" and status1[3] != status2[3]):
						if (currentRun >= 100) and discordantAllowed == 1:
							if rohRun >= 100:
								roh = True
							distance = int(line1set[2]) - startPosition
							addTuple = (line1set[1], startPosition, int(line1set[2]), currentRun, distance, roh)
							cMshareList.append(addTuple)
							discordantAllowed = 0
							for lineShare in fileShareSet:
								commitShareSet.append(lineShare)
						elif discordantAllowed == 0:
							discordantAllowed += 1
						del fileShareSet[:]
						rohRun = 0
						currentRun = 0
						startPosition = 0
						roh = False
					elif (status1[:3] == "hom" and status2[:3] == "hom" and status1[3] == status2[3]):
						if startPosition == 0:
							startPosition = int(line1set[2])
						rohRun += 1
						currentRun += 1
						addLine = line1set[0] + '\t' + line1set[1] + '\t' + line1set[2] + '\t' + status1[3] + '\n'
						fileShareSet.append(addLine)
					elif (status1[:3] == "hom" and (status2[3] == status1[3] or status2[2] == status1[3])):
						if startPosition == 0:
							startPosition = int(line1set[2])
						currentRun += 1
						addLine = line1set[0] + '\t' + line1set[1] + '\t' + line1set[2] + '\t' + status1[3] + '\n'
						fileShareSet.append(addLine)
					elif (status2[:3] == "hom" and (status1[3] == status2[3] or status1[2] == status1[3])):
						if startPosition == 0:
							startPosition = int(line1set[2])
						currentRun += 1
						addLine = line1set[0] + '\t' + line1set[1] + '\t' + line1set[2] + '\t' + status2[3] + '\n'
						fileShareSet.append(addLine)
					elif (status1[:3] == "hem" and status2[:3] == "hem" and status1[3] == status2[3]):
						if startPosition == 0:
							startPosition = int(line1set[2])
						currentRun += 1
					elif (status1[:2] == status2[:2] or status1[:2] == status2[2:]):
						if startPosition == 0:
							startPosition = int(line1set[2])
						currentRun += 1
					elif (status1[0] == status2[0] or status1[0] == status2[1]):
						if startPosition == 0:
							startPosition = int(line1set[2])
						currentRun += 1
						addLine = line1set[0] + '\t' + line1set[1] + '\t' + line1set[2] + '\t' + status1[0] + '\n'
						fileShareSet.append(addLine)
					else:
						if (currentRun >= 100) and discordantAllowed == 1:
							if rohRun >= 100:
								roh = True
							distance = int(line1set[2]) - startPosition
							addTuple = (line1set[1], startPosition, int(line1set[2]), currentRun, distance, roh)
							cMshareList.append(addTuple)
							discordantAllowed = 0
							for lineShare in fileShareSet:
								commitShareSet.append(lineShare)
						elif discordantAllowed == 0:
							discordantAllowed += 1
						del fileShareSet[:]
						rohRun = 0
						currentRun = 0
						startPosition = 0
						roh = False
				elif (int(line1set[2]) > int(line2set[2])):
					line2 = file2.readline()
				else:
					line1 = file1.readline()
			else:
				if (line1set[2] != '' and line2set[2] != '' and int(line1set[2]) > int(line2set[2])):
					line1 = file1.readline()
					if (currentRun >= 100):
						if rohRun >= 100:
							roh = True
						distance = int(line1set[2]) - startPosition
						addTuple = (line1set[1], startPosition, int(line1set[2]), currentRun, distance, roh)
						cMshareList.append(addTuple)
						discordandAllowed = 0
						for lineShare in fileShareSet:
							commitShareSet.append(lineShare)
					del fileShareSet[:]
					rohRun = 0
					currentRun = 0
					startPosition = 0
					roh = False
					
				elif (line1set[2] != '' and line2set[2] != ''):
					line2 = file2.readline()
					if (currentRun >= 100):
						if rohRun >= 100:
							roh = True
						distance = int(line2set[2]) - startPosition
						addTuple = (line2set[1], startPosition, int(line2set[2]), currentRun, distance, roh)
						cMshareList.append(addTuple)
						discordantAllowed = 0
						for lineShare in fileShareSet:
							commitShareSet.append(lineShare)
					del fileShareSet[:]
					rohRun = 0
					currentRun = 0
					startPosition = 0
					roh = False
				else:
					line1 = file1.readline()
					line2 = file2.readline()
		if len(paths) > 0:
			shareIds = []
			couple = []
			if len(paths) == 2:
				firstPath = paths[0]
				secondPath = paths[1]
				for i in range(len(firstPath)):
					if firstPath[i] == secondPath[i] and (firstPath[i] != self.id1 and firstPath[i] != self.id2):
						shareIds.append(firstPath[i])
					elif firstPath[i] != self.id1 and firstPath[i] != self.id2:
						couple.append(firstPath[i])
						couple.append(secondPath[i])
			for iD in shareIds:
				parentGenome = str(iD) + "genome.txt"
				parentFile = open(parentGenome, "a+")
				for line in commitShareSet:
					lineSet = line.split('\t')
					if lineSet[1] != "MT" and lineSet[1] != "Y":
						parentFile.write(line)
				parentFile.close()
				cur = self.db_connection.db_connection.cursor()
				cur.execute("REPLACE INTO familinx.genomes (Id, FileName, IsCouple, IsComplete) VALUES (" + str(iD) + ", '" + parentGenome + "', 0, 0)")
				self.db_connection.db_connection.commit()
				cur.close()
			if len(couple) != 0:
				coupleGenome = str(couple[0]) + '-' + str(couple[1]) + "genome.txt"
				coupleFile = open(coupleGenome, "a+")
				for line in commitShareSet:
					lineSet = line.split('\t')
					if lineSet[1] != "MT" and lineSet[1] != "Y":
						coupleFile.write(line)
				coupleFile.close()
				cur = self.db_connection.db_connection.cursor()
				cur.execute("REPLACE INTO familinx.genomes (Id, FileName, IsCouple, IsComplete) VALUES (" + str(couple[0]) + str(couple[1]) + ", '" + coupleGenome + "', 1, 0)")
				self.db_connection.db_connection.commit()
				cur.close()
		cur = self.db_connection.db_connection.cursor()
		for share in cMshareList:
			rohStr = ""
			if (share[5]):
				rohStr = "1"
			else:
				rohStr = "0"
			cur.execute("INSERT INTO familinx.cMsharing (Id1, Id2, chr, start, end, length, RoH) VALUES (" + str(self.id1) + ", " + str(self.id2) + ", '" + share[0] + "', " + str(share[1]) + ", " + str(share[2]) + ", " + str(share[3]) + ", " + rohStr + ")")
		self.db_connection.db_connection.commit()
		cur.close()
