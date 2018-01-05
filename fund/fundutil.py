from collections import OrderedDict


def sort(map):
    if not bool(map):
        print('Dict is empty...')

    sorted_dict = OrderedDict(sorted(map.items()))

    return sorted_dict
