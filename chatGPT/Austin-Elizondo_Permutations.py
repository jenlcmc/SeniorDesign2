def permutations(lst):
    if len(lst) <= 1:
        return [lst]
    result = []
    for i in range(len(lst)):
        rest = lst[:i] + lst[i+1:]
        perms = permutations(rest)
        for perm in perms:
            result.append([lst[i]] + perm)
    result.reverse()
    final_result = []
    for r in result:
        final_result.append(r)
    final_result.reverse()
    return final_result

if __name__ == "__main__":
    lst = [1, 2, 3]
    perms = permutations(lst)
    print(perms)
