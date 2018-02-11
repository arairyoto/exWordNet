from nltk.corpus import wordnet as wn
from nltk.util import binary_search_file
import numpy as np

class exWordNetError(Exception):
    """An exception class for wordnet-related errors."""

def _relatedness(v_in, v_out):
    return sum(v_in*v_out)/np.sqrt(sum(v_in*v_in)*sum(v_out*v_out))

def search_line(f, key):
    for line in f.readlines():
        if line.find(key) >= 0:
            return line
        else:
            continue
    return None

class Word(object):
    # used in ambiguity which is for weighting function
    _DELTA = 0.65
    # used in association which is weight for shortest path shortest path distance
    # the bigger k is, the more specific associations may be appear
    _k = 0.5

    def __init__(self, exwordnet, name, pos, lang='eng'):
        self._exwordnet = exwordnet
        if name not in wn.all_lemma_names(pos=pos, lang=lang):
            raise exWordNetError('word %s.%s in %s is not defined in WordNet' % (name, pos, lang))

        self._name = name
        self._pos = pos
        self._lang = lang
        self._key = '%s.%s.%s' % (name, pos, lang)
        # self._vector = self.exwordnet._vector(self)

    def name(self):
        return self._name

    def pos(self):
        return self._pos

    def lang(self):
        return self._lang

    def synsets(self):
        return self._exwordnet.synsets(self._name, pos=self._pos, lang=self._lang)

    def lemmas(self):
        return self._exwordnet.lemmas(self._name, pos=self._pos, lang=self._lang)

    ###############################
    # Calc vector for the topic
    ###############################
    def vector(self, topic=None):
        if topic == None:
            vector = self._exwordnet.vector(self)
        else:
            vector = np.zeros(300)
            for l in self.lemmas():
                try:
                    vector += self._exwordnet.lemma_freq(l, topic)*self._exwordnet.vector(l)
                except exWordNetError:
                    continue

        if sum(vector*vector)==0:
            raise exWordNetError('vector for %r in %r is not properly calculated' % (self, topic))

        return vector

    ###############################
    # Calc AMBIGUITY
    ###############################
    def ambiguity(self, topic='general'):
        f = []
        for l in self.lemmas():
            f.append(self._exwordnet.lemma_freq(l, topic))
        try:
            f = np.array(f)/max(f)
            ambiguity = sum([np.power(v, self._DELTA)/(np.power(np.power(v, self._DELTA)+np.power((1-v), self._DELTA),1/self._DELTA)) for v in f])
            return ambiguity
        except ZeroDivisionError:
            raise exWordNetError('all frequency are 0 for %r' % self)

    ###############################
    # Calc TOPIC RELATEDNESS
    ###############################
    def topic_relatedness(self, topic):
        tv = self._exwordnet.topic_vector(topic)
        v = self.vector(topic=topic)
        return _relatedness(v, tv)

    ###############################
    # Calc ASSOCIATION
    ###############################
    def association(self, other, topic=None, index=False):
        rel = _relatedness(self.vector(topic=topic), other.vector(topic=topic))
        sps = []
        for s1 in self.synsets():
            for s2 in other.synsets():
                sp = s1.shortest_path_distance(s2)
                sps.append(sp)

        if len(sps)==0:
            raise exWordNetError('%r and %r are not connected' % (self, other))

        sp = min(sps)

        # return calculated index or just relatedness and shortest path distance
        if index:
            return rel*np.log(1+sp/self._k)
        else:
            return rel, sp


    def _related(self, relation_symbol=None):
        rws = []
        if relation_symbol == None:
            for s in self.synsets():
                for l in s.lemmas(lang=self._lang):
                    if l.name()!=self._name:
                        rws.append(l.name())
        else:
            for s in self.synsets():
                for ss in s._related(relation_symbol):
                    for l in ss.lemmas(lang=self._lang):
                        if l.name()!=self._name:
                            rws.append(l.name())

        return sorted(list(map(lambda x: Word(self._exwordnet, x, self._pos, lang=self._lang), list(set(rws)))))

    def __repr__(self):
        tup = type(self).__name__, self._key
        return "%s('%s')" % tup

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self._key == other._key

    def __ne__(self, other):
        return self._key != other._key

    def __lt__(self, other):
        return self._key < other._key

class exWordNet(object):
    """
    **FIRST, DEFINE ROOT FOR VECTOR and FREQ DATA FOLDER**

    extention of WordNet
    You can use WordNet method as usual WordNet

    following new method added
    * word(name, pos, lang)
      construct word object by name, pos, lang
    * words(name, lang)
      find possible words object by name, lang
    * all_words()
      iterator for all word objects which can be limited by pos
    * vector(obj)
      find vector for the object
    * lemma_freq(lemma, topic)
      find frequency for the lemma in the topic
    * topic_vector(topic)
      find vector for the topic

    """
    _TOPICS = ['general', 'automotive', 'fashion', 'music']

    def __init__(self, root):
        self._root = root

    def topics(self):
        return self._TOPICS

    def word(self, name, pos, lang='eng'):
        word = Word(self, name, pos, lang=lang)
        return word

    def lemma(self, name, lang='eng'):
        lemma = wn.lemma(name, lang=lang)
        # lemma._vector = self._vector(lemma)
        # lemma._freqs = {}
        # for t in self._TOPICS:
        #     lemma._freqs[t] = self._lemma_freq(lemma, t)
        return lemma

    def synset(self, name):
        synset = wn.synset(name)
        # synset._vector = self._vector(synset)
        return synset

    def words(self, name, lang='eng'):
        poss = []
        words = []
        for s in wn.synsets(name, lang=lang):
            poss.append(s.pos())
        for pos in list(set(poss)):
            word = Word(self, name, pos, lang=lang)
            words.append(word)
        return sorted(words)

    def synsets(self, lemma, pos=None, lang='eng'):
        synsets = wn.synsets(lemma, pos=pos, lang=lang)
        # for s in synsets:
        #     s._vector = self._vector(s)
        return synsets

    def lemmas(self, lemma, pos=None, lang='eng'):
        lemmas = wn.lemmas(lemma, pos=pos, lang=lang)
        # for l in lemmas:
        #     l._vector = self._vector(l)
        #     l._freqs = {}
        #     for t in self._TOPICS:
        #         l._freqs[t] = self._lemma_freq(l, t)
        return lemmas

    def all_synsets(self, pos=None):
        for synset in wn.all_synsets(pos=pos):
            # synset._vector = self._vector(synset)
            yield synset

    def all_words(self, pos=None, lang='eng'):
        if pos is None:
            pos_tags = ['n','v','a','r']
        else:
            pos_tags = [pos]

        for pos_tag in pos_tags:
            for l in wn.all_lemma_names(pos=pos_tag, lang=lang):
                word = Word(self, l, pos_tag, lang=lang)
                yield word

    ###############################
    # Load vector
    ###############################
    def vector(self, obj):
        """
        extract vector for the object
        the object could be Word, Synset, Lemma
        """
        obj_name = type(obj).__name__.lower()
        if obj_name == 'synset':
            _data_file = open('%s/synsets.txt' % self._root, 'r')
            line = binary_search_file(_data_file, obj._name)
        elif obj_name == 'lemma':
            tup = self._root, obj._lang
            _data_file = open('%s/%s/lemmas.txt' % tup, 'r')
            tup = obj._synset._name, obj._name
            line = binary_search_file(_data_file, '%s:%s' % tup)
        elif obj_name == 'word':
            tup = self._root, obj._lang
            _data_file = open('%s/%s/words.txt' % tup, 'r')
            line = binary_search_file(_data_file, obj._name)
        else:
            raise exWordNetError('%r is not WordNet Object' % obj)

        vector = self._vector_from_line(line)

        if sum(vector*vector)==0:
            raise exWordNetError('no vector for %r' % obj)

        return vector

    def _vector_from_line(self, line):
        """
        extract vector information from line
        if the object is not found in vector file, or the vector for the object is not properly learned,
        the returned vector would be zero vector
        """
        if line == None:
            return np.zeros(300)
        else:
            vector = np.array(list(map(float, line.strip().split()[1:])))
            return vector

    ###############################
    # Load frequency
    ###############################
    def lemma_freq(self, lemma, topic):
        """
        extract frequency of lemma in specific topic
        if the object is not found in the file,
        the returned frequency would be zero
        """
        # if wrong topic is entered, then raise error
        if topic not in self._TOPICS:
            raise exWordNetError('%s is not registered as a topic' % topic)

        _data_file = open('%s/%s/freq/freq.%s.txt' % (self._root, lemma._lang, topic), 'r')
        line = _data_file.readline()
        total = int(line.split(' ')[0])
        assert total > 0
        tup = lemma._synset._name, lemma._name
        line = binary_search_file(_data_file, '%s:%s' % tup)
        if line == None:
            return 0
        else:
            return int(line.strip().split(' ')[1])/total

    ###############################
    # Load topic vector
    ###############################
    def topic_vector(self, topic):
        """
        extract topic vector calculated as a frequency weighted lemma vector
        """
        if topic not in self._TOPICS:
            raise exWordNetError('%s is not registered as a topic' % topic)

        _data_file = open('%s/topics.txt' % self._root, 'r')

        line = binary_search_file(_data_file, topic)
        if line == None:
            raise exWordNetError('no topic vector for %s' % topic)
        else:
            return self._vector_from_line(line)

    ###############################
    # Vector calculation method
    ###############################
    def relatedness(self, obj_in, obj_out):
        vec_in = self.vector(obj_in)
        vec_out = self.vector(obj_out)
        return _relatedness(vec_in, vec_out)

    def _relatedness(self, vec_in, vec_out):
        return _relatedness(vec_in, vec_out)
    
    ###############################
    # Multilingual definitions
    ###############################
    # currently only adapt to Japanese
    def definition(self, synset, lang='eng'):
        if type(synset).__name__.lower() != 'synset':
            raise exWordNetError('%r is not synset' % synset)
        
        if lang == 'eng':
            return synset.definition()
        else:
            try:
                _data_file = open('%s/%s.definition.txt' % (self._root, lang) , 'r')
                key = '{:08d}-{}'.format(synset.offset(), synset.pos())
                line = search_line(_data_file, key)
                if line == None:
                    return 'None'
                # raise exWordNetError('no definition for %r' % synset)
                else:
                    return line.strip().split('|')[-1]
        except:
            raise exWordNetError('currently %s is not supported' % lang)

