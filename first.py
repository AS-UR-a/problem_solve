
def print_table(X, cost, supply, demand, title="Таблица", real_rows=None, real_cols=None):
    if real_rows is None:
        real_rows = len(supply)
    if real_cols is None:
        real_cols = len(demand)

    print(f"\n{title}")
    print("┌─────" + "┬───────" * real_cols + "┬───────┐")
    print("│     ", end="")
    for j in range(real_cols):
        print(f"│  b{j+1:2}  ", end="")
    print("│ Запасы│")
    print("├─────" + "┼───────" * real_cols + "┼───────┤")

    for i in range(real_rows):
        print(f"│ a{i+1:2} ", end="")
        for j in range(real_cols):
            if X[i][j] > 0:
                print(f"│{X[i][j]:3}({cost[i][j]:2}) ", end="")
            else:
                print(f"│  ·({cost[i][j]:2}) ", end="")
        print(f"│ {supply[i]:5} │")
        if i < real_rows - 1:
            print("├─────" + "┼───────" * real_cols + "┼───────┤")

    print("├─────" + "┼───────" * real_cols + "┼───────┤")
    print("│ Спрос", end="")
    for j in range(real_cols):
        print(f"│ {demand[j]:5} ", end="")
    print("│       │")
    print("└─────" + "┴───────" * real_cols + "┴───────┘")


def total_real_cost(X, cost, real_rows, real_cols):
    total = 0
    for i in range(real_rows):
        for j in range(real_cols):
            total += X[i][j] * cost[i][j]
    return total


def balance(supply, demand, cost):
    total_supply = sum(supply)
    total_demand = sum(demand)
    print(f"\nПроверка баланса: запасы={total_supply}, спрос={total_demand}")
    if total_supply == total_demand:
        print("Задача закрытая")
        return supply, demand, cost
    elif total_supply < total_demand:
        fake = total_demand - total_supply
        supply.append(fake)
        cost.append([0] * len(demand))
        print(f"Добавлен фиктивный поставщик с запасом {fake} (стоимость 0)")
        return supply, demand, cost
    else:
        fake = total_supply - total_demand
        demand.append(fake)
        for row in cost:
            row.append(0)
        print(f"Добавлен фиктивный потребитель со спросом {fake} (стоимость 0)")
        return supply, demand, cost

def north_west(supply, demand, cost):
    m, n = len(supply), len(demand)
    s, d = supply[:], demand[:]
    X = [[0]*n for _ in range(m)]
    basis = []
    i, j = 0, 0
    while i < m and j < n:
        amount = min(s[i], d[j])
        X[i][j] = amount
        if amount > 0:
            basis.append((i, j))
        s[i] -= amount
        d[j] -= amount
        if s[i] == 0:
            i += 1
        if d[j] == 0:
            j += 1
    basis = ensure_connected_basis(X, basis, m, n, cost)
    return X, basis


def min_cost_method(supply, demand, cost):
    m, n = len(supply), len(demand)
    s, d = supply[:], demand[:]
    X = [[0]*n for _ in range(m)]
    basis = []
    cells = [(cost[i][j], i, j) for i in range(m) for j in range(n)]
    cells.sort()
    for c, i, j in cells:
        if s[i] > 0 and d[j] > 0:
            amount = min(s[i], d[j])
            X[i][j] = amount
            basis.append((i, j))
            s[i] -= amount
            d[j] -= amount
    basis = ensure_connected_basis(X, basis, m, n, cost)
    return X, basis

def ensure_connected_basis(X, basis, m, n, cost):
    required = m + n - 1
    if len(basis) >= required:
        return basis

    basis_set = set(basis)
    free_cells = [(cost[i][j], i, j) for i in range(m) for j in range(n) if (i, j) not in basis_set]
    free_cells.sort()

    def find_components(basis_list):
        parent = list(range(m + n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx
        for i, j in basis_list:
            union(i, m + j)
        return find

    while len(basis) < required:
        find = find_components(basis)
        added = False
        for _, i, j in free_cells:
            if find(i) != find(m + j):
                X[i][j] = 0
                basis.append((i, j))
                basis_set.add((i, j))
                added = True
                break
        if not added:
            for _, i, j in free_cells:
                if (i, j) not in basis_set:
                    X[i][j] = 0
                    basis.append((i, j))
                    basis_set.add((i, j))
                    break
    return basis


def calculate_potentials(X, cost, basis, m, n):
    u = [None] * m
    v = [None] * n
    u[0] = 0
    changed = True
    while changed:
        changed = False
        for i, j in basis:
            if u[i] is not None and v[j] is None:
                v[j] = cost[i][j] - u[i]
                changed = True
            elif u[i] is None and v[j] is not None:
                u[i] = cost[i][j] - v[j]
                changed = True
    return u, v


def evaluate_plan(X, basis, cost, supply, demand, real_rows, real_cols):
    m, n = len(supply), len(demand)
    u, v = calculate_potentials(X, cost, basis, m, n)

    print("\nПотенциалы:")
    print("u =", [f"{ui:.2f}" if ui is not None else "None" for ui in u])
    print("v =", [f"{vj:.2f}" if vj is not None else "None" for vj in v])

    print("\nОценки свободных клеток:")
    has_negative = False
    min_delta = 0
    for i in range(m):
        for j in range(n):
            if (i, j) in basis:
                continue
            if u[i] is not None and v[j] is not None:
                delta = cost[i][j] - u[i] - v[j]
                if i < real_rows and j < real_cols:
                    if delta < -1e-10:
                        print(f"Δ({i+1},{j+1}) = {delta:6.2f} *")
                        has_negative = True
                        if delta < min_delta:
                            min_delta = delta
                    else:
                        print(f"Δ({i+1},{j+1}) = {delta:6.2f}")
    if not has_negative:
        print("\nВсе оценки неотрицательны → план оптимален!")
    else:
        print(f"\nЕсть отрицательные оценки (минимальная {min_delta:.2f}) → план не оптимален.")
    return not has_negative, min_delta


def main():
    supply_real = [190, 110, 105, 255, 245]
    demand_real = [50, 150, 240, 145, 95]
    cost_real = [
        [7, 6, 4, 3, 9],
        [3, 8, 5, 4, 7],
        [2, 3, 7, 2, 3],
        [4, 5, 2, 3, 5],
        [5, 7, 3, 9, 2]
    ]

    print("="*70)
    print("ТРАНСПОРТНАЯ ЗАДАЧА (вариант 23, вторая таблица)")
    print("="*70)

    supply, demand, cost = balance(
        supply_real[:], demand_real[:],
        [row[:] for row in cost_real]
    )

    real_rows, real_cols = len(supply_real), len(demand_real)

    X_nw, basis_nw = north_west(supply[:], demand[:], cost)
    cost_nw = total_real_cost(X_nw, cost, real_rows, real_cols)

    X_min, basis_min = min_cost_method(supply[:], demand[:], cost)
    cost_min = total_real_cost(X_min, cost, real_rows, real_cols)

    print_table(X_nw, cost, supply, demand, "ОПОРНЫЙ ПЛАН: СЕВЕРО-ЗАПАДНЫЙ УГОЛ", real_rows, real_cols)
    print(f"Стоимость (только реальные): {cost_nw}")

    print_table(X_min, cost, supply, demand, "ОПОРНЫЙ ПЛАН: МЕТОД МИНИМАЛЬНОЙ СТОИМОСТИ", real_rows, real_cols)
    print(f"Стоимость (только реальные): {cost_min}")

    print("\n" + "="*60)
    print("СРАВНЕНИЕ ОПОРНЫХ ПЛАНОВ")
    print("="*60)
    print(f"Северо-западный угол: {cost_nw}")
    print(f"Минимальная стоимость: {cost_min}")

    if cost_nw <= cost_min:
        best_X, best_basis, best_name, best_cost = X_nw, basis_nw, "северо-западный угол", cost_nw
    else:
        best_X, best_basis, best_name, best_cost = X_min, basis_min, "метод минимальной стоимости", cost_min

    print(f"\nЛучший опорный план: {best_name} (стоимость {best_cost})")

    print("\n" + "="*60)
    print("МЕТОД ПОТЕНЦИАЛОВ (проверка оптимальности)")
    print("="*60)
    is_optimal, min_delta = evaluate_plan(best_X, best_basis, cost, supply, demand, real_rows, real_cols)

    if is_optimal:
        print(f"\nПлан оптимален. Итоговая стоимость: {best_cost}")
    else:
        print(f"\nПлан не оптимален. Наименьшая отрицательная оценка = {min_delta:.2f}")
        print("Для получения оптимального плана нужно перераспределение по циклу.")


if __name__ == "__main__":
    main()
