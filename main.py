import sys
import pygame

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

# Шрифты
font = pygame.font.SysFont("Arial", 18)
log_font = pygame.font.SysFont("Arial", 16)

# Игровые параметры
player_hp = 100
player_hunger = 100
player_money = 50
current_city = "Центральный"
game_message = (
    "Добро пожаловать! Ходите по городу (WASD / стрелки). Подходите к объектам."
)


# Класс Игрока
class Player:

    def __init__(self):
        self.rect = pygame.Rect(400, 300, 30, 30)  # Размеры персонажа
        self.speed = 4

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        # Ограничение движения границами экрана
        self.rect.clamp_ip(pygame.Rect(0, 100, WIDTH, HEIGHT - 100))


# Класс Объектов (Магазины, Люди)
class GameObject:

    def __init__(self, x, y, width, height, color, obj_type, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.type = obj_type  # 'shop' или 'person'
        self.name = name


# Создание объектов на карте
player = Player()
objects = [
    GameObject(150, 200, 80, 60, RED, "shop", "Магазин продуктов"),
    GameObject(600, 150, 80, 60, RED, "shop", "Аптека"),
    GameObject(200, 450, 25, 25, YELLOW, "person", "Прохожий"),
    GameObject(550, 400, 25, 25, YELLOW, "person", "Уличный музыкант"),
]


def draw_hud():
    """Отрисовка панели состояния (HUD)"""
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 100))

    hp_text = font.render(f"Здоровье: {player_hp}%", True, WHITE)
    hunger_text = font.render(f"Сытость: {player_hunger}%", True, WHITE)
    money_text = font.render(f"Деньги: {player_money} руб.", True, WHITE)
    city_text = font.render(f"Город: {current_city}", True, WHITE)
    msg_text = log_font.render(game_message, True, YELLOW)

    screen.blit(hp_text, (20, 20))
    screen.blit(hunger_text, (20, 50))
    screen.blit(money_text, (200, 20))
    screen.blit(city_text, (200, 50))
    screen.blit(msg_text, (400, 35))


# Главный игровой цикл
running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.fill(GRAY)  # Цвет асфальта/города

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

    # Отрисовка объектов города
    for obj in objects:
        pygame.draw.rect(screen, obj.color, obj.rect)
        # Подписи над объектами
        name_tag = log_font.render(obj.name, True, WHITE)
        screen.blit(name_tag, (obj.rect.x - 10, obj.rect.y - 20))

        # Проверка столкновения (взаимодействия) игрока с объектом
        if player.rect.colliderect(obj.rect):
            if obj.type == "shop":
                if obj.name == "Магазин продуктов" and player_money >= 10:
                    player_money -= 1000
                    player_hunger = min(100, player_hunger + 20)
                    game_message = "Вы купили еду в магазине (-1000 руб, +20 сытости)"
                elif obj.name == "Аптека" and player_money >= 20:
                    player_money -= 20
                    player_hp = min(100, player_hp + 30)
                    game_message = "Вы купили аптечку (-20 руб, +30 здоровья)"
                else:
                    game_message = "Недостаточно денег для покупки!"

            elif obj.type == "person":
                if obj.name == "Прохожий":
                    game_message = (
                        "Прохожий: 'Привет иди поработай'"
                    )
                elif obj.name == "Уличный музыкант":
                    player_money += 1
                    game_message = "Музыкант поделился мелочью (+1 руб)"

            # Отталкиваем игрока слегка назад, чтобы не застревать в текстурах
            player.move(-dx, -dy)

    # Проверка условий проигрыша
    if player_hp <= 0:
        game_message = "Вы не выжили."
        player_hp = 0

    # Отрисовка игрока (Синий квадрат)
    pygame.draw.rect(screen, BLUE, player.rect)

    # Отрисовка интерфейса
    draw_hud()

    pygame.display.flip()

pygame.quit()
sys.exit()