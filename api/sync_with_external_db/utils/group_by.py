
def groupBy(arr, idx):
    d = {}
    for elem in arr:
        key = elem[idx]
        if key not in d:
            d[key] = []
        d[key].append(elem)
    return list(d.values())
