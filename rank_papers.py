from __future__ import print_function
import codecs
import json
import os
import string
import sys
import urllib2
from collections import defaultdict
from operator import itemgetter
from pprint import pprint

# filtering adds ngrams for long keywords and lower()s everything
unfilteredfile = 'papers.json'
filteredfile = 'papers.ngrams.json'
filtered = False
papers = []


'''
# you can experiment with keyword extraction, it was worthless for me
def grab(fn,url):
  if not os.path.exists(fn):
    with open(fn,'w') as f:
      response = urllib2.urlopen(url)
      f.write(response.read())

grab('rake.py','https://raw.githubusercontent.com/zelandiya/RAKE-tutorial/master/rake.py')
grab('stoplist.txt','https://raw.githubusercontent.com/zelandiya/RAKE-tutorial/master/SmartStoplist.txt')

import rake
  
Rake = rake.Rake('stoplist.txt',max_words_length=1,min_keyword_frequency=2)
'''

# http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])


if not os.path.exists(filteredfile):
  # tolower all the keywords, 
  # and add bigrams and trigrams from 3+ and 4+ word keywords
  with open(unfilteredfile) as inf, open(filteredfile,'w') as outf:
    for line in inf.readlines():
      paper = json.loads(line.strip())
      updated_keywords = []
      for keyword in paper['keywords']:
        keyword = keyword.lower()
        updated_keywords.append(keyword)
        # use singletons, 2-grams, and 3-grams
        words = keyword.lower().split()
        if len(words) > 2:
          for item in find_ngrams(words,2):
            updated_keywords.append(' '.join(item))
        if len(words) > 3:
          for item in find_ngrams(words,3):
            updated_keywords.append(' '.join(item))
      paper['keywords'] = updated_keywords
      outf.write(json.dumps(paper) + "\n")

  

with open(filteredfile) as f:
  for line in f.readlines():
    papers.append(json.loads(line.strip()))

if not os.path.exists('interests.txt'):
  print("interest list not found - regenerating",file=sys.stderr)
  freqtable = defaultdict(int)

  for paper in papers:
      for keyword in paper['keywords']:
        freqtable[keyword] += 1

  with codecs.open('interests.txt','w',encoding='utf-8') as f:
    for item in sorted(freqtable.items(),key=itemgetter(1),reverse=True):
      f.write( "%s - %d occurrences\n" % item)

    print( "keyword frequencies dumped to interests.txt. Edit this file, delete keywords you don't like and keep keywords you like, and rerun this script.",file=sys.stderr)

else:
  print("keyword frequencies found - updating paper dump to include personal interest level and dumping them to stdout in descending interest order.",file=sys.stderr)
  # interest starts at 0. if line deleted, -1. if line remained, +1.
  desired = []
  with codecs.open('interests.txt',encoding='utf-8') as f:
    for line in f.readlines():
      desired.append(string.rsplit(line,maxsplit=3)[0])
  for paper in papers:
    interest = 0
    for keyword in paper['keywords']:
      if keyword in desired:
        interest += 1
      else:
        interest -= 1
    # normalize by number of keywords
    paper['interest'] = float(interest) / float(len(paper['keywords']))
  
  # dump normalized interests in case someone wants to inspect it offline
  with open(filteredfile,'w') as f:
    for paper in sorted(papers,key=lambda x: x['interest'],reverse=True):
      f.write(json.dumps(paper) + "\n")


  for paper in sorted(papers,key=lambda x: x['interest'],reverse=True):
    print("%s:\n\t%s" % (paper['number'],paper['title'].encode('ascii','ignore')))
    print("interest:\n\t%.2f" % paper['interest'])
    print("keywords:\n\t%s" % ", ".join(paper['keywords']).encode('ascii','ignore'))
    print("abstract:\n\t%s\n\n" % paper['abstract'].encode('ascii','ignore'))
