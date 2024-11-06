def replace(l:list, to_replace, replace_by) -> None:
    for i in range(len(l)):
        if l[i] == to_replace:
            l[i] = replace_by