# -*- coding: utf-8 -*-
from math import sqrt

__author__ = 'goran'

# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


def sim_distance(prefs, person1, person2):
    shared_items = list(set(prefs[person1].keys()) & set(prefs[person2].keys()))
    if len(shared_items) == 0: return 0.0
    sqr_dist_sum = sum(
        [(prefs[person1][item] - prefs[person2][item]) ** 2 for item in shared_items])
    return 1.0 / (1.0 + sqr_dist_sum)


# print set(critics['Toby'].keys()) & set(critics['Jack Matthews'])
# print sim_distance(critics, 'Lisa Rose', 'Gene Seymour')


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r


# print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')


def top_matches(prefs, person, n=10, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    scores.sort(reverse=True)
    return scores[:n]


# print top_matches(critics, 'Toby', n=3)


def user_based_recommendation(prefs, person, similarity=sim_pearson):
    total_sim = {}
    total_score = {}

    for other in prefs:
        if other == person: continue

        sim = similarity(prefs, person, other)

        if sim <= 0: continue

        for item in prefs[other]:
            if item not in prefs[person]:
                # calculate total similarity with users who rated this item
                total_sim[item] = total_sim.get(item, 0) + sim
                # calculate total weighted score as sum of sim(user) * rating_by(user)
                total_score[item] = total_score.get(item, 0) + sim * prefs[other][item]

    return sorted([(1.0 * score / total_sim[item], item)
                   for item, score in total_score.items() if total_sim[item] != 0.0], reverse=True)


# print user_based_recommendation(critics, 'Toby')
# print user_based_recommendation(critics, 'Toby', sim_distance)


def user_based_recommendation_first_n(prefs, person, similarity=sim_pearson, n=10):
    most_sim_users = [tm[1] for tm in top_matches(prefs, person, n=n, similarity=similarity)]

    total_sim = {}
    total_score = {}

    for other in most_sim_users:
        sim = similarity(prefs, person, other)

        for item in prefs[other]:
            if item not in prefs[person]:
                # calculate total similarity with users who rated this item
                total_sim[item] = total_sim.get(item, 0) + sim
                # calculate total weighted score as sum of sim(user) * rating_by(user)
                total_score[item] = total_score.get(item, 0) + sim * prefs[other][item]

    return sorted([(1.0 * total_score[item] / total_sim[item], item) for item in total_sim.keys()], reverse=True)


# print user_based_recommendation_first_n(critics, 'Toby', sim_pearson, 3)

def transform_prefs(prefs):
    result = {}
    for person, items_ratings in prefs.iteritems():
        for item in items_ratings:
            result.setdefault(item, {})
            result[item][person] = items_ratings[item]

    return result


def calculate_similar_items(prefs, n=10, similarity=sim_distance):
    result = {}

    item_prefs = transform_prefs(prefs)

    for item in item_prefs:
        result[item] = top_matches(item_prefs, item, n=n, similarity=similarity)

    return result


# print transform_prefs(critics)
# movies = transform_prefs(critics)
# print user_based_recommendation(movies, 'Just My Luck')

# print calculate_similar_items(critics)

def item_based_recommendation(prefs, items_sim, person):
    '''
    You need to previously have built items_sim = calculate_similar_items(...)
    :param prefs:
    :param items_sim:
    :param person:
    :return:
    '''
    userRatings = prefs[person]
    totalScore = {}
    totalSim = {}

    # Loop over the items rated by this user
    for (item, rating) in userRatings.items():

        # Loop over items similar to this one
        for (similarity, item2) in items_sim[item]:

            # Ignore if this user has already rated item2
            if item2 in userRatings:
                continue

            # Weighted sum of rating * similarity
            totalScore.setdefault(item2, 0)
            totalScore[item2] += rating * similarity

            # similarity
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by the corresponding weighting sum to get an average
    rankings = [(1.0 * score / totalSim[item], item) for (item, score) in totalScore.items() if totalSim[item] > 0]

    rankings.sort(reverse=True)

    return rankings


# print item_based_recommendation(critics, 'Toby', sim_distance)


def loadMovieLens(path='/home/goran/Desktop/data'):
    # Get movie titles
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


def loadMovieLens2(path='/home/goran/Desktop/data'):
    # Get movie titles
    movies = {}
    for line in open(path + '/movies.dat'):
        (id, title) = line.split('::')[0:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path + '/ratings.dat'):
        (user, movieid, rating, ts) = line.split('::')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs

prefs = loadMovieLens()
items_sim = calculate_similar_items(prefs, n=50)
# print prefs['87']
# print items_sim
# print user_based_recommendation(prefs, '87')[0:30]
print item_based_recommendation(prefs, items_sim, '87')[0:30]

