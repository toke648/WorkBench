import gensim

path = "./sgns.target.word-ngram.1-2.dynwin5.thr10.neg5.dim300.iter5.bz2.zip"
text = "你好，世界！"
model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=False)

print(model)