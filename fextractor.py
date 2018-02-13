# Python Version of WordNetExtractor.java
import os
import sys
#exWordNet
from exWordNet import exWordNet

import codecs

class ExtractorError(Exception):
    """An exception class for wordnet-related errors."""

wn = exWordNet('./')

def load_vector_line(file_name):
    model = {}
    f = open(file_name, 'r')
    for line in f.readlines():
        name = line.strip().split(' ')[0]
        vector_line = line.strip().split(' ')[1:]
        vector_line = ' '.join(vector_line)
        model[name] = vector_line
    return model

class ForwardWordNetExtractor:
    def __init__(self, root, lang):
        if lang in wn.langs():
            self.lang = lang
        else:
            raise ExtractorError("language: '%s' is not supported, try another language" % lang)
        self._root= root
        self.folder = '%s/%s' % (self._root, self.lang)
        # make directory for the language
        try:
            os.mkdir(self.folder)
        except:
            print('Folder %s already exists' % self.folder)
        # file name for synset vector
        self.file_name = '%s/words.txt' % self._root
        #initialize
        self.WordIndex = {}
        self.SynsetIndex = {}
        self.pos_list = ['a', 'r', 'n', 'v']
        self.pointer_map = {"@":"hypernym", "&":"similar", "$":"verbGroup", "!":"antonym"}

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
        synsetCounterAll = 0
        lexemCounter = 0
        lexemCounterAll = 0

        _wordCounter = {}
        _wordCounterAll = {}
        _synsetCounter = {}
        _synsetCounterAll = {}
        _lexemCounter = {}
        _lexemCounterAll = {}
        ovv = {}

        for pos in self.pos_list:
            _wordCounter[pos] = 0
            _wordCounterAll[pos] = 0
            _synsetCounter[pos] = 0
            _synsetCounterAll[pos] = 0
            _lexemCounter[pos] = 0
            _lexemCounterAll[pos] = 0
            ovv[pos] = []
            for synset in wn.all_synsets(pos=pos):
                synsetCounterAll += 1
                _synsetCounterAll[pos] += 1
                synsetId = synset.name()
                self.SynsetIndex[synsetId] = synsetCounterAll
                fSynsets.write('%s ' % synsetId)
                wordInSynset = 0
                for lemma in synset.lemmas():
                    lexemCounterAll += 1
                    _lexemCounterAll[pos] += 1
                    wordId = lemma.name()

                    if wordId in self.model.keys():
                        wordInSynset += 1
                        if wordId not in self.WordIndex:
                            fWords.write('%s %s\n' % (wordId, self.model[wordId]))
                            wordCounter += 1
                            _wordCounter[pos] += 1
                            self.WordIndex[wordId] = wordCounter

                        lexemCounter += 1
                        _lexemCounter[pos] += 1
                        lexemeId = '%s.%s' % (synset.name(), lemma.name())

                        fSynsets.write('%s,' % lexemeId)
                        fLexemes.write('%d %d\n' % (self.WordIndex[wordId], synsetCounterAll))

                    else:
                        if wordId not in oov[pos]:
                            ovv[pos].append(wordId)

                fSynsets.write('\n')
                if wordInSynset != 0:
                    synsetCounter += 1
                    _synsetCounter[pos] += 1
                else:
                    self.SynsetIndex[synsetId] = -1

            print("POS: %s" % pos)
            print("   Words: %d / %d\n" % (_wordCounter[pos], (_wordCounter[pos]+len(ovv[pos]))))
            print("  Synset: %d / %d\n" % (_synsetCounter[pos], _synsetCounterAll[pos]))
            print("  Lexems: %d / %d\n" % (_lexemCounter[pos], _lexemCounterAll[pos]))
        fWords.close()
        fSynsets.close()
        fLexemes.close()

    def extractWordRelations(self, filename, relation_symbol):
        affectedPOS = {}
        f = codecs.open(filename, 'w', 'utf-8')
        for pos in self.pos_list:
            for synset in wn.all_synsets(pos=pos):
                synsetId = synset.name()
                # get related words
                if relation_symbol == '!':
                    targetSynsets = []
                    for l in synset.lemmas():
                        for a in l.antonyms():
                            targetSynsets.append(a.synset())
                else:
                    targetSynsets = synset._related(relation_symbol)

                for targetSynset in targetSynsets:
                    pos = targetSynset.pos()
                    targetSynsetId = targetSynset.name()

                    if pos in affectedPOS:
                        affectedPOS[pos] += 1
                    else:
                        affectedPOS[pos] = 1

                    if snysetId in self.SynsetIndex and targetSynsetId in self.SynsetIndex:
                        if self.SynsetIndex[synsetId] >= 0 and self.SynsetIndex[targetSynsetId] >= 0:
                            f.write('%d %d\n' % (self.SynsetIndex[synsetId], self.SynsetIndex[targetSynsetId]))
                    else:
                        print(synsetId, targetSynsetId)
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
        fwne = ForwardWordNetExtractor(root, lang)
        fwne.main()

    #List of Languages
    #     ['als', 'arb', 'cat', 'cmn', 'dan', 'eng', 'eus', 'fas',
    # 'fin', 'fra', 'fre', 'glg', 'heb', 'ind', 'ita', 'jpn', 'nno',
    # 'nob', 'pol', 'por', 'spa', 'tha', 'zsm']
