README

CONTENTS
	REQUIREMENTS
	HOW TO RUN

REQUIREMENTS
	Python 2.6.5
	NumPy
	MySQLdb

HOW TO RUN
	DNAConnect.py
		To add a pedigree file to the database use:
			python DNAConnect.py -p pedigree.ged
		To add an anonymous genetic profile to the database:
			python DNAConnect.py -g genome.txt
		To add a connected genetic profile with a given id:
			python DNAConnect.py -g genome.txt -i id
	DNAQuery.py
		To get an id for a person:
			python DNAQuery.py -i FirstName LastName
		To get an id for an anonymous profile:
			python DNAQuery.py -a genome.txt
		To get a connection between two people based on genetic and/or pedigree data:
			python DNAQuery.py -c id1 id2
		To get the genotype for an rsid for all complete genomes in the database:
			python DNAQuery.py -r rsid
		To get the genotype for an rsid for all genomes (including incomplete):
			python DNAQuery.py -r rsid -nc
		To get the genotype for a given chromosome and position:
			python DNAQuery.py -p position -chr chrom
		To get the genotype for a given chromosome and position, including incomplete:
			python DNAQuery.py -p position -chr chrom -nc
		To get all runs of shared SNPs for a given individual:
			python DNAQuery.py -h id
		To get all DNA connections for an individual:
			python DNAQuery.py -d id
