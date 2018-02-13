# Python Version of WordNetExtractor.java
import os
import sys
#exWordNet
from exWordNet import exWordNet

import codecs

import util

class ExtractorError(Exception):
    """An exception class for wordnet-related errors."""

wn = exWordNet('./')

def load_vector_line(file_name):
    model = {}
    f = open(file_name, 'r')
    for line in f.readlines():
        name = line.strip().split(' ')[0]
        vector_line = ' '.join(line.strip().split[1:])
        model[name] = vector_line
    return model

class BackwardWordNetExtractor:
    def __init__(self, root, lang):
        if lang in wn.langs():
            self.lang = lang
        else:
            raise ExtractorError("language: '%s' is not supported, try another language" % lang)
        self._root= root
        self.folder = '%s/%s' % (self._root, self.lang)
        # make directory for the language
        os.mkdir(self.folder)
        # file name for synset vector
        self.file_name = '%s/synsets.txt' % self.folder
        #initialize
        self.WordIndex = {}
        self.SynsetIndex = {}
        self.pos_list = ['a', 'r', 'n', 'v']
        self.pointer_map = {"@":"hypernym", "&":"similar", "$":"verbGroup", "!":"antonym", None:"synonym"}

    def main(self):
        # Load vector line
        self.model = load_vector_line(self.file_name)
        ver = wn.get_version()
        print("RESOURCE: WN " + str(ver) + "\n")
        print("LANGUAGE: "+self.lang+"\n")
        print("VECTORS: " + self.file_name + "\n")
        print("TARGET: " + self.folder + "\n")
        self.extractWordsAndSynsets(self.folder + "/words.txt",self.folder + "/synsets.txt",self.folder + "/lexemes.txt")
        self.extractWordRelations(self.folder + "/hypernym.txt", '@')
        self.extractWordRelations(self.folder + "/similar.txt",  '&')
        self.extractWordRelations(self.folder + "/synonym.txt",  None)
        self.extractWordRelations(self.folder + "/verbGroup.txt",  '$')
        self.extractWordRelations(self.folder + "/antonym.txt",  '!')

        print("DONE")


    def extractWordsAndSynsets(self, filenameWords, filenameSynsets,  filenameLexemes):
        #file
        fWords = codecs.open(filenameWords, 'w', 'utf-8')
        fSynsets = codecs.open(filenameSynsets, 'w',  'utf-8')
        fLexemes = codecs.open(filenameLexemes, 'w',  'utf-8')

        wordCounter = 0
        wordCounterAll = 0
        synsetCounter = 0
        lexemCounter = 0
        lexemCounterAll = 0

        wordCounter = {}
        wordCounterAll = {}
        synsetCounter = {}
        lexemCounter = {}
        lexemCounterAll = {}
        ovv = {}

        for pos in self.pos_list:
            wordCounter[pos] = 0
            wordCounterAll[pos] = 0
            synsetCounter[pos] = 0
            lexemCounter[pos] = 0
            lexemCounterAll[pos] = 0
            ovv[pos] = []
            for word in wn.all_words(pos=pos, lang=self.lang):
                wordCounterAll += 1
                wordCounterAll[pos] += 1
                wordId = '%s.%s' % (word.name(), word.pos())
                self.WordIndex[wordId] = wordCounterAll
                fWords.write('%s ' % wordId)
                synsetInWord = 0
                for synset in word.synsets():
                    lexemCounterAll += 1
                    lexemCounterAll[pos] += 1
                    synsetId = synset.name()

                    if synsetId in self.model.keys():
                        synsetInWord += 1
                        if synsetId not in self.SynsetIndex:
                            fSynsets.write('%s %s\n' % (synsetId, self.model[synsetId]))
                            synsetCounter += 1
                            synsetCounter[pos] += 1
                            self.SynsetIndex[synsetId] = synsetCounter

                        lexemCounter += 1
                        lexemCounter[pos] += 1
                        lexemeId = '%s.%s' % (synset.name(), word.name())

                        fWords.write('%s,' % lexemeId)
                        fLexemes.write('%d %d\n' % (self.SynsetIndex[synsetId], wordCounterAll))

                    else:
                        if synsetId not in oov[pos]:
                            ovv[pos].append(synsetId)

                fWords.write('\n')
                if synsetInWord != 0:
                    wordCounter += 1
                    wordCounter[pos] += 1
                else:
                    self.WordIndex[word] = -1

            print("POS: %s" % pos)
            print("   Words: %d / %d\n" % (wordCounter[pos], wordCounterAll[pos]))
            print("  Synset: %d / %d\n" % (synsetCounter[pos], synsetCounter[pos] + len(ovv[pos])))
            print("  Lexems: %d / %d\n" % (lexemCounter[pos], lexemCounterAll[pos]))
        fWords.close()
        fSynsets.close()
        fLexemes.close()

    def extractWordRelations(self, filename, relation_symbol):
        affectedPOS = {}
        f = codecs.open(filename, 'w', 'utf-8')
        for pos in self.pos_list:
            for word in wn.all_words(pos=pos):
                wordId = '%s.%s' % (word.name(), word.pos())
                # get related words
                if relation_symbol == None:
                    targetWords = word._related()
                else:
                    targetWords = word._related(relation_symbol)

                for targetWord in targetWords:
                    pos = targetWord.pos()
                    targetwordId = '%s.%s' % (targetWord.name(), targetWord.pos())

                    if pos in affectedPOS:
                        affectedPOS[pos] += 1
                    else:
                        affectedPOS[pos] = 1

                    if wordId in self.WordIndex and targetWordId in self.WordIndex:
                        if self.WordIndex[wordId] >= 0 and self.WordIndex[targetWordId] >= 0:
                            f,write('%d %d\n' % (self.WordIndex[wordId], self.WordIndex[targetWordId]))
                    else:
                        print(wordId, targetWordId)
        f.close()
        print("Extracted %s: done!\n" % self.pointer_map[relation_symbol])

        for k,v in affectedPOS.items():
            print("  %s: %d\n" % (k, v))

if __name__ == '__main__':
    # get root
    root = sys.argv[1]
    # get languages
    langs = sys.argv[2:]

    for lang in langs:
        bwne = BackwardWordNetExtractor(root, lang)
        bwne.main()

    #List of Languages
    #     ['als', 'arb', 'cat', 'cmn', 'dan', 'eng', 'eus', 'fas',
    # 'fin', 'fra', 'fre', 'glg', 'heb', 'ind', 'ita', 'jpn', 'nno',
    # 'nob', 'pol', 'por', 'spa', 'tha', 'zsm']
