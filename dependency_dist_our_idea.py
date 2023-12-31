# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import spacy

from spacy.tokens import Doc

class WhitespaceTokenizer(object):
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = text.split()
        # All tokens 'own' a subsequent space character in this tokenizer
        spaces = [True] * len(words)
        return Doc(self.vocab, words=words, spaces=spaces)

nlp = spacy.load('en_core_web_sm')
nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)

def dependency_dist_func(text, aspect_term):

    # https://spacy.io/docs/usage/processing-text
    document = nlp(text)
    # Load spacy's dependency tree into a networkx graph
    edges = []
    
    list2 = []
    words = []
    for token in document:
        # FYI https://spacy.io/docs/api/token
        # print("token:", token.dep_)
        list2.append(token.dep_)
        words.append(token.text)
        for child in token.children:
            # Comprehensive print please
            # print("token: ", token.i, token.text, token.dep_, token.head.i, token.head.text, [child for child in token.children])
            edges.append((token.i, child.i))
    # print("edges: ", edges)
    graph = nx.Graph(edges)

    text_lst = text.split()
    seq_len = len(text_lst)
    text_left, _, _ = text.partition(aspect_term)
    start = len(text_left.split())
    end = start + len(aspect_term.split())
    asp_idx = [i for i in range(start, end)]
    dist_matrix = seq_len*np.ones((seq_len, len(asp_idx))).astype('float32')
    for i, asp in enumerate(asp_idx):
        for j in range(seq_len):
            try:
                dist_matrix[j][i] = nx.shortest_path_length(graph, source=asp, target=j)
            except:
                dist_matrix[j][i] = seq_len/2
    dist_matrix = np.min(dist_matrix, axis=1)
    
    for i in range(len(dist_matrix)):
        # print("list2[i]:", list2[i])
        if list2[i] == "neg" or list2[i] == "advmod" or list2[i] == "amod" or list2[i] == "attr" \
            or list2[i] == "ccomp" or list2[i] == "acomp":
            dist_matrix[i] = 1
        # if list2[i] == "advmod" or list2[i] == "amod" or list2[i] == "attr" \
        #     or list2[i] == "ccomp" or list2[i] == "acomp":
        #     dist_matrix[i] = 1
    
    aspect_term_split = aspect_term.split()
    for i in range(len(words) - len(aspect_term_split) + 1):
        if words[i:i+len(aspect_term_split)] == aspect_term_split:
            dist_matrix[i:i+len(aspect_term_split)] = 0
            
    return dist_matrix