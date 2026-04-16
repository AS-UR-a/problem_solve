def balance(supply, demand, cost):
    supply = supply[:]
    demand = demand[:]
    cost = [row[:] for row in cost]

    s, d = sum(supply), sum(demand)
    if s == d:
        print('Задача уже сбалансирована')
    elif s < d:
        fiction = d - s
        supply.append(fiction)
        cost.append([0] * len(demand))
        print(f'Добавлен фиктивный поставщик: {fiction}')
    else:
        fiction = s - d
        demand.append(fiction)
        for row in cost:
            row.append(9)
        print(f'Добавлен фиктивный потребитель: {fiction}')
    return supply, demand, cost


def north_west(supply, demand, cost):
    m, n = len(supply), len(demand)
    s = supply[:]
    d = demand[:]
    X = [[0] * n for _ in range(m)]
    basis = []

    i = j = 0
    while i < m and j < n:
        amount = min(s[i], d[j])
        X[i][j] = amount
        if amount > 0:
            basis.append((i, j))

        s[i] -= amount
        d[j] -= amount

        if s[i] == 0 and d[j] == 0:
            if i + 1 < m:
                basis.append((i + 1, j))
            i += 1
            j += 1
        elif s[i] == 0:
            i += 1
        elif d[j] == 0:
            j += 1
    return X, basis


def min_cost(supply, demand, cost):
    m, n = len(supply), len(demand)
    s = supply[:]
    d = demand[:]
    X = [[0] * n for _ in range(m)]
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
    return X, basis


def potentials(cost, basis, m, n):
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


def delta_table(cost, basis, u, v):
    m, n = len(cost), len(cost[0])
    deltas = [[None] * n for _ in range(m)]
    is_optimal = True
    min_delta = 0
    min_cell = None

    for i in range(m):
        for j in range(n):
            if (i, j) in basis:
                deltas[i][j] = 0
                continue
            if u[i] is None or v[j] is None:
                deltas[i][j] = None
                continue
            delta = cost[i][j] - u[i] - v[j]
            deltas[i][j] = delta
            if delta < 0:
                is_optimal = False
                if delta < min_delta:
                    min_delta = delta
                    min_cell = (i, j)
    return deltas, is_optimal, min_cell, min_delta


def total_cost(X, cost):
    return sum(X[i][j] * cost[i][j] for i in range(len(X)) for j in range(len(X[0])))


def print_table(X, cost, supply, demand, title='Таблица'):
    print('\n' + title)
    print('     ' + ' '.join(f'b{j+1:>5}' for j in range(len(demand))) + ' | Запасы')
    print('-' * (8 + 6 * len(demand) + 10))
    for i in range(len(supply)):
        row = []
        for j in range(len(demand)):
            if X[i][j] > 0:
                row.append(f'{X[i][j]:>3}({cost[i][j]:>2})')
            else:
                row.append(f'  ·({cost[i][j]:>2})')
        print(f'a{i+1:>2} ' + ' '.join(row) + f' | {supply[i]:>6}')
    print('-' * (8 + 6 * len(demand) + 10))
    print('Спрос ' + ' '.join(f'{d:>6}' for d in demand))


def print_deltas(deltas, title='Матрица дельт'):
    print('\n' + title)
    header = '       ' + ' '.join(f'b{j+1:>7}' for j in range(len(deltas[0])))
    print(header)
    for i, row in enumerate(deltas):
        line = []
        for x in row:
            if x is None:
                line.append('   None')
            else:
                line.append(f'{x:7.2f}')
        print(f'a{i+1:>2} ' + ' '.join(line))


def print_potentials(u, v):
    print('\nПотенциалы:')
    print('u =', [None if x is None else round(x, 2) for x in u])
    print('v =', [None if x is None else round(x, 2) for x in v])


def analyze_plan(X, basis, cost, label='План'):
    print('\n' + '=' * 70)
    print(label)
    print('Базис:', basis)
    print('Стоимость:', total_cost(X, cost))
    u, v = potentials(cost, basis, len(X), len(X[0]))
    print_potentials(u, v)
    deltas, is_optimal, min_cell, min_delta = delta_table(cost, basis, u, v)
    print_deltas(deltas)
    if is_optimal:
        print('Вывод: план оптимален')
    else:
        print(f'Вывод: план не оптимален, минимальная отрицательная оценка {min_delta:.2f} в клетке {min_cell}')
    return {
        'u': u,
        'v': v,
        'deltas': deltas,
        'is_optimal': is_optimal,
        'min_cell': min_cell,
        'min_delta': min_delta,
        'cost': total_cost(X, cost)
    }


def choose_best_plan(results):
    best_idx = min(range(len(results)), key=lambda i: results[i]['cost'])
    return best_idx, results[best_idx]


def main():
    o_supply = [190, 110, 105, 255, 245]
    o_demand = [50, 150, 240, 145, 95]
    o_cost = [
        [7, 6, 4, 3, 9],
        [3, 8, 5, 4, 7],
        [2, 3, 7, 2, 3],
        [4, 5, 2, 3, 5],
        [5, 7, 3, 9, 2]
    ]

    supply, demand, cost = balance(o_supply, o_demand, o_cost)

    X_nw, basis_nw = north_west(supply, demand, cost)
    print_table(X_nw, cost, supply, demand, 'План северо-западного угла')
    res_nw = analyze_plan(X_nw, basis_nw, cost, 'Анализ плана северо-западного угла')

    X_mc, basis_mc = min_cost(supply, demand, cost)
    print_table(X_mc, cost, supply, demand, 'План минимальной стоимости')
    res_mc = analyze_plan(X_mc, basis_mc, cost, 'Анализ плана минимальной стоимости')

    best_idx, best = choose_best_plan([res_nw, res_mc])
    print('\n' + '=' * 70)
    if best_idx == 0:
        print('Для дальнейшего анализа выбран план северо-западного угла')
        print('Так как его стоимость меньше или равна альтернативе')
    else:
        print('Для дальнейшего анализа выбран план минимальной стоимости')
        print('Так как его стоимость меньше альтернативы')
    print(f'Лучшая стоимость: {best["cost"]}')
    if best['is_optimal']:
        print('Выбранный план уже оптимален')
    else:
        print(f'Выбранный план не оптимален, отрицательная оценка {best["min_delta"]:.2f} в клетке {best["min_cell"]}')


if __name__ == '__main__':
    main()