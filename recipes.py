"""
6.1010 Spring '23 Lab 4: Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    recipe_book = {}
    compound_foods = set()
    for food in recipes:
        if food[0] == "compound":
            if food[1] not in compound_foods:
                recipe_book[food[1]] = [food[2]]
                compound_foods.add(food[1])
            else:
                recipe_book[food[1]].append(food[2])

    return recipe_book


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomic_costs = {}
    atomic_foods = set()
    for food in recipes:
        if food[0] == "atomic" and food[1] not in atomic_foods:
            atomic_costs[food[1]] = food[2]
            atomic_foods.add(food[1])

    return atomic_costs


def lowest_cost(recipes, food_item, foods_to_ignore=None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    if foods_to_ignore is None:
        foods_to_ignore = ()

    recipe_book = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)
    if (
        food_item not in recipe_book and food_item not in atomic_costs
    ) or food_item in foods_to_ignore:
        return None
    if food_item in atomic_costs:
        return atomic_costs[food_item]
    else:
        # make a list of the costs of each recipe to generate a food item
        costs = []
        for recipe in recipe_book[food_item]:
            cost = 0
            for pair in recipe:
                item_cost = lowest_cost(recipes, pair[0], foods_to_ignore)
                if item_cost is None:
                    cost = None
                    break
                    # break if any item in the recipe has a lowest cost of None
                else:
                    cost += item_cost * pair[1]
            if cost is not None:
                costs.append(cost)
        if costs:
            return min(costs)
        else:
            return None


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    return {food: n * flat_recipe[food] for food in flat_recipe}


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    foods = set()
    grocery_list = {}
    for recipe in flat_recipes:
        for food in recipe:
            if food not in foods:
                foods.add(food)
                grocery_list[food] = recipe[food]
            else:
                grocery_list[food] += recipe[food]
    return grocery_list


def cheapest_flat_recipe(recipes, food_item, foods_to_ignore=None):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    flat_recipes = all_flat_recipes(recipes, food_item, foods_to_ignore)
    if flat_recipes == []:
        return None
    else:
        costs = []
        atomic_costs = make_atomic_costs(recipes)
        for flat_recipe in flat_recipes:
            cost = 0
            for pair in flat_recipe.items():
                cost += pair[1] * atomic_costs[pair[0]]
            costs.append(cost)
        return flat_recipes[costs.index(min(costs))]


def combine_dict(dict1, dict2):
    """
    Combines two recipe dictionaries.
    """
    # print(f"dict1: {dict1}")
    # print(f"dict2: {dict2}")
    combined = {}
    keys = set({})
    for key1 in dict1:
        if key1 in dict2:
            combined[key1] = dict1[key1] + dict2[key1]
        else:
            combined[key1] = dict1[key1]
        keys.add(key1)
    for key2 in dict2:
        if key2 not in keys:
            combined[key2] = dict2[key2]
    return combined


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    # print(f"flat recipes: {flat_recipes}")
    if len(flat_recipes) == 1:
        return flat_recipes[0]
    elif len(flat_recipes) == 0:
        return flat_recipes
    else:
        mix = []
        sub_mix = ingredient_mixes(flat_recipes[1:])
        # print(f"sub_mix: {sub_mix}")
        first = flat_recipes[0]
        # print(f"first: {first}")
        for recipe1 in first:
            for recipe2 in sub_mix:
                mix.append(combine_dict(recipe1, recipe2))
        return mix


def all_flat_recipes(recipes, food_item, foods_to_ignore=None):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    if foods_to_ignore is None:
        foods_to_ignore = ()

    recipe_book = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)
    if (
        food_item not in recipe_book and food_item not in atomic_costs
    ) or food_item in foods_to_ignore:
        return []
    if food_item in atomic_costs:
        return [{food_item: 1}]
    else:
        flat_recipes_for_food_item = []
        for recipe in recipe_book[food_item]:
            flat_recipes_for_recipe = [{}]
            for pair in recipe:
                flat_recipes_for_ingredient = all_flat_recipes(
                    recipes, pair[0], foods_to_ignore
                )
                # print(f"recipes: {recipes}")
                # print(f"pair[0]: {pair[0]}")
                if flat_recipes_for_ingredient == []:
                    flat_recipes_for_recipe = []
                    break
                    # break if any item in the recipe does not have a possible recipe
                else:
                    # print(f"flat_recipes_for_recipe: {flat_recipes_for_recipe}")
                    # print(f"flat_recipes_for_ingredient 
                    # {flat_recipes_for_ingredient}")
                    for flat_recipe in flat_recipes_for_ingredient:
                        for ingredient in flat_recipe:
                            flat_recipe[ingredient] *= pair[1]
                    flat_recipes_for_recipe = ingredient_mixes(
                        [flat_recipes_for_recipe, flat_recipes_for_ingredient]
                    )
            flat_recipes_for_food_item = (
                flat_recipes_for_food_item + flat_recipes_for_recipe
            )
        return flat_recipes_for_food_item


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    recipe_book_dict = make_recipe_book(example_recipes)
    # print(recipe_book_dict)
    # atomic_costs_dict = make_atomic_costs(example_recipes)
    # print(atomic_costs_dict)
    # print(recipe_book_dict["cheese"])
    # print(sum(atomic_costs_dict.values()))
    # print(sum(len(recipe_book_dict[x]) > 1 for x in recipe_book_dict))
    # cookie_recipes = [
    #     ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
    #     ("compound", "cookie", [("chocolate chips", 3)]),
    #     ("compound", "cookie", [("sugar", 10)]),
    #     ("atomic", "chocolate chips", 200),
    #     ("atomic", "sugar", 5),
    #     ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
    #     ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
    #     ("atomic", "vanilla ice cream", 20),
    #     ("atomic", "chocolate ice cream", 30),
    # ]
    # low_cookie = lowest_cost(cookie_recipes, "cookie sandwich")
    # print(low_cookie)
    # dairy_recipes_2 = [
    #     ("compound", "milk", [("cow", 2), ("milking stool", 1)]),
    #     ("compound", "cheese", [("milk", 1), ("time", 1)]),
    #     ("compound", "cheese", [("cutting-edge laboratory", 11)]),
    #     ("atomic", "milking stool", 5),
    #     ("atomic", "cutting-edge laboratory", 1000),
    #     ("atomic", "time", 10000),
    # ]
    # print(lowest_cost(dairy_recipes_2, "cheese", ["cutting-edge laboratory"]))
    # print(lowest_cost(dairy_recipes_2, "cheese"))
    # soup = {"carrots": 5, "celery": 3, "broth": 2, 
    # "noodles": 1, "chicken": 3, "salt": 10}
    # carrot_cake = {"carrots": 5, "flour": 8, 
    # "sugar": 10, "oil": 5, "eggs": 4, "salt": 3}
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # print(make_grocery_list([soup,carrot_cake,bread]))
    # cake_recipes = [{"cake": 1}, {"gluten free cake": 1}]
    # icing_recipes = [{"vanilla icing": 1}, {"cream cheese icing": 1}]
    # topping_recipes = [{"sprinkles": 20}]
    # ingredient_mix = ingredient_mixes([cake_recipes, 
    # icing_recipes, topping_recipes, [{}]])
    # print(ingredient_mix)
    cookie_recipes = [
        ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
        ("compound", "cookie", [("chocolate chips", 3)]),
        ("compound", "cookie", [("sugar", 10)]),
        ("atomic", "chocolate chips", 200),
        ("atomic", "sugar", 5),
        ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
        ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
        ("atomic", "vanilla ice cream", 20),
        ("atomic", "chocolate ice cream", 30),
    ]
    cookie_sandwich = all_flat_recipes(cookie_recipes, "cookie sandwich", ("cookie"))
    print(cookie_sandwich)
