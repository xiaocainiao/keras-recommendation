# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from .data_utils import get_file
import string
import random
import os
from six import *
import numpy as np

def make_reuters_dataset(path=os.path.join('datasets', 'temp', 'reuters.pkl'), min_samples_per_topic=15):
    import re
    from ..preprocessing.text import Tokenizer

    wire_topics = []
    topic_counts = {}
    wire_bodies = []

    for fname in os.listdir(path):
        if 'sgm' in fname:
            s = open(path + fname).read()
            tag = '<TOPICS>'
            while tag in s:
                s = s[s.find(tag)+len(tag):]
                topics = s[:s.find('</')]
                
                if topics and not '</D><D>' in topics:
                    topic = topics.replace('<D>', '').replace('</D>', '')
                    wire_topics.append(topic)
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                else:
                    continue

                bodytag = '<BODY>'
                body = s[s.find(bodytag)+len(bodytag):]
                body = body[:body.find('</')]
                wire_bodies.append(body)

    # only keep most common topics
    items = list(topic_counts.items())
    items.sort(key = lambda x: x[1])
    kept_topics = set()
    for x in items:
        print(x[0] + ': ' + str(x[1]))
        if x[1] >= min_samples_per_topic:
            kept_topics.add(x[0])
    print('-')
    print('Kept topics:', len(kept_topics))

    # filter wires with rare topics
    kept_wires = []
    labels = []
    topic_indexes = {}
    for t, b in zip(wire_topics, wire_bodies):
        if t in kept_topics:
            if t not in topic_indexes:
                topic_index = len(topic_indexes)
                topic_indexes[t] = topic_index
            else:
                topic_index = topic_indexes[t]

            labels.append(topic_index)
            kept_wires.append(b)

    # vectorize wires
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(kept_wires)
    X = tokenizer.texts_to_sequences(kept_wires)

    print('Sanity check:')
    for w in ["banana", "oil", "chocolate", "the", "dsft"]:
        print('...index of', w, ':', tokenizer.word_index.get(w))

    dataset = (X, labels) 
    print('-')
    print('Saving...')
    moves.cPickle.dump(dataset, open(os.path.join('datasets', 'data', 'reuters.pkl'), 'w'))
    moves.cPickle.dump(tokenizer.word_index, open(os.path.join('datasets','data', 'reuters_word_index.pkl'), 'w'))



def load_data(path="reuters.pkl", nb_words=None, skip_top=0, maxlen=None, test_split=0.2, seed=113,
    start_char=1, oov_char=2, index_from=3):

    path = get_file(path, origin="https://s3.amazonaws.com/text-datasets/reuters.pkl")
    f = open(path, 'rb')

    X, labels = moves.cPickle.load(f)
    f.close()

    np.random.seed(seed)
    np.random.shuffle(X)
    np.random.seed(seed)
    np.random.shuffle(labels)

    if start_char is not None:
        X = [[start_char] + [w + index_from for w in x] for x in X]
    elif index_from:
        X = [[w + index_from for w in x] for x in X]

    if maxlen:
        new_X = []
        new_labels = []
        for x, y in zip(X, labels):
            if len(x) < maxlen:
                new_X.append(x)
                new_labels.append(y)
        X = new_X
        labels = new_labels

    if not nb_words:
        nb_words = max([max(x) for x in X])

    # by convention, use 2 as OOV word
    # reserve 'index_from' (=3 by default) characters: 0 (padding), 1 (start), 2 (OOV)
    if oov_char is not None:
        X = [[oov_char if (w >= nb_words or w < skip_top) else w for w in x] for x in X]
    else:
        nX = []
        for x in X:
            nx = []
            for w in x:
                if (w >= nb_words or w < skip_top):
                    nx.append(w)
            nX.append(nx)
        X = nX

    X_train = X[:int(len(X)*(1-test_split))]
    y_train = labels[:int(len(X)*(1-test_split))]

    X_test = X[int(len(X)*(1-test_split)):]
    y_test = labels[int(len(X)*(1-test_split)):]

    return (X_train, y_train), (X_test, y_test)


def get_word_index(path="reuters_word_index.pkl"):
    path = get_file(path, origin="https://s3.amazonaws.com/text-datasets/reuters_word_index.pkl")
    f = open(path, 'rb')
    return moves.cPickle.load(f)


if __name__ == "__main__":
    make_reuters_dataset()
    (X_train, y_train), (X_test, y_test) = load_data()
