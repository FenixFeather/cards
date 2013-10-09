#!/usr/bin/env python
import nltk
def generateWords(path,outPath):
    f = open(path,'r')
    text = f.readline()
    f.close()
#    for (i,word) in enumerate(text):
#        for c in ".[]1234567890\n":
#            text[i] = word.strip()
    text = nltk.pos_tag(nltk.tokenize.wordpunct_tokenize(text))
    nouns = open(outPath + "-nouns.txt",'a')
    verbs = open(outPath + "-adjs.txt",'a')
    for pair in text:
        if "NN" in pair[1]:
            nouns.write(pair[0]+"\n")
        elif "JJ" in pair[1]:
            verbs.write(pair[0]+"\n")
    nouns.close()
    verbs.close()
    
if __name__=="__main__":
    generateWords("source.txt","test")
    
    
            
    
        
    
