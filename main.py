import sys
import pygame
import time

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выживание в городе")
clock = pygame.time.Clock()

# Цвета
GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLUE = (56, 2, 255)
RED = (255, 7, 0)
BLACK = (3, 0, 0)
YELLOW = (15, 215, 0)
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BEIGE = (245, 245, 220)

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


# Класс Игрока
class Player:

    def __init__(self):
        self.rect = pygame.Rect(400, 300, 30, 30)
        self.speed = 4
        self.direction = 1  # 1 = вправо, -1 = влево

    def move(self, dx, dy):
        if dx != 0:
            self.direction = dx
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        # Ограничение движения границами экрана
        self.rect.clamp_ip(pygame.Rect(0, 100, WIDTH, HEIGHT - 100))


def draw_person(x, y, width, height, color, direction=1):
    """Рисует силуэт человека из простых элементов"""
    # Голова
    head_radius = width // 4
    head_center = (x + width // 2, y + head_radius)
    pygame.draw.circle(screen, color, head_center, head_radius)
    
    # Тело
    body_rect = pygame.Rect(x + width // 4, y + head_radius * 2, width // 2, height // 2)
    pygame.draw.rect(screen, color, body_rect)
    
    # Ноги
    leg_width = width // 6
    leg_height = height // 3
    left_leg = pygame.Rect(x + width // 6, y + height - leg_height, leg_width, leg_height)
    right_leg = pygame.Rect(x + width // 2 + width // 12, y + height - leg_height, leg_width, leg_height)
    pygame.draw.rect(screen, color, left_leg)
    pygame.draw.rect(screen, color, right_leg)
    
    # Руки
    arm_width = width // 8
    arm_height = height // 4
    arm_offset = direction * 5
    left_arm = pygame.Rect(x + width // 8 - arm_offset, y + head_radius * 2 + 5, arm_width, arm_height)
    right_arm = pygame.Rect(x + width // 2 + width // 8 + arm_offset, y + head_radius * 2 + 5, arm_width, arm_height)
    pygame.draw.rect(screen, color, left_arm)
    pygame.draw.rect(screen, color, right_arm)


def draw_building(x, y, width, height, color, building_type="shop"):
    """Рисует здание из простых элементов"""
    # Основное здание
    pygame.draw.rect(screen, color, (x, y + height // 4, width, height * 3 // 4))
    
    # Крыша
    roof_points = [(x - 10, y + height // 4), (x + width // 2, y), (x + width + 10, y + height // 4)]
    pygame.draw.polygon(screen, DARK_GRAY, roof_points)
    
    # Дверь
    door_width = width // 4
    door_height = height // 3
    door_x = x + width // 2 - door_width // 2
    door_y = y + height - door_height
    pygame.draw.rect(screen, BROWN, (door_x, door_y, door_width, door_height))
    
    # Окна
    window_size = width // 6
    window_color = LIGHT_BLUE if building_type == "shop" else ORANGE
    
    # Левое окно
    pygame.draw.rect(screen, window_color, (x + width // 8, y + height // 2, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + width // 8, y + height // 2, window_size, window_size), 2)
    
    # Правое окно
    pygame.draw.rect(screen, window_color, (x + width - width // 8 - window_size, y + height // 2, window_size, window_size))
    pygame.draw.rect(screen, BLACK, (x + width - width // 8 - window_size, y + height // 2, window_size, window_size), 2)
    
    # Вывеска для магазина
    if building_type == "shop":
        sign_rect = pygame.Rect(x + width // 4, y + height // 4 - 15, width // 2, 20)
        pygame.draw.rect(screen, RED, sign_rect)
        pygame.draw.rect(screen, WHITE, sign_rect, 2)


def draw_house(x, y, width, height):
    """Рисует жилой дом"""
    draw_building(x, y, width, height, BEIGE, "house")
    # Добавим дымоход
    chimney_width = width // 8
    chimney_height = height // 4
    pygame.draw.rect(screen, DARK_GRAY, (x + width * 3 // 4, y - chimney_height // 2, chimney_width, chimney_height))


def draw_police_station(x, y, width, height):
    """Рисует полицейский участок"""
    draw_building(x, y, width, height, BLUE, "police")
    # Сирена на крыше
    siren_x = x + width // 2
    siren_y = y - 10
    pygame.draw.circle(screen, RED, (siren_x - 10, siren_y), 8)
    pygame.draw.circle(screen, BLUE, (siren_x + 10, siren_y), 8)


def draw_park(x, y, width, height):
    """Рисует парк с деревьями"""
    # Трава
    pygame.draw.rect(screen, GREEN, (x, y, width, height))
    
    # Деревья
    tree_positions = [
        (x + width // 4, y + height // 2),
        (x + width // 2, y + height // 3),
        (x + width * 3 // 4, y + height // 2),
    ]
    
    for tx, ty in tree_positions:
        # Ствол
        trunk_width = width // 15
        trunk_height = height // 4
        pygame.draw.rect(screen, BROWN, (tx - trunk_width // 2, ty, trunk_width, trunk_height))
        
        # Крона
        crown_radius = width // 8
        pygame.draw.circle(screen, GREEN, (tx, ty - trunk_height // 2), crown_radius)
        pygame.draw.circle(screen, GREEN, (tx - crown_radius // 2, ty - trunk_height), crown_radius // 1.5)
        pygame.draw.circle(screen, GREEN, (tx + crown_radius // 2, ty - trunk_height), crown_radius // 1.5)


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


# Локации
locations = [
    {"name": "Центральный район", "bg_color": GRAY},
    {"name": "Жилой район", "bg_color": BEIGE},
    {"name": "Промышленная зона", "bg_color": DARK_GRAY},
    {"name": "Парковая зона", "bg_color": GREEN},
]

# Создание объектов на карте
player = Player()

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
    
    # Жилой район (1)
    GameObject(100, 200, 120, 100, BEIGE, "building", "Многоквартирный дом", 1,
               ["Вы зашли домой и отдохнули (+10 здоровья)", "Дом закрыт"]),
    GameObject(300, 180, 100, 90, BEIGE, "building", "Кафе", 1,
               ["Вы пообедали в кафе (-30 руб, +25 сытости)", "Кафе закрыто или нет денег"]),
    GameObject(550, 250, 30, 40, BLUE, "person", "Рабочий", 1,
               ["Рабочий: 'Хорошего дня!'", "Рабочий спешит на работу"]),
    GameObject(650, 200, 110, 95, BLUE, "building", "Офис", 1,
               ["Вы нашли подработку (+15 руб)", "Вакансий нет"]),
    
    # Промышленная зона (2)
    GameObject(150, 180, 130, 110, DARK_GRAY, "building", "Завод", 2,
               ["Вы поработали на заводе (+25 руб, -5 здоровья)", "Работы нет"]),
    GameObject(400, 200, 100, 85, GRAY, "building", "Склад", 2,
               ["Вы нашли ценные вещи на складе (+10 руб)", "Склад пуст"]),
    GameObject(600, 350, 30, 40, RED, "person", "Охранник", 2,
               ["Охранник: 'Проходи мимо'", "Охранник проверяет документы"]),
    GameObject(50, 350, 120, 100, PURPLE, "building", "Больница", 2,
               ["Вас подлечили бесплатно (+20 здоровья)", "Больница переполнена"]),
    
    # Парковая зона (3)
    GameObject(50, 150, 200, 180, GREEN, "park", "Городской парк", 3,
               ["Вы отдохнули в парке (+5 здоровья, +5 сытости)", "Парк на ремонте"]),
    GameObject(350, 200, 30, 40, GREEN, "person", "Спортсмен", 3,
               ["Спортсмен: 'Занимайся спортом!'", "Спортсмен на тренировке"]),
    GameObject(500, 180, 110, 95, BROWN, "building", "Киоск с едой", 3,
               ["Вы купили хот-дог (-20 руб, +15 сытости)", "Киоск закрыт"]),
    GameObject(650, 300, 30, 40, PURPLE, "person", "Художник", 3,
               ["Художник подарил картину (+10 руб при продаже)", "Художник занят"]),
]


def draw_hud():
    """Отрисовка панели состояния (HUD)"""
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 100))

    hp_text = font.render(f"Здоровье: {player_hp}%", True, WHITE)
    hunger_text = font.render(f"Сытость: {player_hunger}%", True, WHITE)
    money_text = font.render(f"Деньги: {player_money} руб.", True, WHITE)
    location_text = font.render(f"Район: {locations[current_location_index]['name']}", True, WHITE)
    msg_text = log_font.render(game_message, True, YELLOW)

    screen.blit(hp_text, (20, 20))
    screen.blit(hunger_text, (20, 50))
    screen.blit(money_text, (200, 20))
    screen.blit(location_text, (200, 50))
    screen.blit(msg_text, (400, 35))


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
    """Взаимодействие с объектом с учетом кулдауна"""
    global player_hp, player_hunger, player_money, game_message
    
    current_time = time.time()
    
    # Проверка кулдауна
    if current_time - obj.last_interaction_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (current_time - obj.last_interaction_time))
        game_message = f"Подождите {remaining} сек. до следующего взаимодействия"
        return
    
    # Обработка взаимодействия в зависимости от типа объекта
    if obj.type == "shop":
        if obj.name == "Магазин продуктов":
            if player_money >= 100:
                player_money -= 100
                player_hunger = min(100, player_hunger + 20)
                game_message = obj.interaction_text[0]
                obj.last_interaction_time = current_time
            else:
                game_message = obj.interaction_text[1]
                
        elif obj.name == "Аптека":
            if player_money >= 50:
                player_money -= 50
                player_hp = min(100, player_hp + 30)
                game_message = obj.interaction_text[0]
                obj.last_interaction_time = current_time
            else:
                game_message = obj.interaction_text[1]
                
    elif obj.type == "person":
        if obj.name == "Прохожий":
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Уличный музыкант":
            player_money += 5
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Рабочий":
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Охранник":
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Спортсмен":
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Художник":
            player_money += 10
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
            
    elif obj.type == "building":
        if obj.name == "Многоквартирный дом":
            player_hp = min(100, player_hp + 10)
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Кафе":
            if player_money >= 30:
                player_money -= 30
                player_hunger = min(100, player_hunger + 25)
                game_message = obj.interaction_text[0]
                obj.last_interaction_time = current_time
            else:
                game_message = obj.interaction_text[1]
        elif obj.name == "Офис":
            player_money += 15
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Завод":
            player_money += 25
            player_hp = max(0, player_hp - 5)
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Склад":
            player_money += 10
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Больница":
            player_hp = min(100, player_hp + 20)
            game_message = obj.interaction_text[0]
            obj.last_interaction_time = current_time
        elif obj.name == "Киоск с едой":
            if player_money >= 20:
                player_money -= 20
                player_hunger = min(100, player_hunger + 15)
                game_message = obj.interaction_text[0]
                obj.last_interaction_time = current_time
            else:
                game_message = obj.interaction_text[1]
                
    elif obj.type == "park":
        player_hp = min(100, player_hp + 5)
        player_hunger = min(100, player_hunger + 5)
        game_message = obj.interaction_text[0]
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

    # Отрисовка и обработка объектов города
    for obj in objects:
        # Рисуем только объекты текущей локации
        if obj.location == current_location_index:
            # Отрисовка в зависимости от типа объекта
            if obj.type == "person":
                draw_person(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height, obj.color, player.direction)
            elif obj.type == "park":
                draw_park(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height)
            else:  # shop, building
                draw_building(obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height, obj.color, obj.type)
            
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
    draw_person(player.rect.x, player.rect.y, player.rect.width, player.rect.height, BLUE, player.direction)

    # Отрисовка интерфейса
    draw_hud()

    pygame.display.flip()

pygame.quit()
sys.exit()