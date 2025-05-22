import itertools

# group1, group2 = [1, 2, 3], [4, 5, 6]
# perm_group1 = list(itertools.permutations(group1))
# perm_group2 = list(itertools.permutations(group2))

# print([(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)])

# print(len([(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]))


# group1, group2 = [1, 2], [3, 4]
# perm_group1 = list(itertools.permutations(group1))
# perm_group2 = list(itertools.permutations(group2))
# print([(*p, *q) for p in perm_group1 for q in perm_group2])

forward_permutations = [tuple(itertools.islice(itertools.cycle([1, 2, 3, 4]), i, i + 4)) for i in range(4)]
reverse_permutations = [reversed(perm) for perm in forward_permutations]
print(forward_permutations, reverse_permutations)