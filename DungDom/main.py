import pygame
import random
import time
import math

# Configuración de la Pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 720
TELEPORT_WIDTH, TELEPORT_HEIGHT = 970, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Seleccionar Clase")
FPS = 30
clock = pygame.time.Clock()

# Inicializando Pygame
pygame.init()

# Fuentes y Opciones de Menú
font = pygame.font.Font(None, 74)
title_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 36)

menu_options = ["Empezar Partida", "Acerca de", "Salir"]
class_options = ["Mago", "Asesino", "Tanque", "Ladrón", "Pirata"]
selected_option = 0
selected_class_option = 0

# Velocidad constante ajustada
CONSTANT_SPEED = 6
CHARACTER_SPEED = 8


# Definición e Instancias de Clases de Personaje
class CharacterClass:
    def __init__(self, name, image_path, health, damage, attack_range):
        self.name = name
        self.image_path = image_path
        self.health = health
        self.damage = damage
        self.attack_range = attack_range


# Definición de las clases con sus respectivos rangos de ataque
clases = {
    "Mago": CharacterClass("Mago", "assets/mage.png", 100, 20, 200),
    "Asesino": CharacterClass("Asesino", "assets/assassin.png", 75, 25, 150),
    "Tanque": CharacterClass("Tanque", "assets/tank.png", 150, 15, 50),
    "Ladrón": CharacterClass("Ladrón", "assets/thief.png", 85, 22, 120),
    "Pirata": CharacterClass("Pirata", "assets/pirate.png", 100, 20, 130)
}

# Lista de Enemigos y Spawneo
enemies = []
player_health = None  # Variable global para la salud del jugador


# Definición de Clases de Enemigos
class Enemy:
    def __init__(self, image_path, health, damage):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.health = health
        self.damage = damage
        self.speed = CONSTANT_SPEED
        self.attack_interval = 1
        self.last_attack_time = time.time()
        self.hitbox = pygame.Rect(0, 0, 60, 60)
        self.spawn()

    def spawn(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect.x = random.randint(0, TELEPORT_WIDTH)
            self.rect.y = -self.rect.height
        elif side == 'bottom':
            self.rect.x = random.randint(0, TELEPORT_WIDTH)
            self.rect.y = TELEPORT_HEIGHT
        elif side == 'left':
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, TELEPORT_HEIGHT)
        elif side == 'right':
            self.rect.x = TELEPORT_WIDTH
            self.rect.y = random.randint(0, TELEPORT_HEIGHT)
        self.hitbox.center = self.rect.center

    def update(self, player_hitbox, current_time):
        dx, dy = player_hitbox.centerx - self.hitbox.centerx, player_hitbox.centery - self.hitbox.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        self.hitbox.center = self.rect.center

        if current_time - self.last_attack_time >= self.attack_interval:
            if self.hitbox.colliderect(player_hitbox):
                global player_health
                player_health -= self.damage
                self.last_attack_time = current_time

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Goblin(Enemy):
    def __init__(self):
        super().__init__('assets/goblin.png', 10, 2)


class Skeleton(Enemy):
    def __init__(self):
        super().__init__('assets/skeleton.png', 20, 2)


class Rat(Enemy):
    def __init__(self):
        super().__init__('assets/rat.png', 20, 1)


class Monk(Enemy):
    def __init__(self):
        super().__init__('assets/monk.png', 30, 3)


class Snake(Enemy):
    def __init__(self):
        super().__init__('assets/snake.png', 30, 2)


class Inferno(Enemy):
    def __init__(self):
        super().__init__('assets/inferno.png', 40, 4)


# Lógica de Fases de Spawneo
enemy_spawn_phases = [
    (Goblin, 30),
    (Skeleton, 30),
    (Rat, 30),
    (Monk, 30),
    (Snake, 30),
    (Inferno, 30)
]

# Variables globales para las fases de spawneo
current_phase_index = 0
phase_start_time = None
spawn_rate = 1
last_spawn_time = None
last_attack_time = None


# Función para el dibujado de texto centrado
def draw_text_centered(text, font, color, screen, center_pos):
    text_render = font.render(text, True, color)
    text_rect = text_render.get_rect(center=center_pos)
    screen.blit(text_render, text_rect)
    return text_rect


# Función para el dibujado de texto en una posición específica
def draw_text(text, font, color, screen, pos):
    text_render = font.render(text, True, color)
    screen.blit(text_render, pos)
    return text_render.get_rect(topleft=pos)


def draw_health_bar(screen, x, y, health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (health / max_health) * bar_width
    border_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, (255, 0, 0), fill_rect)
    pygame.draw.rect(screen, (0, 0, 0), border_rect, 2)


# Función para manejar los eventos del menú principal
def handle_events(option_rects, action_callbacks, key_callbacks):
    global selected_option
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key in key_callbacks:
                key_callbacks[event.key]()
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(event.pos):
                    selected_option = i
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(event.pos):
                    action_callbacks[i]()


def main_menu(screen):
    global selected_option, enemies
    selected_option = 0
    enemies.clear()
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen_width, screen_height = screen.get_size()
        option_rects = []
        for i, option in enumerate(menu_options):
            color = (255, 255, 255) if i != selected_option else (255, 0, 0)
            text_rect = draw_text_centered(option, font, color, screen, (screen_width / 2, 150 + i * 100))
            option_rects.append(text_rect)
        pygame.display.flip()
        action_callbacks = [lambda: select_class(screen), lambda: show_about(screen), lambda: quit_game()]
        key_callbacks = {
            pygame.K_UP: lambda: select_option(-1, len(menu_options)),
            pygame.K_DOWN: lambda: select_option(1, len(menu_options)),
            pygame.K_RETURN: lambda: execute_action(action_callbacks[selected_option])
        }
        handle_events(option_rects, action_callbacks, key_callbacks)


def select_option(delta, max_options):
    global selected_option
    selected_option = (selected_option + delta) % max_options


# Función para manejar los eventos de selección de clase
def handle_events_class_selection(option_rects, action_callbacks, key_callbacks):
    global selected_class_option
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key in key_callbacks:
                key_callbacks[event.key]()
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(event.pos):
                    selected_class_option = i
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(event.pos):
                    if i < len(action_callbacks):
                        action_callbacks[i]()


def select_class(screen):
    global selected_class_option
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen_width, screen_height = screen.get_size()
        draw_text_centered("Selecciona tu clase", title_font, (255, 255, 255), screen, (screen_width / 2, 50))
        option_rects = []
        for i, option in enumerate(class_options):
            color = (255, 255, 255) if i != selected_class_option else (255, 0, 0)
            text_rect = draw_text_centered(option, font, color, screen, (screen_width / 2, 150 + i * 100))
            option_rects.append(text_rect)
        back_button_rect = draw_text("Volver", button_font, (255, 255, 255), screen, (20, screen_height - 50))
        pygame.display.flip()
        action_callbacks = [lambda: start_selected_game(screen) for i in range(len(class_options))] + [return_to_menu]
        key_callbacks = {
            pygame.K_UP: lambda: select_class_option(-1, len(class_options)),
            pygame.K_DOWN: lambda: select_class_option(1, len(class_options)),
            pygame.K_RETURN: lambda: execute_action(action_callbacks[selected_class_option]),
            pygame.K_ESCAPE: return_to_menu
        }
        handle_events_class_selection(option_rects, action_callbacks, key_callbacks)
        if check_back_button(back_button_rect):
            return_to_menu()


def select_class_option(delta, max_options):
    global selected_class_option
    selected_class_option = (selected_class_option + delta) % max_options


def execute_action(action_callback):
    action_callback()


def start_selected_game(screen):
    global phase_start_time, last_spawn_time, current_phase_index, player_health
    phase_start_time = None
    last_spawn_time = None
    current_phase_index = 0
    character = clases[class_options[selected_class_option]]
    player_health = character.health
    control_character_screen(screen, character)


def control_character_screen(screen, character):
    global phase_start_time, last_spawn_time, current_phase_index, last_attack_time, player_health

    background_image = pygame.image.load("assets/background.png").convert()
    character_image = pygame.image.load(character.image_path).convert_alpha()
    character_rect = character_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    move_speed = CHARACTER_SPEED

    hitbox = pygame.Rect(0, 0, 60, 60)
    hitbox.center = character_rect.center

    running = True
    phase_start_time = time.time()
    last_spawn_time = phase_start_time
    last_attack_time = phase_start_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_menu()
                return

        keys = pygame.key.get_pressed()
        character_rect_velocity = [0, 0]

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            character_rect_velocity[1] -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            character_rect_velocity[1] += move_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            character_rect_velocity[0] -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            character_rect_velocity[0] += move_speed

        character_rect.move_ip(*character_rect_velocity)
        hitbox.center = character_rect.center

        # Teletransporte del personaje dentro del área específica de teletransporte
        if character_rect.left > TELEPORT_WIDTH:
            character_rect.right = 0
        elif character_rect.right < 0:
            character_rect.left = TELEPORT_WIDTH
        if character_rect.top > TELEPORT_HEIGHT:
            character_rect.bottom = 0
        elif character_rect.bottom < 0:
            character_rect.top = TELEPORT_HEIGHT

        current_time = time.time()

        # Chequeo para cambiar la fase de spawneo usando tiempo
        elapsed_time = current_time - phase_start_time
        if elapsed_time >= enemy_spawn_phases[current_phase_index][1]:
            current_phase_index += 1
            if current_phase_index >= len(enemy_spawn_phases):
                show_victory(screen)  # Muestra la pantalla de victoria
                return
            phase_start_time = current_time
            last_spawn_time = current_time

        # Spawneo de enemigos de la fase actual
        enemy_class, _ = enemy_spawn_phases[current_phase_index]

        if current_time - last_spawn_time >= spawn_rate:
            spawn_enemy(enemy_class, 3)
            last_spawn_time = current_time

        screen.blit(background_image, (0, 0))

        # Movimiento y autoataque de enemigos
        for enemy in enemies:
            enemy.update(hitbox, current_time)
            enemy.draw(screen)

        # Autoataque del personaje
        if current_time - last_attack_time >= 0.3:  # Disminución del tiempo de autoataque
            target = find_closest_enemy(hitbox.center)
            if target and hitbox.colliderect(target.hitbox):
                target.health -= character.damage
                if target.health <= 0:
                    enemies.remove(target)
            last_attack_time = current_time

        screen.blit(character_image, character_rect)
        draw_health_bar(screen, 10, 10, player_health, character.health)

        if player_health <= 0:
            show_game_over(screen)
            return

        pygame.display.flip()
        clock.tick(FPS)


def find_closest_enemy(position):
    closest_enemy = None
    min_distance = float('inf')
    for enemy in enemies:
        distance = math.hypot(enemy.rect.centerx - position[0], enemy.rect.centery - position[1])
        if distance < min_distance:
            min_distance = distance
            closest_enemy = enemy
    return closest_enemy


def spawn_enemy(enemy_class, count):
    for _ in range(count):
        enemies.append(enemy_class())


def show_victory(screen):
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen_width, screen_height = screen.get_size()
        draw_text_centered("¡Victoria!", title_font, (0, 255, 0), screen, (screen_width / 2, 200))
        draw_text_centered("¡Has derrotado a todos los enemigos!", font, (255, 255, 255), screen,
                           (screen_width / 2, 300))
        back_button_rect = draw_text("", button_font, (255, 255, 255), screen, (20, screen_height - 50))
        pygame.display.flip()
        time.sleep(3)  # Pausa por unos instantes
        return_to_menu()
        return


def show_game_over(screen):
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen_width, screen_height = screen.get_size()
        draw_text_centered("¡Juego Terminado!", title_font, (255, 0, 0), screen, (screen_width / 2, 200))
        draw_text_centered("Gracias por jugar.", font, (255, 255, 255), screen, (screen_width / 2, 300))
        back_button_rect = draw_text("", button_font, (255, 255, 255), screen, (20, screen_height - 50))
        pygame.display.flip()
        time.sleep(3)  # Pausa por unos instantes
        return_to_menu()
        return


def show_about(screen):
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen_width, screen_height = screen.get_size()
        draw_text_centered("Acerca de", title_font, (255, 255, 255), screen, (screen_width / 2, 50))
        about_font = pygame.font.Font(None, 36)
        about_lines = ["Descripción del juego..."]
        for i, line in enumerate(about_lines):
            draw_text_centered(line, about_font, (255, 255, 255), screen, (screen_width / 2, 150 + i * 40))
        back_button_rect = draw_text("Volver", button_font, (255, 255, 255), screen, (20, screen_height - 50))
        pygame.display.flip()
        if check_back_button(back_button_rect):
            return_to_menu()


def quit_game():
    pygame.quit()
    quit()


def check_back_button(button_rect):
    for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                return True
    return False


def return_to_menu():
    main_menu(screen)


if __name__ == "__main__":
    main_menu(screen)
