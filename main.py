import sys
import pygame
import time

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Настройки окна - вид сверху
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выживание в городе - Вид сверху")
clock = pygame.time.Clock()

# Цвета - приглушённые тёмные тона для фонов, яркие для активностей и людей
DARK_BG_1 = (45, 45, 48)      # Тёмно-серый для центра
DARK_BG_2 = (38, 35, 30)      # Тёмно-коричневый для жилого района
DARK_BG_3 = (30, 30, 35)      # Тёмно-синий для промышленной зоны
DARK_BG_4 = (25, 40, 30)      # Тёмно-зелёный для парка

GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLUE = (56, 7, 255)
RED = (255, 7, 0)
BLACK = (3, 0, 0)
YELLOW = (255, 215, 0)        # Золотой яркий
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
PURPLE = (180, 50, 200)       # Яркий фиолетовый
BEIGE = (245, 245, 220)
GREEN = (50, 200, 50)         # Яркий зелёный
CYAN = (0, 255, 255)          # Яркий циан
PINK = (255, 105, 180)        # Яркий розовый
LIME = (180, 255, 0)          # Яркий лайм
GOLD = (255, 215, 0)          # Золотой
ROAD_COLOR = (80, 80, 85)     # Цвет дороги
SIDEWALK_COLOR = (100, 100, 105)  # Цвет тротуара
GRASS_COLOR = (34, 139, 34)   # Цвет травы для парков
WATER_COLOR = (30, 144, 255)  # Цвет воды

# Кулдаун (30 секунд)
COOLDOWN_SECONDS = 30

# Шрифты
font = pygame.font.SysFont("Arial", 18)
log_font = pygame.font.SysFont("Arial", 16)

# Игровые параметры
player_hp = 100
player_hunger = 100
player_money = 50
current_location_index = 0

game_message = (
    "Добро пожаловать! Ходите по городу (WASD / стрелки). Подходите к объектам."
)


# Класс Игрока - вид сверху
class Player:

    def __init__(self):
        self.rect = pygame.Rect(400, 300, 24, 24)  # Квадратный игрок для вида сверху
        self.speed = 4
        self.angle = 0  # Направление взгляда для вида сверху

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            # Вычисляем угол направления движения
            import math
            self.angle = math.degrees(math.atan2(-dy, dx))
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        # Ограничение движения границами экрана (теперь по всей площади)
        self.rect.clamp_ip(pygame.Rect(0, 100, WIDTH, HEIGHT - 100))


def draw_person_topdown(x, y, width, height, color, angle=0):
    """Рисует человека сверху - круг с направлением"""
    center_x = x + width // 2
    center_y = y + height // 2
    
    # Тело (круг)
    radius = width // 2
    pygame.draw.circle(screen, color, (center_x, center_y), radius)
    
    # Направление взгляда (линия или небольшой круг спереди)
    import math
    rad = math.radians(angle)
    front_x = center_x + int(radius * 0.7 * math.cos(rad))
    front_y = center_y - int(radius * 0.7 * math.sin(rad))
    pygame.draw.circle(screen, WHITE, (front_x, front_y), radius // 3)
    
    # Плечи/руки (эллипс)
    shoulder_rect = pygame.Rect(x + 4, y + 8, width - 8, height - 10)
    pygame.draw.ellipse(screen, color, shoulder_rect)


def draw_building_topdown(x, y, width, height, color, building_type="shop"):
    """Рисует здание сверху - прямоугольник с крышей"""
    # Основное здание
    pygame.draw.rect(screen, color, (x, y, width, height))
    
    # Крыша сверху (контур)
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), 3)
    
    # Дверь снизу здания
    door_width = width // 3
    door_height = 10
    door_x = x + width // 2 - door_width // 2
    door_y = y + height - door_height
    pygame.draw.rect(screen, BROWN, (door_x, door_y, door_width, door_height))
    
    # Окна
    window_size = width // 5
    window_color = LIGHT_BLUE if building_type == "shop" else ORANGE
    
    # Четыре окна по углам
    pygame.draw.rect(screen, window_color, (x + 8, y + 8, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + 8, y + 8, window_size, window_size), 2)
    
    pygame.draw.rect(screen, window_color, (x + width - 8 - window_size, y + 8, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + width - 8 - window_size, y + 8, window_size, window_size), 2)
    
    pygame.draw.rect(screen, window_color, (x + 8, y + height - 8 - window_size, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + 8, y + height - 8 - window_size, window_size, window_size), 2)
    
    pygame.draw.rect(screen, window_color, (x + width - 8 - window_size, y + height - 8 - window_size, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + width - 8 - window_size, y + height - 8 - window_size, window_size, window_size), 2)
    
    # Вывеска для магазина
    if building_type == "shop":
        sign_rect = pygame.Rect(x + width // 4, y - 10, width // 2, 8)
        pygame.draw.rect(screen, RED, sign_rect)
        pygame.draw.rect(screen, WHITE, sign_rect, 2)


def draw_house_topdown(x, y, width, height):
    """Рисует жилой дом сверху"""
    draw_building_topdown(x, y, width, height, BEIGE, "house")
    # Добавим дымоход сверху
    chimney_width = width // 6
    chimney_height = height // 6
    pygame.draw.rect(screen, DARK_GRAY, (x + width * 3 // 4 - chimney_width // 2, y - chimney_height, chimney_width, chimney_height))


def draw_police_station_topdown(x, y, width, height):
    """Рисует полицейский участок сверху"""
    draw_building_topdown(x, y, width, height, BLUE, "police")
    # Сирена на крыше
    siren_x = x + width // 2
    siren_y = y + height // 2
    pygame.draw.circle(screen, RED, (siren_x - 8, siren_y), 6)
    pygame.draw.circle(screen, BLUE, (siren_x + 8, siren_y), 6)


def draw_park_topdown(x, y, width, height):
    """Рисует парк сверху с деревьями и травой"""
    # Трава - основа парка
    pygame.draw.rect(screen, GRASS_COLOR, (x, y, width, height))
    
    # Деревья сверху (круги с центром)
    tree_positions = [
        (x + width // 4, y + height // 3),
        (x + width // 2, y + height // 2),
        (x + width * 3 // 4, y + height * 2 // 3),
        (x + width // 3, y + height * 3 // 4),
        (x + width * 2 // 3, y + height // 4),
    ]
    
    for tx, ty in tree_positions:
        # Крона дерева (круг)
        crown_radius = min(width, height) // 10
        pygame.draw.circle(screen, GREEN, (tx, ty), crown_radius)
        # Центр дерева (темнее)
        pygame.draw.circle(screen, (30, 150, 30), (tx, ty), crown_radius // 2)


def draw_road(x, y, width, height, road_type="horizontal"):
    """Рисует дорогу"""
    pygame.draw.rect(screen, ROAD_COLOR, (x, y, width, height))
    
    # Разметка дороги
    if road_type == "horizontal":
        line_y = y + height // 2
        for i in range(0, width, 40):
            pygame.draw.rect(screen, WHITE, (x + i, line_y - 2, 20, 4))
    else:  # vertical
        line_x = x + width // 2
        for i in range(0, height, 40):
            pygame.draw.rect(screen, WHITE, (line_x - 2, y + i, 4, 20))


def draw_sidewalk(x, y, width, height):
    """Рисует тротуар"""
    pygame.draw.rect(screen, SIDEWALK_COLOR, (x, y, width, height))
    # Узор плитки
    tile_size = 20
    for row in range(0, height, tile_size):
        for col in range(0, width, tile_size):
            pygame.draw.rect(screen, GRAY, (x + col, y + row, tile_size - 2, tile_size - 2), 1)


def draw_water(x, y, width, height):
    """Рисует воду (озеро, река)"""
    pygame.draw.rect(screen, WATER_COLOR, (x, y, width, height))
    # Волны
    for i in range(0, width, 30):
        for j in range(0, height, 30):
            pygame.draw.arc(screen, (100, 180, 255), (x + i, y + j, 25, 25), 0, 3.14, 2)


# Класс Объектов (Магазины, Люди, Здания)
class GameObject:

    def __init__(self, x, y, width, height, color, obj_type, name, location=0, interaction_text=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.type = obj_type  # 'shop', 'person', 'building', 'park'
        self.name = name
        self.location = location  # Номер локации
        self.interaction_text = interaction_text or []
        self.last_interaction_time = 0  # Время последнего взаимодействия


# Локации с приглушёнными тёмными фонами и поверхностями
locations = [
    {"name": "Центральный район", "bg_color": DARK_BG_1, 
     "roads": [(0, 280, WIDTH, 60)],  # Горизонтальная дорога по центру
     "sidewalks": [(0, 270, WIDTH, 10), (0, 340, WIDTH, 10)]},  # Тротуары
    {"name": "Жилой район", "bg_color": DARK_BG_2,
     "roads": [(150, 0, 50, HEIGHT), (600, 0, 50, HEIGHT)],  # Вертикальные дороги
     "sidewalks": [(140, 0, 10, HEIGHT), (200, 0, 10, HEIGHT), (590, 0, 10, HEIGHT), (650, 0, 10, HEIGHT)]},
    {"name": "Промышленная зона", "bg_color": DARK_BG_3,
     "roads": [(0, 300, WIDTH, 80)],  # Широкая дорога
     "sidewalks": [(0, 290, WIDTH, 10), (0, 380, WIDTH, 10)],
     "water": [(50, 450, 150, 80)]},  # Водоём
    {"name": "Парковая зона", "bg_color": DARK_BG_4,
     "roads": [(0, 0, 40, HEIGHT), (WIDTH-40, 0, 40, HEIGHT)],  # Дороги по краям
     "sidewalks": [(40, 0, 20, HEIGHT), (WIDTH-60, 0, 20, HEIGHT)],
     "grass_areas": [(100, 150, 200, 300), (400, 200, 250, 250)]},  # Зоны травы
]

# Создание объектов на карте
player = Player()

# Журнал действий для отображения последних событий
action_log = []

objects = [
    # Центральный район (0)
    GameObject(150, 200, 100, 80, RED, "shop", "Магазин продуктов", 0, 
               ["Вы купили продукты (-100 руб, +20 сытости)", "Недостаточно денег!"]),
    GameObject(600, 150, 100, 80, PURPLE, "shop", "Аптека", 0,
               ["Вы купили лекарства (-50 руб, +30 здоровья)", "Недостаточно денег!"]),
    GameObject(350, 400, 30, 40, YELLOW, "person", "Прохожий", 0,
               ["Прохожий: 'Привет, иди поработай'", "Прохожий занят"]),
    GameObject(500, 450, 30, 40, ORANGE, "person", "Уличный музыкант", 0,
               ["Музыкант поделился мелочью (+5 руб)", "Музыкант сегодня без настроения"]),
    GameObject(250, 350, 30, 40, CYAN, "person", "Таксист", 0,
               ["Таксист предлагает работу (+15 руб)", "Таксист уже уехал"]),
    GameObject(700, 380, 30, 40, PINK, "person", "Турист", 0,
               ["Турист дал чаевые (+10 руб)", "Турист не говорит по-русски"]),
    
    # Жилой район (1)
    GameObject(100, 200, 120, 100, BEIGE, "building", "Многоквартирный дом", 1,
               ["Вы зашли домой и отдохнули (+10 здоровья)", "Дом закрыт"]),
    GameObject(300, 180, 100, 90, BEIGE, "building", "Кафе", 1,
               ["Вы пообедали в кафе (-30 руб, +25 сытости)", "Кафе закрыто или нет денег"]),
    GameObject(550, 250, 30, 40, LIME, "person", "Рабочий", 1,
               ["Рабочий: 'Хорошего дня!'", "Рабочий спешит на работу"]),
    GameObject(650, 200, 110, 95, BLUE, "building", "Офис", 1,
               ["Вы нашли подработку (+15 руб)", "Вакансий нет"]),
    GameObject(450, 350, 30, 40, GOLD, "person", "Курьер", 1,
               ["Курьер поделился едой (+10 сытости)", "Курьер опаздывает"]),
    GameObject(200, 320, 100, 85, ORANGE, "building", "Пекарня", 1,
               ["Свежий хлеб (+15 сытости, -20 руб)", "Пекарня закрыта"]),
    
    # Промышленная зона (2)
    GameObject(150, 180, 130, 110, DARK_GRAY, "building", "Завод", 2,
               ["Вы поработали на заводе (+25 руб, -5 здоровья)", "Работы нет"]),
    GameObject(400, 200, 100, 85, GRAY, "building", "Склад", 2,
               ["Вы нашли ценные вещи на складе (+10 руб)", "Склад пуст"]),
    GameObject(600, 350, 30, 40, RED, "person", "Охранник", 2,
               ["Охранник: 'Проходи мимо'", "Охранник проверяет документы"]),
    GameObject(50, 350, 120, 100, PURPLE, "building", "Больница", 2,
               ["Вас подлечили бесплатно (+20 здоровья)", "Больница переполнена"]),
    GameObject(300, 380, 30, 40, CYAN, "person", "Инженер", 2,
               ["Инженер заплатил за консультацию (+20 руб)", "Инженер занят"]),
    GameObject(500, 280, 110, 90, BROWN, "building", "Гараж", 2,
               ["Подработка механиком (+18 руб)", "Нет заказов"]),
    
    # Парковая зона (3)
    GameObject(50, 150, 200, 180, GREEN, "park", "Городской парк", 3,
               ["Вы отдохнули в парке (+5 здоровья, +5 сытости)", "Парк на ремонте"]),
    GameObject(350, 200, 30, 40, LIME, "person", "Спортсмен", 3,
               ["Спортсмен: 'Занимайся спортом!'", "Спортсмен на тренировке"]),
    GameObject(500, 180, 110, 95, BROWN, "building", "Киоск с едой", 3,
               ["Вы купили хот-дог (-20 руб, +15 сытости)", "Киоск закрыт"]),
    GameObject(650, 300, 30, 40, PURPLE, "person", "Художник", 3,
               ["Художник подарил картину (+10 руб при продаже)", "Художник занят"]),
    GameObject(250, 280, 30, 40, PINK, "person", "Девушка с собакой", 3,
               ["Девушка улыбнулась (+5 настроения)", "Собака играет"]),
    GameObject(450, 320, 100, 80, CYAN, "building", "Аренда велосипедов", 3,
               ["Прогулка на велосипеде (+10 здоровья, -15 руб)", "Нет велосипедов"]),
    GameObject(600, 180, 30, 40, YELLOW, "person", "Фотокорреспондент", 3,
               ["Вас сфотографировали (+5 руб)", "Камера разряжена"]),
]


def draw_hud():
    """Отрисовка панели состояния (HUD)"""
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 100))

    # Проценты сытости и здоровья без десятичных чисел (целые числа)
    hp_text = font.render(f"Здоровье: {int(player_hp)}%", True, WHITE)
    hunger_text = font.render(f"Сытость: {int(player_hunger)}%", True, WHITE)
    money_text = font.render(f"Деньги: {player_money} руб.", True, WHITE)
    location_text = font.render(f"Район: {locations[current_location_index]['name']}", True, WHITE)
    msg_text = log_font.render(game_message, True, YELLOW)

    screen.blit(hp_text, (20, 20))
    screen.blit(hunger_text, (20, 50))
    screen.blit(money_text, (200, 20))
    screen.blit(location_text, (200, 50))
    screen.blit(msg_text, (400, 35))
    
    # Отрисовка журнала действий
    draw_action_log()


def draw_action_log():
    """Отрисовка последних действий в стиле популярных симуляторов"""
    log_y = 120
    for i, (action_text, timestamp) in enumerate(action_log[-5:]):  # Показываем последние 5 действий
        alpha = max(50, 255 - (len(action_log) - i) * 40)  # Затухание старых сообщений
        color = (min(255, alpha + 50), min(255, alpha + 100), min(255, alpha + 50))
        log_msg = log_font.render(f"> {action_text}", True, color)
        screen.blit(log_msg, (10, log_y))
        log_y += 22


def check_location_transition():
    """Проверка перехода между локациями при достижении края экрана"""
    global current_location_index, game_message
    
    if player.rect.right >= WIDTH - 5:
        # Переход вправо - следующая локация
        if current_location_index < len(locations) - 1:
            current_location_index += 1
            player.rect.left = 10
            game_message = f"Переход в район: {locations[current_location_index]['name']}"
        else:
            player.rect.right = WIDTH - 5
            
    elif player.rect.left <= 5:
        # Переход влево - предыдущая локация
        if current_location_index > 0:
            current_location_index -= 1
            player.rect.right = WIDTH - 10
            game_message = f"Переход в район: {locations[current_location_index]['name']}"
        else:
            player.rect.left = 5


def interact_with_object(obj):
    """Взаимодействие с объектом с учетом кулдауна (скрыто)"""
    global player_hp, player_hunger, player_money, game_message
    
    current_time = time.time()
    
    # Проверка кулдауна - скрыто, без отображения текста
    if current_time - obj.last_interaction_time < COOLDOWN_SECONDS:
        return  # Просто не выполняем действие, без сообщения
    
    action_performed = False
    
    # Обработка взаимодействия в зависимости от типа объекта
    if obj.type == "shop":
        if obj.name == "Магазин продуктов":
            if player_money >= 100:
                player_money -= 100
                player_hunger = min(100, player_hunger + 20)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
                
        elif obj.name == "Аптека":
            if player_money >= 50:
                player_money -= 50
                player_hp = min(100, player_hp + 30)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
                
    elif obj.type == "person":
        if obj.name == "Прохожий":
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Уличный музыкант":
            player_money += 5
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Рабочий":
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Охранник":
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Спортсмен":
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Художник":
            player_money += 10
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Таксист":
            player_money += 15
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Турист":
            player_money += 10
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Курьер":
            player_hunger = min(100, player_hunger + 10)
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Инженер":
            player_money += 20
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Девушка с собакой":
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Фотокорреспондент":
            player_money += 5
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
            
    elif obj.type == "building":
        if obj.name == "Многоквартирный дом":
            player_hp = min(100, player_hp + 10)
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Кафе":
            if player_money >= 30:
                player_money -= 30
                player_hunger = min(100, player_hunger + 25)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
        elif obj.name == "Офис":
            player_money += 15
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Завод":
            player_money += 25
            player_hp = max(0, player_hp - 5)
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Склад":
            player_money += 10
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Больница":
            player_hp = min(100, player_hp + 20)
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Киоск с едой":
            if player_money >= 20:
                player_money -= 20
                player_hunger = min(100, player_hunger + 15)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
        elif obj.name == "Пекарня":
            if player_money >= 20:
                player_money -= 20
                player_hunger = min(100, player_hunger + 15)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
        elif obj.name == "Гараж":
            player_money += 18
            game_message = obj.interaction_text[0]
            action_log.append((obj.interaction_text[0], current_time))
            action_performed = True
        elif obj.name == "Аренда велосипедов":
            if player_money >= 15:
                player_money -= 15
                player_hp = min(100, player_hp + 10)
                game_message = obj.interaction_text[0]
                action_log.append((obj.interaction_text[0], current_time))
                action_performed = True
            else:
                game_message = obj.interaction_text[1]
                
    elif obj.type == "park":
        player_hp = min(100, player_hp + 5)
        player_hunger = min(100, player_hunger + 5)
        game_message = obj.interaction_text[0]
        action_log.append((obj.interaction_text[0], current_time))
        action_performed = True
    
    # Обновляем время последнего взаимодействия только если действие произошло
    if action_performed:
        obj.last_interaction_time = current_time


# Главный игровой цикл
running = True
while running:
    clock.tick(60)  # 60 FPS
    current_location = locations[current_location_index]
    screen.fill(current_location["bg_color"])

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление персонажем
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx = -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = 1

    if dx != 0 or dy != 0:
        player.move(dx, dy)
        # Постепенный расход сытости при движении
        player_hunger -= 0.02
        if player_hunger <= 0:
            player_hunger = 0
            player_hp -= 0.05

    # Проверка перехода между локациями
    check_location_transition()

    # Отрисовка поверхностей локации (дороги, тротуары, вода, трава)
    current_loc = locations[current_location_index]
    
    # Рисуем дороги
    if "roads" in current_loc:
        for road in current_loc["roads"]:
            draw_road(road[0], road[1], road[2], road[3])
    
    # Рисуем тротуары
    if "sidewalks" in current_loc:
        for sidewalk in current_loc["sidewalks"]:
            draw_sidewalk(sidewalk[0], sidewalk[1], sidewalk[2], sidewalk[3])
    
    # Рисуем воду
    if "water" in current_loc:
        for water in current_loc["water"]:
            draw_water(water[0], water[1], water[2], water[3])
    
    # Рисуем зоны травы
    if "grass_areas" in current_loc:
        for grass in current_loc["grass_areas"]:
            pygame.draw.rect(screen, GRASS_COLOR, (grass[0], grass[1], grass[2], grass[3]))

    # Отрисовка и обработка объектов города
    for obj in objects:
        # Рисуем только объекты текущей локации
        if obj.location == current_location_index:
            # Отрисовка в зависимости от типа объекта
            if obj.type == "person":
                draw_person_topdown(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height, obj.color, player.angle)
            elif obj.type == "park":
                draw_park_topdown(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height)
            else:  # shop, building
                draw_building_topdown(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height, obj.color, obj.type)
            
            # Подписи над объектами
            name_tag = log_font.render(obj.name, True, WHITE)
            screen.blit(name_tag, (obj.rect.x - 10, obj.rect.y - 20))

            # Проверка столкновения (взаимодействия) игрока с объектом
            if player.rect.colliderect(obj.rect):
                interact_with_object(obj)

    # Проверка условий проигрыша
    if player_hp <= 0:
        game_message = "Вы не выжили. Нажмите R для рестарта."
        player_hp = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            player_hp = 100
            player_hunger = 100
            player_money = 50
            current_location_index = 0
            player.rect = pygame.Rect(400, 300, 30, 30)
            game_message = "Новая игра началась!"

    # Отрисовка игрока (силуэт человека)
    draw_person_topdown(player.rect.x, player.rect.y, player.rect.width, player.rect.height, BLUE, player.angle)

    # Отрисовка интерфейса
    draw_hud()

    pygame.display.flip()

pygame.quit()
sys.exit()