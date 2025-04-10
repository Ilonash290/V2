import random
import math
import time as tm

# Ввод данных
m = int(input("Введите количество заказов: "))
speed = int(input("Введите скорость всех курьеров (км/ч): "))
work_time = int(input("Введите время работы всех курьеров (часы): "))
print("Введите матрицу расстояний (m+1 строк по m+1 чисел, где строка 0 — склад):")
dist_matrix = []
for i in range(m + 1):
    row = list(map(float, input(f"Введите строку {i+1}: ").split()))
    dist_matrix.append(row)

# Начало замера времени
start_time = tm.time()

warehouse_index = 0
orders_indices = list(range(1, m + 1))
max_orders_per_courier = m  # Максимальное количество заказов на курьера ( = кол-ву заказов )
print("Введите начальное количество курьеров: АВТОМАТИЧЕСКИ ПРИСВОЕНО ЧИСЛО, РАВНОЕ КОЛИЧЕСТВУ ЗАКАЗОВ")
n = m

# Жадный алгоритм для построения маршрута
def greedy_route(courier_order_indices, warehouse_index, dist_matrix):
    if not courier_order_indices:
        return [], 0
    route = []
    current = warehouse_index  # Начинаем со склада
    total_distance = 0
    unvisited = list(courier_order_indices)
    while unvisited:
        next_order = min(unvisited, key=lambda idx: dist_matrix[current][idx])
        route.append(next_order)
        total_distance += dist_matrix[current][next_order]
        current = next_order
        unvisited.remove(next_order)
    total_distance += dist_matrix[current][warehouse_index]  # Возвращение на склад
    return route, total_distance

# Время доставки для курьера
def calculate_time(courier_order_indices, warehouse_index, dist_matrix, speed):
    route, total_distance = greedy_route(courier_order_indices, warehouse_index, dist_matrix)
    delivery_time = total_distance / speed
    return delivery_time, route

# Функция приспособленности
def fitness(chromosome, n, orders_indices, warehouse_index, dist_matrix, speed, work_time, max_orders_per_courier):
    courier_assignments = [[] for _ in range(n)]
    for order_idx, courier in enumerate(chromosome):
        courier_assignments[courier].append(orders_indices[order_idx])
    
    total_time_excess = 0
    used_courier_count = sum(1 for ca in courier_assignments if ca)  # Количество занятых курьеров
    total_time = 0
    penalty = 0
    
    for ca in courier_assignments:
        if len(ca) > max_orders_per_courier:
            penalty += 1000  # Штраф за превышение количества заказов
        if ca:
            delivery_time, _ = calculate_time(ca, warehouse_index, dist_matrix, speed)
            total_time += delivery_time  # Учитываем общее время
            if delivery_time > work_time:
                total_time_excess += (delivery_time - work_time)  # Штраф за превышение времени
    
    if total_time_excess > 0 or penalty > 0:
        return 10000 + 100 * total_time_excess + penalty + used_courier_count
    
    # Минимизируем количество курьеров и общее время
    return used_courier_count + 0.1 * total_time

# Генетический алгоритм с элитизмом
def genetic_algorithm(n, orders_indices, warehouse_index, dist_matrix, speed, work_time, max_orders_per_courier):
    pop_size = 200  # Размер популяции
    generations = 5000  # Количество поколений
    mutation_rate = 0.02  # Вероятность мутации
    elite_size = int(pop_size * 0.1)  # Сохранение 10% лучших решений
    
    population = [[random.randint(0, n-1) for _ in range(len(orders_indices))] for _ in range(pop_size)]
    for generation in range(generations):
        fitness_scores = [fitness(chrom, n, orders_indices, warehouse_index, dist_matrix, speed, work_time, max_orders_per_courier) for chrom in population]
        best_score = min(fitness_scores)
        
        if best_score < 1000:  # Решение найдено
            best_chrom = population[fitness_scores.index(best_score)]
            ca = [[] for _ in range(n)]
            for idx, c in enumerate(best_chrom):
                ca[c].append(orders_indices[idx])
            used = sum(1 for x in ca if x)
            print(f"НАЙДЕНО РЕШЕНИЕ: Поколение {generation}, курьеров: {used}, лучшее приспособление: {best_score}")
            return True, best_chrom
        
        # Элитизм: сохраняем лучшие решения
        sorted_population = sorted(zip(population, fitness_scores), key=lambda x: x[1])
        new_population = [x[0] for x in sorted_population[:elite_size]]
        
        # Турнирная селекция для остальной популяции
        while len(new_population) < pop_size:
            tournament = random.sample(list(zip(population, fitness_scores)), 3)
            winner = min(tournament, key=lambda x: x[1])[0]
            new_population.append(winner[:])
        
        # Кроссовер
        for i in range(0, pop_size, 2):
            if i + 1 < pop_size and random.random() < 0.8:
                point1 = random.randint(1, len(orders_indices) - 2)
                point2 = random.randint(point1 + 1, len(orders_indices) - 1)
                parent1, parent2 = new_population[i], new_population[i + 1]
                new_population[i] = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
                new_population[i + 1] = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
        
        # Мутация
        for chrom in new_population:
            for j in range(len(chrom)):
                if random.random() < mutation_rate:
                    chrom[j] = random.randint(0, n-1)
        
        population = new_population
        
        # Вывод прогресса
        if generation % 50 == 0 or generation < 100:
            best_chrom = population[fitness_scores.index(best_score)]
            ca = [[] for _ in range(n)]
            for idx, c in enumerate(best_chrom):
                ca[c].append(orders_indices[idx])
            used = sum(1 for x in ca if x)
            print(f"Поколение {generation}, курьеров: {used}, лучшее приспособление: {best_score}")
    
    return False, None

low = 1
high = m  # Максимальное количество курьеров равно количеству заказов
min_couriers = None
best_chrom = None

while low <= high:
    mid = (low + high) // 2
    print(f"\nПроверка с {mid} курьерами")
    success, chrom = genetic_algorithm(mid, orders_indices, warehouse_index, dist_matrix, speed, work_time, max_orders_per_courier)
    if success:
        min_couriers = mid
        best_chrom = chrom
        high = mid - 1
    else:
        low = mid + 1

# Обработка результата
if min_couriers is not None:
    # Распределение заказов
    courier_assignments = [[] for _ in range(min_couriers)]
    for order_idx, courier in enumerate(best_chrom):
        courier_assignments[courier].append(orders_indices[order_idx])
    
    # Подсчитываем реальное количество занятых курьеров
    actual_used_couriers = sum(1 for ca in courier_assignments if ca)
    print(f"\nМинимальное количество курьеров: {actual_used_couriers}")
    
    # Оптимальные маршруты
    best_routes = []
    for ca in courier_assignments:
        if ca:
            _, route = calculate_time(ca, warehouse_index, dist_matrix, speed)
            best_routes.append(route)
        else:
            best_routes.append([])
    
    # Вывод маршрутов
    courier_number = 1
    for ca, route in zip(courier_assignments, best_routes):
        if ca:
            delivery_time, _ = calculate_time(ca, warehouse_index, dist_matrix, speed)
            route_str = ' -> '.join([f'Заказ {idx}' for idx in route])
            print(f"Курьер {courier_number}: склад -> {route_str} -> склад, время: {delivery_time:.2f} ч")
            courier_number += 1
    
    # Конец замера времени
    end_time = tm.time()
    execution_time = end_time - start_time
    print(f"Время выполнения программы: {execution_time:.2f} секунд")
else:
    end_time = tm.time()
    execution_time = end_time - start_time
    print(f"Время выполнения программы: {execution_time:.2f} секунд")
    print("Невозможно доставить все заказы с заданными параметрами.")