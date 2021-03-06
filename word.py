'''
Hopefully this code will just work so it will never have to be touched ever again.
It must've given me nightmares at least five times.
'''
import defs, re, time
from defs import *

def sanitizeParsedDictionary(dictionary):
    def cleanField(val):
        #must be string value at this point:

        #find '#' delimiters:
        if '#' in val:
            splittedItems = re.split("(\n)+#(?![*:{1,3}])", val)
            return [definition for definition in map(lambda x:cleanField(x.replace("#","")), splittedItems) if
                    len(definition)]
        val = val.replace("\n", "")
        val = val.replace("[", "")
        val = val.replace("]", "")
        return re.sub("'{1,5}", "", re.sub("={2,4}[A-Z][a-zA-z0-9 ]*={2,4}", "", val));

    if len(dictionary) == 1:
        return cleanField(dictionary[list(dictionary.keys())[0]])
    newDictionary = {}
    for key in dictionary:
        val = dictionary[key]
        newVal = ""
        #not great, but..
        if isinstance(val, dict):
            newVal = sanitizeParsedDictionary(val)
        elif isinstance(val, str):
            newVal = cleanField(val)
        if len(newVal) > 0:
            newDictionary[key] = newVal
    return newDictionary

class Word:
    def __init__(self, title, language, parsedDictionary={}):
        self.title = title;
        self.language = language;
        parsedDictionary = sanitizeParsedDictionary(parsedDictionary)
        if not isinstance(parsedDictionary, dict):
            print("word: ", title)
        self.content = parsedDictionary;
        self.content["title"] = title;
        self.content["language"] = language;
        self.hashValueDict = {"hashValue" :title+language};
        self.content["hashValue"] = title+language;
        self.wordTypes = [val for val in defs.wordTypes if val in parsedDictionary.keys()];
        self.content["type"] = self.wordTypes;
        if self.title[0:1] == "-":
            self.content["type"].append("Suffix")

    def __str__(self):
        return self.title;

    def toObject(self):
        self.content["modifiedTime"] = time.time()
        return self.content

def deserializeJSONWordObject(parsedDictionary):
    return Word(parsedDictionary["title"],parsedDictionary["language"],parsedDictionary)

#simple parser:
def parseWikiEntry(entryString):
    langdict = {};
    lastindex = 0;
    while(lastindex < len(entryString)):
        regexMatch = re.search("^==[A-Z][a-z]+==(\s|.)*?(----|\Z)", entryString[lastindex:], re.MULTILINE)
        if(regexMatch):
            #hardcoded:
            language = (re.search("^==[A-Z][a-z]+==",regexMatch.group(0)).group(0)[2:-2]);
            trailingChars = len(regexMatch.groups()[-1])
            langdict[language] = parseSectionEntry(entryString[lastindex+regexMatch.start(0):lastindex+regexMatch.end(0)-trailingChars])
            lastindex += (regexMatch.end(0) - trailingChars)
        else:
            break
    return langdict

def parseSectionsAndSubsections(entryString, delimiter, subsectionFunction, discardNonMatchingInfo = True):
    secDict = {};
    lastindex = 0;
    while(lastindex < len(entryString)):
        regexMatch = re.search("(^|\n)"+delimiter+"[A-Z][A-Za-z0-9 ]+"+delimiter+"[^=](\s|.)*?(^"+delimiter+"[A-Z]|\Z)", entryString[lastindex:], re.MULTILINE)
        if(regexMatch):
            #hardcoded:
            type = (re.search("(^|\n)"+delimiter+"[A-Z][A-Za-z0-9 ]+"+delimiter,regexMatch.group(0)).group(0)[len(delimiter):-1*len(delimiter)]).replace("=","")
            trailingChars = len(regexMatch.groups()[-1])
            secDict[type] = subsectionFunction(entryString[lastindex+regexMatch.start(0):lastindex+regexMatch.end(0)-trailingChars])
            if lastindex==0 and regexMatch.start(0)>0:
                secDict["content"]=entryString[0:regexMatch.start(0)]
            lastindex += (regexMatch.end(0) - trailingChars)
        else:
            if lastindex==0:
                secDict["content"]=entryString;
            break
    return secDict

def parseSectionEntry(entryString):
    return parseSectionsAndSubsections(entryString, "===", parseSubSectionEntry)


def parseSubSectionEntry(entryString):
    return parseSectionsAndSubsections(entryString, "====", lambda x:x)

#hamming distance from wikipedia
#url: https://en.wikipedia.org/wiki/Hamming_distance
def hamming_distance(s1, s2):
    """Return the Hamming distance between equal-length sequences"""
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))

#there's gotta be a better way to do this...
def suffix_match(a, b):
    a = list(reversed(list(str(a).lower())));
    b = list(reversed(list(str(b).lower())));
    matched_letters = 0;
    for i in range(len(a)):
        if i >= len(b):
            break;
        if a[i] == b[i]:
            matched_letters += 1;
        else:
            break;
    return matched_letters;

#modify vowel def when needed.
def suffix_match_vowels(a, b):
    a = list(reversed(list(str(a).lower())));
    b = list(reversed(list(str(b).lower())));
    matched_vowels = 0;
    for i in range(len(a)):
        if i >= len(b):
            break;
        if a[i] == b[i] and (a[i] in vowels):
            matched_vowels += 1;
        elif (a[i] in vowels) or (b[i] in vowels):
            break;
        else:
            #still counts, for ranking purposes
            matched_vowels += 1;
            continue;
    return matched_vowels;
#input: list
def rankBySuffix(words, target):
    return sorted(words, key = lambda word: suffix_match(word, target));
