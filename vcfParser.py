import sys

with open(sys.argv[1]) as file:
	outFile = open('NA12874.txt', 'w')
	for line in file:
		line = line.strip()
		if (line[0] != '#'):
			row = line.split('\t')
			rsid = row[2]
			chrom = row[0]
			ref = row[3]
			alt = row[4]
			info = row[7]
			NA = row[65]
			colonCount = 0
			semicolonCount = 0
			pos = ""
			isG = False
			for char in info:
				if char == 'G':
					isG = True
				if char == ';':
					semicolonCount += 1
				if char == ':' and semicolonCount >= 4:
					colonCount += 1
				if colonCount >= 1 and isG and char != ':':
					if char == ';':
						break;
					pos += char
			allele1 = NA[0]
			allele2 = NA[2]
			allele = ""
			if allele1 == '0':
				allele += ref
			if allele1 == '1':
				allele += alt[0]
			if allele1 == '2':
				allele += alt[-1]
			if allele2 == '0':
				allele += ref
			if allele2 == '1':
				allele += alt[0]
			if allele2 == '2':
				allele += alt[-1]
			outFile.write(rsid + '\t' + chrom + '\t' + pos + '\t' + allele + '\n')
	outFile.close()


