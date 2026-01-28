"""
Утилиты для расчета стоимости доставки на основе зон
"""
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def point_in_polygon(lat, lon, polygon_coords):
    """
    Проверяет, находится ли точка (lat, lon) внутри полигона.
    
    Использует алгоритм Ray Casting (луч из точки в бесконечность).
    
    Args:
        lat: Широта точки
        lon: Долгота точки
        polygon_coords: Список координат полигона [[lat1, lon1], [lat2, lon2], ...]
                       Координаты хранятся в формате [lat, lon] (как в Yandex Maps)
    
    Returns:
        bool: True если точка внутри полигона, False иначе
    """
    if not polygon_coords or len(polygon_coords) < 3:
        return False
    
    # Нормализуем координаты: если это список списков, берем первый уровень
    # Формат может быть [[lat, lon], [lat, lon], ...] или [[[lat, lon], ...]]
    coords = polygon_coords
    if len(coords) > 0 and isinstance(coords[0], list) and len(coords[0]) > 0:
        if isinstance(coords[0][0], (int, float)):
            # Формат: [[lat, lon], [lat, lon], ...]
            coords = polygon_coords
        elif isinstance(coords[0][0], list):
            # Формат: [[[lat, lon], ...]] - берем первый элемент
            coords = coords[0]
    
    # Проверяем, что координаты в правильном формате
    if not all(isinstance(coord, (list, tuple)) and len(coord) >= 2 for coord in coords):
        return False
    
    # Конвертируем координаты полигона из [lat, lon] в [lon, lat] для алгоритма
    # Алгоритм Ray Casting работает с координатами в формате [lon, lat]
    polygon_lon_lat = [[coord[1], coord[0]] for coord in coords]
    
    # Точка в формате [lon, lat]
    point_lon = lon
    point_lat = lat
    
    n = len(polygon_lon_lat)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon_lon_lat[i]  # [lon, lat] для точки i
        xj, yj = polygon_lon_lat[j]  # [lon, lat] для точки j
        
        # Проверяем пересечение горизонтального луча (идущего вправо от точки)
        # с ребром полигона между точками i и j
        # Условие: луч пересекает ребро, если:
        # 1. Одна вершина выше луча, другая ниже (yi > point_lat) != (yj > point_lat)
        # 2. Точка пересечения находится справа от точки (point_lon < ...)
        # 3. Ребро не горизонтальное (yj != yi)
        
        # Пропускаем горизонтальные ребра
        if yj == yi:
            j = i
            continue
        
        # Проверяем пересечение
        if ((yi > point_lat) != (yj > point_lat)):
            # Вычисляем x-координату точки пересечения
            intersect_x = ((xj - xi) * (point_lat - yi)) / (yj - yi) + xi
            if point_lon < intersect_x:
                inside = not inside
        
        j = i
    
    return inside


def evaluate_formula(formula: str, order_sum: float, zone: Dict[str, Any]) -> float:
    """
    Вычисляет стоимость доставки по формуле.
    
    Поддерживаемые переменные:
    - {{order_sum}} - сумма заказа
    - {{min_sum}} - минимальная сумма из настроек зоны
    - {{price}} - базовая стоимость доставки из настроек зоны
    
    Args:
        formula: Строка с формулой (например: "({{order_sum}} < {{min_sum}}) ? {{price}} : 0")
        order_sum: Сумма заказа
        zone: Словарь с данными зоны
    
    Returns:
        float: Рассчитанная стоимость доставки
    
    Raises:
        ValueError: Если формула содержит недопустимые символы или не может быть вычислена
    """
    if not formula or not isinstance(formula, str):
        raise ValueError("Formula must be a non-empty string")
    
    # Безопасность: проверяем, что формула содержит только разрешенные символы
    # Разрешаем: числа, операторы, скобки, пробелы, плейсхолдеры
    allowed_pattern = re.compile(r'^[0-9+\-*/().\s<>=!?:&|{{}}]+$')
    if not allowed_pattern.match(formula.replace('{{order_sum}}', '').replace('{{min_sum}}', '').replace('{{price}}', '')):
        raise ValueError("Formula contains invalid characters")
    
    # Получаем значения переменных
    min_sum = zone.get('min_order_amount', 0)
    price = zone.get('delivery_cost', 0)
    
    # Заменяем плейсхолдеры на значения
    formula_eval = formula.replace('{{order_sum}}', str(order_sum))
    formula_eval = formula_eval.replace('{{min_sum}}', str(min_sum))
    formula_eval = formula_eval.replace('{{price}}', str(price))
    
    # Безопасное вычисление формулы
    # Используем eval только с ограниченным набором функций
    try:
        # Заменяем тернарный оператор на if-else для Python
        # Формат: (condition) ? value_if_true : value_if_false
        # Преобразуем в: value_if_true if condition else value_if_false
        
        # Простая замена тернарного оператора
        if '?' in formula_eval and ':' in formula_eval:
            # Находим тернарный оператор
            parts = formula_eval.split('?', 1)
            if len(parts) == 2:
                condition = parts[0].strip().strip('()')
                rest = parts[1].strip()
                if ':' in rest:
                    true_part, false_part = rest.split(':', 1)
                    true_part = true_part.strip()
                    false_part = false_part.strip()
                    # Преобразуем в Python if-else
                    formula_eval = f"({true_part} if ({condition}) else {false_part})"
        
        # Безопасное вычисление: только математические операции
        # Создаем безопасный контекст для eval
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
        }
        
        result = eval(formula_eval, safe_dict)
        
        # Проверяем, что результат - число
        if not isinstance(result, (int, float)):
            raise ValueError("Formula must return a number")
        
        # Округляем до 2 знаков после запятой и возвращаем
        return round(float(result), 2)
        
    except Exception as e:
        logger.error(f"Error evaluating formula '{formula}': {e}")
        raise ValueError(f"Invalid formula: {str(e)}")


def calculate_delivery_cost(lat, lon, delivery_zones, order_amount=0):
    """
    Рассчитывает стоимость доставки на основе координат и зон доставки.
    
    Args:
        lat: Широта точки доставки
        lon: Долгота точки доставки
        delivery_zones: Список зон доставки из delivery_zones_conditions
        order_amount: Сумма заказа (для проверки min_order_amount)
    
    Returns:
        dict: {
            'cost': float,  # Стоимость доставки (0 для бесплатной)
            'zone_name': str,  # Название зоны
            'is_free': bool,  # Бесплатная ли доставка
            'zone_found': bool  # Найдена ли подходящая зона
        }
    """
    if not delivery_zones or not isinstance(delivery_zones, list):
        return {
            'cost': None,
            'zone_name': None,
            'is_free': False,
            'zone_found': False,
            'message': 'Зоны доставки не настроены'
        }
    
    # Сортируем зоны по приоритету (1 - наивысший приоритет)
    sorted_zones = sorted(
        delivery_zones,
        key=lambda z: z.get('priority', 999)
    )
    
    # Проверяем каждую зону, начиная с наивысшим приоритетом
    for zone in sorted_zones:
        coordinates = zone.get('coordinates', [])
        if not coordinates or len(coordinates) < 3:
            logger.debug(f"Zone {zone.get('name', 'Unknown')} skipped: invalid coordinates")
            continue
        
        # Проверяем попадание точки в зону
        logger.debug(f"Checking point ({lat}, {lon}) in zone {zone.get('name', 'Unknown')} with {len(coordinates)} coordinates")
        is_inside = point_in_polygon(lat, lon, coordinates)
        logger.debug(f"Point ({lat}, {lon}) {'INSIDE' if is_inside else 'OUTSIDE'} zone {zone.get('name', 'Unknown')}")
        
        if is_inside:
            zone_name = zone.get('name', 'Неизвестная зона')
            
            # Проверяем, есть ли формула для расчета
            formula = zone.get('formula')
            
            if formula:
                # Используем формулу для расчета
                try:
                    cost = evaluate_formula(formula, order_amount, zone)
                    is_free = cost == 0
                    return {
                        'cost': cost,
                        'zone_name': zone_name,
                        'is_free': is_free,
                        'zone_found': True,
                        'formula_used': True
                    }
                except Exception as e:
                    logger.error(f"Error evaluating formula for zone {zone_name}: {e}")
                    # Fallback на старую логику при ошибке в формуле
                    pass
            
            # Старая логика (без формул) - для обратной совместимости
            delivery_type = zone.get('delivery_type', 'free')
            
            if delivery_type == 'free':
                # Проверяем минимальную сумму заказа для бесплатной доставки
                min_order_amount = zone.get('min_order_amount', 0)
                if order_amount >= min_order_amount:
                    return {
                        'cost': 0,
                        'zone_name': zone_name,
                        'is_free': True,
                        'zone_found': True,
                        'min_order_amount': min_order_amount
                    }
                else:
                    # Заказ меньше минимальной суммы - доставка платная
                    delivery_cost = zone.get('delivery_cost', 0)
                    return {
                        'cost': delivery_cost,
                        'zone_name': zone_name,
                        'is_free': False,
                        'zone_found': True,
                        'min_order_amount': min_order_amount,
                        'message': f'Для бесплатной доставки минимальная сумма заказа {min_order_amount} ₸'
                    }
            else:
                # Платная доставка
                delivery_cost = zone.get('delivery_cost', 0)
                return {
                    'cost': delivery_cost,
                    'zone_name': zone_name,
                    'is_free': False,
                    'zone_found': True
                }
    
    # Точка не попала ни в одну зону
    return {
        'cost': None,
        'zone_name': None,
        'is_free': False,
        'zone_found': False,
        'message': 'Адрес не попадает в зоны доставки'
    }
