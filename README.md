# exWordNet

## Description
WordNetの拡張です．基本的なWordNetの機能は使えます．

datafile：https://www.dropbox.com/sh/ckylez7t5x3ecm5/AAA7yizJ5CA3mF8nE5Teo2ARa?dl=0

datafileのfolderのパスをexWordNetの定義の時に指定してください．


**WordNetとの相違点（追加点）**
- Wordオブジェクトの追加

  Synset, Lemmaに加え，Wordオブジェクトを追加しました．

- ベクトルプロパティの追加

  Synset, Lemma, Wordそれぞれのオブジェクトにベクトルプロパティを追加しました．

- 頻度プロパティの追加

  Lemmaオブジェクトにはトピックごとの頻度情報を追加しました．

- トピックベクトルの追加

  トピックごとのトピックベクトルを追加しました．

### Word Object
Word Objectに定義されているプロパティとメソッドに関して説明します．
Word Objectは語・品詞・言語で特定します．

**Property**

- name

  語(e.g. "design")

- pos

  品詞(e.g. "n")

- lang

  言語(e.g. "eng")/WordNetでの言語名と同一

- synsets

  語と紐付くSynsetのリスト

- lemmas

  語と紐付くLemmaのリスト

**Method**

- vector(topic=None)

  語のトピックごとのベクトル表現を返します．topicに何も指定しないと，ジェネラルな語のベクトル表現を返します．

- ambiguity(topic='general')

  トピックごとの曖昧性を返します．topicに何も指定しないと，WordNetにもともと実装されているSemCor Corpusを元にした頻度情報による曖昧性の計算をします．

- topic relatedness(topic)

  トピックとの関連性を返します．トピックを必ず指定する必要があります．

- association(other, topic)

  トピックごとの当該Word Object(other)との連想関連指標を返します．topicに何も指定しないとジェネラルな語のベクトル表現で算出します．

### New Method for exWordNet
exWordNetに新たに追加したメソッドについて説明します．

- vector(obj)

  引数のObjectのベクトル表現を返します．ObjectとしてはSynset, Lemma, Word Objectが可能です．

- lemma_freq(lemma, topic)

  引数のlemmaの当該topic下での頻度情報を返します．頻度情報は，全体のlemmaの出現頻度数で割られており，正規化されています．

- topic_vector(topic)

  引数のtopicのトピックベクトル表現を返します．

- relatedness(obj_in, obj_out)

  引数のObject同士のベクトル表現によるコサイン類似度を算出します．

## How to Use

```
from exWordNet import exWordNet

exwn = exWordNet([root of data folder])

########################################
# same as normal wordnet
########################################

# definition of synset
synset = exwn.synset('design.n.01')
synsets = exwn.synsets('design')

# definition of lemma
lemma = exwn.lemmas('design')

# iterator
for synset in exwn.all_synsets(pos=[pos], lang=[lang]):
  ...

########################################
# new feature Word Object
########################################

# definition of word
exwn.word('design', 'n')
-> Word('design.n.eng')

exwn.words('design')
-> [Word('design.n.eng'),Word('design.v.eng')]

# iterator
for word in exwn.all_words(pos=[pos], lang=[lang]):
  ...

word = exwn.word('design','n') (=> Word('design.n.eng'))

word.name()
->'design'

word.pos()
->'n'

word.lang()
->'eng'

word.synsets()
->[Synset('design.n.01'), Synset('design.n.02'), Synset('blueprint.n.01'), Synset('design.n.04'), Synset('purpose.n.01'), Synset('design.n.06'), Synset('invention.n.01')]

word.lemmas()
->[Lemma('design.n.01.design'), Lemma('design.n.02.design'), Lemma('blueprint.n.01.design'), Lemma('design.n.04.design'), Lemma('purpose.n.01.design'), Lemma('design.n.06.design'), Lemma('invention.n.01.design')]

word.vector(topic='automotive')
->[  1.10705128e-05   1.98191884e-05   1.39555417e-05   9.93190906e-07
  -2.22414645e-05   1.99030851e-05   8.21694933e-06  

  ...

   3.69272634e-08  -8.30829140e-06  -2.96530259e-06  -2.12390994e-05]

word.ambiguity(topic='automotive')
->1.12806609165

word.topic_relatedness(topic='automotive')
->0.329674593626

other = exwn.word('fun','n')

word.association(other, topic='automotive')
->(0.26641401556350547, 4) % (relatedness, shortest path distance)

########################################
# new feature exWordNet
########################################
obj = Synset('design.n.01')
lemma = Lemma('design.n.01.design')

exwn.vector(obj)
->[ -7.66520000e-02  -6.46370000e-02  -4.26910000e-02   1.31290000e-02
   9.02590000e-02   2.69600000e-03   3.52740000e-02  

   ...

   2.47840000e-02  -1.24070000e-02  -4.05540000e-02   1.01210000e-01]

exwn.lemma_freq(lemma)
->2.414572427514536e-06

exwn.topic_vector('automotive')
->[  1.21331815e-03   6.99298846e-03  -4.08518871e-03   9.87208609e-03
  -5.81681535e-03   2.28192701e-03   3.73350873e-03  

  ...

   7.80417654e-04   2.82445540e-03   5.24175109e-03  -1.18144666e-03]

exwn.relatedness(obj, lemma)
->-0.128979924671
```
