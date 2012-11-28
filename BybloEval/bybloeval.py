#~ !/usr/bin/env python -c

#~ Copyright (c) 2012, University of Sussex
#~ All rights reserved.

#~ Redistribution and use in source and binary forms, with or without 
#~ modification, are permitted provided that the following conditions are met:

 #~ * Redistributions of source code must retain the above copyright notice, this
   #~ list of conditions and the following disclaimer.

 #~ * Redistributions in binary form must reproduce the above copyright notice, 
   #~ this list of conditions and the following disclaimer in the documentation 
   #~ and/or other materials provided with the distribution.

 #~ * Neither the name of the University of Sussex nor the names of its 
   #~ contributors may be used to endorse or promote products  derived from this
   #~ software without specific prior written permission.

#~ THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#~ AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
#~ IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#~ DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, 
#~ INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#~ BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#~ DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
#~ OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
#~ NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
#~ EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#~ -----------------------------------------------------------------------------
__author__ = "Joanne Robert"
__copyright__ = "Copyright (c) 2012, University of Sussex"
__credits__ = ["Joanne Robert", "Hamish Morgan"]
__license__ = "3-clause BSD"
__version__ = "1.1.0"
__maintainer__ = "Joanne Robert"
__email__ = "jr317@sussex.ac.uk"
__status__ = "Development"
#~ -----------------------------------------------------------------------------

import sys
import argparse
import time
import string
import stat
import os
## needed?
#~ import math
#~ from nltk.corpus import wordnet as wn, wordnet_ic as wn_ic
#~ from operator import itemgetter, attrgetter


## Lin's WordNet similarity function
def linWordnetSimilarity(word1, word2):
		return max([wn.lin_similarity(synset1, synset2, ic) \
				for synset1 in wn.synsets(word1) \
				for synset2 in wn.synsets(word2) \
				if synset1.pos == synset2.pos \
				and synset1.pos in ic and synset2.pos in ic])


class BybloEval:
	
	"""
	Compute the percentage of similarity between two thesauri
	"""
	
	##Initialises the parameters of the module
	def __init__(self, inputFiles, outputFile, method, testIndex, maxRank, maxIndex, verbose):
		## input files containing the thesauri
		self.inputFiles = inputFiles
		## output file for comparison results
		self.outputFile = outputFile
		## measure used for neighbour set (i.e. thesaurus entry) comparison
		self.method = method
		## index for a single test entry
		self.testIndex = testIndex
		## maximum neighbour rank
		self.maxRank = maxRank
		## maximum entry index
		self.maxIndex = maxIndex
		## verbose option
		self.verbose = verbose
	
	
	## Runs the comparison between two thesauri
	def run(self):
		
		## start operations
		stime = time.time()
		print "***************************************************************************"
		print "THESAURUS COMPARISON TOOL"
		print "***************************************************************************\n"
		
		## read files
		print "[1] Extracting words from input files\n"
		thesauri = [self.extractTerms(f) for f in self.inputFiles]
		names = [f.name for f in self.inputFiles]
		if len(self.inputFiles) == 1:
			thesauri.append(self.createWordnetThesaurus(thesauri[0], a.method))
			names.append("WordNet")
		
		## verify extracted information
		for th, name in zip(thesauri, names):
			print_lines(th, max=10, line_max=75, title="\""+name+"\" after sort:")
			print '\n'
		
		## compare one entry as a test
		print "\n[2] Comparing neighbour sets for test index"  + str(self.testIndex) + "\n"
		#~ set1, set2 = [th[a.testIndex] for th in thesauri]
		#~ sim_score1 = {
			  #~ 'Lin'	: 	neighbour_set_sim_lin(set1, set2, verbose=a.verbose),
			  #~ 'rank': 	neighbour_set_sim_rank(set1, set2, verbose=a.verbose)
		#~ }[a.method]
		#~ print "\nSimilarity score: ", sim_score1, "\n"
		
		## compare thesauri
		print "\n[3] Comparing thesauri\n" 
		#~ with open(a.outputFile, 'w') as output:
			#~ sim_score2 = thesaurus_sim(thesauri, a.method, n=a.n, verbose=a.verbose)
			#~ output.write(str(sim_score2) + '\t' + '\t'.join(names))
		#~ print "\nSimilarity score: ", sim_score2, "\n"

		etime = time.time()
		print "\n>Execution took", etime-stime, "seconds"   
	
	
	## Extracts thesaurus entries from a file
	## The entries are formatted as follows:
	##		term 	neighbour1	sim_score1	neighbour2	sim_score2	...	...
	##
	## When the similarity measure chosen for comparison between neighbour sets uses ranks,
	## similarity scores are replaced by their rank in the resultant array.
	## @return array representing a thesaurus
	def extractTerms(self, file):
		terms = []
		for line in file:
			fields = string.split(line, "\t")
			fields = fields[:(self.maxRank*2+1) if self.maxRank else None]
			
			## build tuples depending on method chosen
			if self.method == "Lin":
				line_terms = [(fields[i], float(fields[i+1])) for i in xrange(1, len(fields)) if i%2 == 1]
			elif self.method == "rank":
				line_terms = [(fields[i], i/2) for i in xrange(1, len(fields)) if i%2 == 1]
				
			line_terms.sort()
			line_terms = [fields[0]] + line_terms
			terms.append(line_terms)
		terms.sort()
		return terms
			

	
	## Creates a neighbour set from WordNet, using the terms already present in an existing neighbour set
	## When the similarity measure chosen for comparison between neighbour sets uses ranks,
	## similarity scores are replaced by their rank in the resultant array.
	## @return array representing a neighbour set
	def createWordnetNeighbourSet(self, originalSet, ic):
		## neighbour set creation
		word = originalSet[0]
		set = [(neighbour, linWordnetSim(word, neighbour)) 
			for (neighbour, val) in originalSet[1:] 
			if wn.synsets(neighbour)]
		
		## conversion to ranks when needed
		if self.method != "Lin":
			set.sort(key=itemgetter(1), reverse=True)
			set = [(neighbour, rank) for rank, (neighbour, val) in enumerate(set)]
		
		return [word] + sorted(set)


	## Creates a thesaurus from WordNet, using the terms already present in an existing thesaurus
	## @return array representing a neighbour set
	def createWordnetThesaurus(self, originalThesaurus):
		ic = wn_ic.ic('ic-brown.dat')
		#~ semcor_ic = wn_ic.ic('ic-semcor.dat')
		return [self.createWordnetNeighbour_set(set, ic) 
			for set in originalThesaurus if wn.synsets(set[0])]
			
###############################################################################		
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

##
##
def neighbour_set_sim_lin(set1, set2, k=None, max_sim_score=None, verbose=False):
	sim_score, pt1, pt2 = 0, 1, 1
	square_score = lambda x: x[1] * x[1]
	
	## determine maximum possible similarity score
	max_sim_score = sum([square_score(neighbour) for neighbour in set1[1:]]) \
		* sum([square_score(neighbour) for neighbour in set2[1:]])
	max_sim_score = math.sqrt(max_sim_score)
	
	## avoid division by zero
	if max_sim_score == 0:
		return 0
		
	while pt1 < len(set1) and pt2 < len(set2) :
		if set1[pt1][0] < set2[pt2][0]:
			pt1 += 1
			
		elif set1[pt1][0] > set2[pt2][0]:
			pt2 += 1
		
		else: # potential neighbour present in both sets
			score_product = set1[pt1][1]*set2[pt2][1]
			sim_score += score_product
			
			# what is happening?
			if verbose:
				print "["+str(pt1)+"]"+str(set1[pt1])
				print "["+str(pt2)+"]"+str(set2[pt2])
				print "\t=> "+str(score_product)
			
			pt1 += 1
			pt2 += 1
			
	return 1.0 * sim_score / max_sim_score

##
##
def neighbour_set_sim_rank(set1, set2, k=None, max_sim_score=None, verbose=False):
	sim_score, pt1, pt2 = 0, 1, 1
	
	## determine maximum rank distance if not passed
	if k == None:
		k = max(len(set1), len(set2)) - 1 # target word doesn't count
		
	## determine maximum similarity score if not passed
	if max_sim_score == None:
		max_sim_score = sum([i*i for i in xrange(1, k+1)])
		
	## avoid division by zero
	if max_sim_score == 0:
		return 0
	
	while pt1 < len(set1) and pt2 < len(set2) :
		if set1[pt1][0] < set2[pt2][0]:
			pt1 += 1
				
		elif set1[pt1][0] > set2[pt2][0]:
			pt2 += 1
			
		else: # potential neighbour present in both sets
			score_product = (k - set1[pt1][1])*(k - set2[pt2][1])
			sim_score += score_product
				
			# what is happening?
			if verbose:
				print "["+str(pt1)+"]"+str(set1[pt1])
				print "["+str(pt2)+"]"+str(set2[pt2])
				print "\t=> "+str(score_product)
			
			pt1 += 1
			pt2 += 1
			
	return 1.0 * sim_score / max_sim_score


##
##
def thesaurus_sim(th, method="rank", n=None, k=None, verbose=False):
	th1, th2 = th[0], th[1]
	global_sim_score, pt1, pt2 = 0, 0, 0
	fixed_k = (k != None)
	neighbour_set_sim = {
		'Lin'	: neighbour_set_sim_lin,
		'rank': neighbour_set_sim_rank,
	}[method]
	
	## determine maximum thesaurus size if not passed (n allows comparison on a subset)
	if n == None:
		n = max(len(th1), len(th2))
		
	## avoid division by zero
	if n == 0:
		return 0
	
	## determine a possible maximum rank distance if not passed
	if k == None:
		k = len(th1[0]) - 1
	
	## and a possible maximum neighbour set similarity score
	## (to avoid unneccessary computations of unchanged values)
	max_sim_score = sum([i*i for i in xrange(1, k+1)])
	
	while pt1 < n and pt2 < n and pt1 < len(th1) and pt2 < len(th2) :
		
		if th1[pt1][0] == th2[pt2][0]: # target word present in both sets
			l1, l2 = len(th1[pt1])-1, len(th2[pt2])-1
			
			if fixed_k and k <= l1 and k <= l2 or k == l1 == l2 :
				set_sim = neighbour_set_sim(th1[pt1], th2[pt2], k, max_sim_score)
			else:
				set_sim = neighbour_set_sim(th1[pt1], th2[pt2])
			global_sim_score += set_sim
			
			# what is happening?
			if verbose:
				print "th1[", pt1, "]", th1[pt1][0], ": th2[", pt2, "]", th2[pt2][0], \
				"=> ", set_sim
			
			pt1 += 1
			pt2 += 1
			
		elif th1[pt1][0] < th2[pt2][0]:
			pt1 += 1
		else:
			pt2 += 1
	return 1.0 * global_sim_score / n
	
	
## Prints an array with customizable start, end, line length and title
def print_lines(list, min=0, max=None, line_max=None, title="List"):
	if max is None:
		max = len(list)
	print title + "\n"
	for index in range(min, max):
		print str(list[index])[:line_max], "..."
	print "\n"
	

## Parses a command line
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Compare two thesauri.')
	
	## Forces one or two values exactly for an argument
	def required_length(nmin,nmax):
		class RequiredLength(argparse.Action):
			def __call__(self, parser, args, values, option_string=None):
				if not nmin<=len(values)<=nmax:
					msg='argument "{f}" requires between {nmin} and {nmax} arguments'.format( \
						f=self.dest,nmin=nmin,nmax=nmax)
					raise argparse.ArgumentTypeError(msg)
				setattr(args, self.dest, values)
				return RequiredLength

	## input files containing the thesauri
	parser.add_argument('inputFiles', metavar='file', type=file, nargs='+', \
		action=required_length(1, 2), \
		help='files containing the thesauri to compare (against WordNet if there is only one)')
	## output file for comparison results
	parser.add_argument('-o', '--output-file', metavar='file', dest='outputFile', 
		action='store', default="./result.thsim",
		help='output file in which similarity scores and file names will be written'+\
		'(default: "./result.thsim")')
	## measure used for neighbour set (i.e. thesaurus entry) comparison
	parser.add_argument('-l', '--Lin', metavar='string', dest='method', action='store_const', \
		const='Lin', default='rank', \
		help='method used to calculate the similarity between two neighbour sets')
	## index for a single test entry
	parser.add_argument('-i', '--test-index', metavar='n', type=int, dest='testIndex', \
		action='store', default=0, \
		help="index of a single word to compare as a test")
	## maximum neighbour rank
	parser.add_argument('-k', '--max-rank', metavar='n', type=int, dest='maxRank', \
		action='store', default=None, \
		help="maximum rank for neighbours to compare")
	## maximum entry index
	parser.add_argument('-n', '--max-index', type=int, dest='maxIndex', \
		action='store', default=None, \
		help="maximum index for entries to compare")
	## verbose option
	parser.add_argument('-v', '--verbose', dest='verbose', action='store_const', \
		const=True, default=False, \
		help="display information about each comparison")
		
	a = parser.parse_args()
	for item in vars(a):
		print item, ":", vars(a)[item]
	bybloEval = BybloEval(a.inputFiles, a.outputFile, a.method, a.testIndex, a.maxRank, a.maxIndex, a.verbose)
	bybloEval.run()
	
	
	