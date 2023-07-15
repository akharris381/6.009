"""
6.1010 Spring '23 Lab 3: Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """
    Takes in raw film data, outputs:
        1. a dictionary where each key is an actor id,
        and each value is the set of actor ids they have acted with
        2. a dictionary where each key is an actor id,
        and each value is the set of film ids they have filmed in
        3. a dictionary where each key is a film id,
        and each value is the set of actor ids in that film
    """
    acted_together_dict = {}
    filmed_in_dict = {}
    actors_in_film_dict = {}
    for record in raw_data:
        if record[0] in acted_together_dict:
            acted_together_dict[record[0]].add(record[1])
            filmed_in_dict[record[0]].add(record[2])
        else:
            acted_together_dict[record[0]] = {record[1]}
            filmed_in_dict[record[0]] = {record[2]}
        if record[1] in acted_together_dict:
            acted_together_dict[record[1]].add(record[0])
            filmed_in_dict[record[1]].add(record[2])
        else:
            acted_together_dict[record[1]] = {record[0]}
            filmed_in_dict[record[1]] = {record[2]}
        if record[2] in actors_in_film_dict:
            actors_in_film_dict[record[2]].update([record[0], record[1]])
        else:
            actors_in_film_dict[record[2]] = {record[0], record[1]}
    return (acted_together_dict, filmed_in_dict, actors_in_film_dict)


def acted_together(transformed_data, actor_id_1, actor_id_2):
    if actor_id_2 in transformed_data[0][actor_id_1] or actor_id_1 == actor_id_2:
        return True
    else:
        return False


def actors_with_bacon_number(transformed_data, n):
    """
    Returns set of actor ids with bacon number n
    """
    agenda = {4724}
    visited = {4724}
    for i in range(n):
        print(agenda)
        neighbors = set({})
        for actor_id in agenda:
            for actor in transformed_data[0][actor_id]:
                if actor not in visited:
                    neighbors.add(actor)
                    visited.add(actor)
        agenda = neighbors
        if not agenda:
            break
    return neighbors


def bacon_path(transformed_data, actor_id):
    return actor_to_actor_path(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    return actor_path(transformed_data, actor_id_1, lambda id: id == actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Returns shortest path from actor_id_1 to actor id satisfying the goal test function
    """
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    agenda = [[actor_id_1]]
    visited = {actor_id_1}
    while agenda:
        current_path = agenda.pop(0)
        end_of_path = current_path[-1]
        for actor in transformed_data[0][end_of_path]:
            if actor not in visited:
                new_path = current_path + [actor]
                if goal_test_function(actor):
                    return new_path
                agenda.append(new_path)
                visited.add(actor)
    return None


def find_shared_film(transformed_data, actor_id_1, actor_id_2):
    for film_id in transformed_data[1][actor_id_1]:
        if film_id in transformed_data[1][actor_id_2]:
            return film_id


def movie_path(transformed_data, actor_id_1, actor_id_2):
    actors_path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    return [
        find_shared_film(transformed_data, actors_path[i], actors_path[i + 1])
        for i in range(len(actors_path) - 1)
    ]


def actors_connecting_films(transformed_data, film1, film2):
    """
    Returns list of the shortest path of actor ids from film1 to film2
    """
    min_length = float("inf")
    shortest_path = None
    actors_in_film1 = transformed_data[2][film1]
    actors_in_film2 = transformed_data[2][film2]
    for actor_id in actors_in_film1:
        path = actor_path(transformed_data, actor_id, lambda id: id in actors_in_film2)
        if path is not None:
            if len(path) < min_length:
                shortest_path = path
                min_length = len(path)
    return shortest_path


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
    # print(smalldb)
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    with open("resources/names.pickle", "rb") as f:
        namesdb = pickle.load(f)
    # id1 = namesdb["Melanie Laurent"]
    # id2 = namesdb["Stephanie Sotomayer"]
    # print(namesdb)
    # print(namesdb["Robert LeQuang"])
    # for name in namesdb:
    #   if namesdb[name] == 12006:
    #      print(name)
    new_small = transform_data(smalldb)
    # print(new_small)
    # print(acted_together(new_small,id1,id2))
    # print(id1)
    # print(id2)
    # print(new_small[id1])
    # print(new_small[id2])
    # for record in smalldb:
    #   if id1 in record or id2 in record:
    #      print(record)
    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)
    new_large = transform_data(largedb)
    id1 = namesdb["Rex Everhart"]
    id2 = namesdb["Iva Ilakovac"]
    # path = actor_to_actor_path(new_large,id1,id2)
    # names = []
    # for id in path:
    #   for name in namesdb:
    #      if namesdb[name] == id:
    #         names.append(name)
    # print(names)
    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)
    film_path = movie_path(new_large, id1, id2)
    print(film_path)
    with open("resources/movies.pickle", "rb") as f:
        moviesdb = pickle.load(f)
    movies = []
