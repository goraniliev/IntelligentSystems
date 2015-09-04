# -*- coding: utf-8 -*-
# Because working with Macedonian Cyrillic characters

import math
import time

__author__ = 'goran'

def scalar(n1, n2):
    '''
    returns the scalar (dot) product of vectors n1 and n2
    :param n1:
    :param n2:
    :return:
    '''
    s = 0.0

    for w in n1:
        if w in n2:
            s += n1[w] * n2[w]

    return s


def module(n):
    '''
    returns the module of vector n
    :param n:
    :return:
    '''
    return math.sqrt(sum(n.values()))


def sim_fun(n1, n2):
    '''
    Similarity measure to check how similar 2 clusters are
    :param n1:
    :param n2:
    :return:
    '''
    return 1.0 * scalar(n1, n2) / (module(n1) * module(n2))


class BiCluster:
    '''
    Represents a cluster for HAC. Contains dictionary of key words for the cluster, left child and right child
    are the corresponding children clusters of the cluster,
    similarity keeps track of the similarity between the left and right children. id is used to identify the cluster
    and keep track which ones are single documents (the ones with positive id). size equals the number of documents
    in the cluster. Title is the title of the document for single document clusters and None otherwise.
    '''
    def __init__(self, words, left=None, right=None, similarity=1.0, id=None, size=1, title=None):
        self.words = words
        self.left = left
        self.right = right
        self.similarity = similarity
        self.id = id
        self.size = size
        self.title = title


def get_word_and_rating(p):
    '''
    Used to extract word and its rating from strings of form 'word(rating)'
    :param p:
    :return:
    '''
    p = p.strip()
    word = p[0:p.find('(')]
    rating = float(p[p.find('(') + 1:p.find(')')])
    return word, rating


def split_all_word_rating_pairs(line):
    '''
    Split words by space, and then get return
    :param line:
    :return:
    '''
    parts = line.split(' ')
    wordRatings = [get_word_and_rating(p) for p in parts]
    return dict(wordRatings)


def join_all_word_rating_pairs(words):
    '''
    For dictionary of key words with and corresponding importance in document as value, returns string of format
    word1(importance1) word2(importance2) ...
    :param words:
    :return:
    '''
    return ' '.join(str.format('%s(%f)' %(w[0], w[1])) for w in words.items())


def load_data(path='news.txt'):
    '''
    Loads initial clusters (every news document is cluster on its own at the start)
    :param path:
    :return:
    '''
    clusters = []

    with open(path, 'r') as r:
        count = 0
        for line in r:
            if count % 3 == 0:
                # Title reading
                title = line
            elif count % 3 == 1:
                words = split_all_word_rating_pairs(line)
            else:
                cluster = BiCluster(words, left=None, right=None, similarity=1, id=count/3, title=title)
                clusters.append(cluster)

            count += 1

    return clusters


def print_cluster(writer, cluster):
    '''
    Prints cluster recursively (first line contains words for this cluster, then for each document in the cluster
    prints firstly the title and after it the key words for that document
    :param cluster:
    :return:
    '''
    if cluster.id < 0:# this is not a document so it don't need to be printed

        if cluster.left != None:# recursively do the printing for the left child
            print_cluster(writer, cluster.left)

        if cluster.right != None: # recursively do the printing for the right child
            print_cluster(writer, cluster.right)

    else:

        writer.write('\t' + cluster.title)

        writer.write('\t' + join_all_word_rating_pairs(cluster.words))

        writer.write('\n\n')


def merge_key_words(x, y):
    '''
    Calculates result[k] = (len1 * x[k] + len2 * y[k]) / (len1 + len2) for all keywords k in x or y
    :param x:
    :param y:
    :return:
    '''
    len1 = len(x)
    len2 = len(y)

    allKeys = set(x.keys()).union(set(y.keys()))

    result = {}

    for key in allKeys:
        result[key] = 1.0 * (len1 * x.get(key, 0) + len2 * y.get(key, 0)) / (len1 + len2)

    return result


# print merge_key_words({'a': 1, 'b': 2}, {'b': 3, 'c': 3})


def hierarchical_clustering(data, sim_function=sim_fun, min_closeness=0.4):
    '''
    At the start every news document is a cluster on its own. While there is a pair of clusters which similarity is
    above min_closeness the 2 closest such clusters are merged in one new cluster.
    :param data:
    :param sim_function:
    :param min_closeness:
    :return:
    '''

    similarities = {}

    clusters = data

    before_similarities_calc = time.time()

    for i in xrange(len(clusters)):
        for j in xrange(i + 1, len(clusters)):
            similarities[(clusters[i].id, clusters[j].id)] = sim_function(clusters[i].words, clusters[j].words)

    after_similarities_calc = time.time()

    print 'Similarity calculations seconds = %d' %(after_similarities_calc - before_similarities_calc)


    current_id = -1
    while(len(clusters) > 1):
        no_merge = True

        closest = min_closeness

        clusters_to_merge = (0, 1)

        for i in xrange(len(clusters)):
            for j in xrange(i + 1, len(clusters)):

                if (clusters[i].id, clusters[j].id) not in similarities:
                    similarities[(clusters[i].id, clusters[j].id)] = sim_function(clusters[i].words, clusters[j].words)

                similarity = similarities[(clusters[i].id, clusters[j].id)]

                if similarity >= closest:
                    closest = similarity
                    no_merge = False
                    clusters_to_merge = (i, j)

        # if there aren't 2 clusters which can be merged, then clustering is finished
        if no_merge:
            break

        merged_words = merge_key_words(clusters[clusters_to_merge[0]].words, clusters[clusters_to_merge[1]].words)

        new_cluster = BiCluster(merged_words, clusters[clusters_to_merge[0]], clusters[clusters_to_merge[1]], closest,
                                id = current_id, size = clusters[clusters_to_merge[0]].size + clusters[clusters_to_merge[1]].size)

        del clusters[clusters_to_merge[1]]
        del clusters[clusters_to_merge[0]]
        current_id -= 1
        clusters.append(new_cluster)

    # Sort clusters by size

    clusters.sort(cmp=lambda x,y: cmp(x.size, y.size))
    clusters.reverse()

    return clusters


def print_all_clusters(path='out.txt'):
    '''
    Prints all clusters. For each cluster firstly the key words are written. After that each document contained
    in the cluster is printed indented, firstly the title and below its key words.
    :param path:
    :return:
    '''
    before_load = time.time()
    clusters = load_data()[0:700] # takes 38 seconds for 700 items. For more than 1000 news works slow.
    after_load = time.time()

    print 'Loading seconds = %d' %(after_load - before_load)

    clusters = hierarchical_clustering(clusters)
    after_clust = time.time()

    print 'Clustering seconds = %d' %(after_clust - after_load)

    with open(path, 'w') as wr:
        for c in clusters:
            wr.write('Size:\t%d\n' %c.size)
            wr.write(join_all_word_rating_pairs(c.words) + '\n')
            print_cluster(wr, c)


print_all_clusters()




