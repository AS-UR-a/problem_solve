from copy import deepcopy

def print_matrix(mat, title=None):
    if title:
        print("\n" + title)
    for row in mat:
        print(" ".join(f"{x:>4}" for x in row))
    print()

def reduce_rows(a):
    a = deepcopy(a)
    row_mins = [min(row) for row in a]
    for i in range(len(a)):
        for j in range(len(a[0])):
            a[i][j] -= row_mins[i]
    return a, row_mins

def reduce_cols(a):
    a = deepcopy(a)
    col_mins = [min(a[i][j] for i in range(len(a))) for j in range(len(a[0]))]
    for i in range(len(a)):
        for j in range(len(a[0])):
            a[i][j] -= col_mins[j]
    return a, col_mins

def find_zero_matching(mat):
    n = len(mat)
    match_col = [-1] * n

    def dfs(i, seen):
        for j in range(n):
            if mat[i][j] == 0 and not seen[j]:
                seen[j] = True
                if match_col[j] == -1 or dfs(match_col[j], seen):
                    match_col[j] = i
                    return True
        return False

    for i in range(n):
        seen = [False] * n
        dfs(i, seen)

    match_row = [-1] * n
    for j in range(n):
        if match_col[j] != -1:
            match_row[match_col[j]] = j
    return match_row

def hungarian_min(cost):
    a = deepcopy(cost)
    n = len(a)

    print_matrix(a, "Исходная матрица")

    a, row_mins = reduce_rows(a)
    print("Минимумы строк:", row_mins)
    print_matrix(a, "После редукции по строкам")

    a, col_mins = reduce_cols(a)
    print("Минимумы столбцов:", col_mins)
    print_matrix(a, "После редукции по столбцам")

    assignment = find_zero_matching(a)

    if -1 in assignment:
        raise ValueError("Для этой версии кода не удалось найти полное назначение только по нулям.")

    total = sum(cost[i][assignment[i]] for i in range(n))

    print("Назначение:")
    for i, j in enumerate(assignment):
        print(f"  строка {i+1} -> столбец {j+1}, стоимость = {cost[i][j]}")
    print("Итоговая стоимость:", total)

    return assignment, total

def solve_task_1():
    cost = [
        [1, 3, 7, 8, 10, 3, 1],
        [8, 1, 1, 7, 1, 5, 4],
        [5, 1, 2, 1, 9, 1, 9],
        [9, 4, 1, 3, 1, 2, 8],
        [2, 5, 4, 3, 4, 9, 5],
        [1, 3, 7, 10, 0, 1, 6],
        [7, 2, 10, 1, 3, 5, 1]
    ]
    print("\n===== ЗАДАЧА 1 =====")
    return hungarian_min(cost)

def solve_task_2():
    cost = [
        [10, 6, 10, 7, 2],
        [9, 7, 10, 7, 6],
        [7, 6, 3, 9, 10],
        [10, 5, 9, 4, 7],
        [2, 2, 1, 20, 1]
    ]
    print("\n===== ЗАДАЧА 2 =====")
    return hungarian_min(cost)

if __name__ == "__main__":
    solve_task_1()
    solve_task_2()