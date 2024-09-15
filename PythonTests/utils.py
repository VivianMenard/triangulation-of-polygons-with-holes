def replace(l:list, to_replace, replace_by) -> None:
    l = [replace_by if elem == to_replace else elem for elem in l]