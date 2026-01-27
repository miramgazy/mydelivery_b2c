"""
Утилиты для расчета стоимости доставки на основе зон
"""
import logging

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
            delivery_type = zone.get('delivery_type', 'free')
            zone_name = zone.get('name', 'Неизвестная зона')
            
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
