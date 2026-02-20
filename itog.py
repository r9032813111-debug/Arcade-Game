import arcade
import random
import math
import os
from arcade import rect as arc_rect
from arcade.gui import UIManager, UIBoxLayout, UIFlatButton, UIAnchorLayout
from arcade.camera import Camera2D

# ==================== Константы ====================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "П О С Л Е"

PLAYER_SPEED = 7
VACUUM_RANGE_BASE = 50
VACUUM_UPGRADE_COST = 130
VACUUM_UPGRADE_INCREMENT = 25

CLOUD_POINTS = 20
FINAL_LEVEL_INDEX = 4
MIN_MONEY_FOR_TRAP = 650

TILE_SIZE = 80
TRANSITION_DURATION = 2.0

COLOR_WALL = arcade.color.GRAY
COLOR_FLOOR = arcade.color.LIGHT_GRAY
COLOR_PLAYER = arcade.color.DODGER_BLUE
COLOR_CLOUD = arcade.color.LIME_GREEN
COLOR_VACUUM = arcade.color.YELLOW
COLOR_TEXT_DARK = arcade.color.DIM_GRAY
COLOR_TRAP = arcade.color.RED
COLOR_TRAP_INACTIVE = arcade.color.DARK_RED

# Новые константы для экономики
INITIAL_MONEY = 300
VACUUM_COST_PER_SECOND = 8
VACUUM_START_COST = 20

ROOM_LAYOUTS = [
    # Уровень 1 — открытая (10x8)
    [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],

    # Уровень 2 — перегородки (10x8)
    [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
     [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
     [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
     [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 1, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 1, 0, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],

    # Уровень 3 — лабиринт (10x8)
    [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
     [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
     [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
     [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
     [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
     [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
     [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],

    # Уровень 4 — крест с коридорами (10x8)
    [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
     [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
     [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
     [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],

    # Уровень 5 — ловушка с препятствиями (10x8)
    [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
]


class Player:
    def __init__(self):
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.width = 40
        self.height = 40
        self.vacuum_range = VACUUM_RANGE_BASE
        self.score = INITIAL_MONEY
        self.upgrades = 0
        self.vacuum_on = False
        self.vacuum_angle = 0
        self.vacuum_active_time = 0.0
        self.total_vacuum_cost = 0
        self.last_payment_time = 0.0

    def draw(self):
        # Рисуем игрока
        arcade.draw_rect_filled(
            arc_rect.XYWH(self.center_x, self.center_y, self.width, self.height),
            COLOR_PLAYER
        )

        if self.vacuum_on:
            cone_color = (COLOR_VACUUM[0], COLOR_VACUUM[1], COLOR_VACUUM[2], 120)

            triangle_points = [
                (0, 0),
                (self.vacuum_range, self.vacuum_range // 2),
                (self.vacuum_range, -self.vacuum_range // 2)
            ]

            rotated_points = []
            angle_rad = math.radians(self.vacuum_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            for x, y in triangle_points:
                rotated_x = self.center_x + x * cos_a - y * sin_a
                rotated_y = self.center_y + x * sin_a + y * cos_a
                rotated_points.append((rotated_x, rotated_y))

            arcade.draw_polygon_filled(rotated_points, cone_color)

    def update_vacuum_angle(self, target_x, target_y):
        dx = target_x - self.center_x
        dy = target_y - self.center_y

        angle_rad = math.atan2(dy, dx)
        self.vacuum_angle = math.degrees(angle_rad)

    def try_upgrade(self):
        if self.score >= VACUUM_UPGRADE_COST:
            self.score -= VACUUM_UPGRADE_COST
            self.vacuum_range += VACUUM_UPGRADE_INCREMENT
            self.upgrades += 1
            return True
        return False

    def pay_vacuum_cost(self, delta_time):
        if self.vacuum_on:
            self.vacuum_active_time += delta_time

            if self.last_payment_time == 0 or self.vacuum_active_time - self.last_payment_time >= 1.0:
                if self.score >= VACUUM_COST_PER_SECOND:
                    self.score -= VACUUM_COST_PER_SECOND
                    self.total_vacuum_cost += VACUUM_COST_PER_SECOND
                    self.last_payment_time = self.vacuum_active_time
                else:
                    self.vacuum_on = False

    def start_vacuum(self):
        if self.score >= VACUUM_START_COST and not self.vacuum_on:
            self.vacuum_on = True
            self.vacuum_active_time = 0.0
            self.last_payment_time = 0.0
            self.score -= VACUUM_START_COST
            self.total_vacuum_cost += VACUUM_START_COST
            return True
        elif self.vacuum_on:
            return True
        else:
            return False


class Cloud(arcade.Sprite):
    def __init__(self, x, y, texture=None):
        super().__init__(texture=texture, scale=1.0)
        self.center_x = x
        self.center_y = y
        self.points = CLOUD_POINTS

        if texture:
            self.width = 64
            self.height = 64
        else:
            self.width = 60
            self.height = 45

        self.rotation_speed = random.uniform(-0.4, 0.4)

    def update(self):
        self.angle += self.rotation_speed

    def draw(self):
        if self.texture:
            super().draw()

            arcade.draw_circle_filled(
                self.center_x,
                self.center_y,
                self.width // 2,
                (0, 255, 0, 25)
            )
        else:
            arcade.draw_circle_filled(self.center_x, self.center_y, 22, COLOR_CLOUD)
            arcade.draw_text(
                "☢",
                self.center_x,
                self.center_y,
                arcade.color.DARK_GREEN,
                20,
                anchor_x="center",
                anchor_y="center"
            )


class Room:
    def __init__(self, layout, level_index, cloud_texture=None):
        self.layout = layout
        self.level_index = level_index
        self.tile_width = len(layout[0])
        self.tile_height = len(layout)
        self.pixel_width = self.tile_width * TILE_SIZE
        self.pixel_height = self.tile_height * TILE_SIZE
        self.cloud_texture = cloud_texture

        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.clouds = arcade.SpriteList(use_spatial_hash=False)

        self.has_trap = (level_index == FINAL_LEVEL_INDEX)
        if self.has_trap:
            self.trap_center_x = self.pixel_width // 2
            self.trap_center_y = self.pixel_height // 2
            self.trap_size = 70
        else:
            self.trap_center_x = None
            self.trap_center_y = None
            self.trap_size = 0

        self._build_walls()
        self._spawn_clouds()

    def _build_walls(self):
        for row_idx, row in enumerate(self.layout):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    x = col_idx * TILE_SIZE + TILE_SIZE // 2
                    y = (self.tile_height - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2
                    wall = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, COLOR_WALL)
                    wall.position = (x, y)
                    self.walls.append(wall)

    def _spawn_clouds(self):
        count = random.randint(10, 18)
        for _ in range(count):
            attempts = 0
            while attempts < 100:
                x = random.uniform(100, self.pixel_width - 100)
                y = random.uniform(100, self.pixel_height - 100)
                cloud = Cloud(x, y, self.cloud_texture)

                hit = any(
                    math.hypot(cloud.center_x - w.center_x, cloud.center_y - w.center_y) < TILE_SIZE * 0.9
                    for w in self.walls
                )
                if not hit:
                    self.clouds.append(cloud)
                    break
                attempts += 1

    def get_spawn_position(self):
        positions = []
        for row_idx, row in enumerate(self.layout):
            for col_idx, cell in enumerate(row):
                if cell == 0:
                    x = col_idx * TILE_SIZE + TILE_SIZE // 2
                    y = (self.tile_height - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2
                    if abs(x - self.pixel_width // 2) > 200 or abs(y - self.pixel_height // 2) > 200:
                        positions.append((x, y))

        if positions:
            return random.choice(positions)

        for row_idx, row in enumerate(self.layout):
            for col_idx, cell in enumerate(row):
                if cell == 0:
                    x = col_idx * TILE_SIZE + TILE_SIZE // 2
                    y = (self.tile_height - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2
                    return x, y

        return self.pixel_width // 2, self.pixel_height // 2

    def draw(self, player_score=0):
        # Рисуем пол
        for row_idx in range(self.tile_height):
            for col_idx in range(self.tile_width):
                if self.layout[row_idx][col_idx] == 0:
                    center_x = col_idx * TILE_SIZE + TILE_SIZE // 2
                    center_y = (self.tile_height - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2
                    floor_rect = arc_rect.XYWH(center_x, center_y, TILE_SIZE, TILE_SIZE)
                    arcade.draw_rect_filled(floor_rect, COLOR_FLOOR)

        self.walls.draw()
        self.clouds.draw()

        if self.has_trap:
            trap_color = COLOR_TRAP if player_score >= MIN_MONEY_FOR_TRAP else COLOR_TRAP_INACTIVE

            trap_rect = arc_rect.XYWH(
                self.trap_center_x,
                self.trap_center_y,
                self.trap_size,
                self.trap_size
            )
            arcade.draw_rect_filled(trap_rect, trap_color)

            text_color = arcade.color.WHITE if player_score >= MIN_MONEY_FOR_TRAP else arcade.color.GRAY
            arcade.draw_text(
                "T",
                self.trap_center_x,
                self.trap_center_y,
                text_color,
                28,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.ui_manager.enable()

        box = UIBoxLayout(vertical=True, space_between=25)

        btn_play = UIFlatButton(text="Играть", width=280, height=70)
        btn_play.on_click = self.on_play
        box.add(btn_play)

        btn_help = UIFlatButton(text="Справка", width=280, height=70)
        btn_help.on_click = self.on_help
        box.add(btn_help)

        btn_about = UIFlatButton(text="О проекте", width=280, height=70)
        btn_about.on_click = self.on_about
        box.add(btn_about)

        anchor = UIAnchorLayout()
        anchor.add(child=box, anchor_x="center_x", anchor_y="center_y")
        self.ui_manager.add(anchor)

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_play(self, event):
        self.window.show_view(GameView())

    def on_help(self, event):
        self.window.show_view(HelpView())

    def on_about(self, event):
        self.window.show_view(AboutView())

    def on_show_view(self):
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()


class HelpView(arcade.View):
    def on_draw(self):
        self.clear()
        arcade.draw_text("УПРАВЛЕНИЕ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
                         arcade.color.BLACK, 32, anchor_x="center")
        lines = [
            "WASD или стрелки — движение",
            "ЛКМ (удерживать) — включить пылесос (облака исчезают)",
            "Пылесос автоматически поворачивается к ближайшему облаку",
            f"Запуск пылесоса: {VACUUM_START_COST} валюты, затем {VACUUM_COST_PER_SECOND}/сек!",
            f"U (англ.) или Г (рус.) — улучшить пылесос (если ≥{VACUUM_UPGRADE_COST} валюты)",
            "",
            f"Начальный баланс: {INITIAL_MONEY} валюты",
            f"Облако: {CLOUD_POINTS} валюты",
            "ВНИМАНИЕ: На 5-м уровне есть красный квадрат с буквой 'T'",
            f"Квадрат можно активировать только при {MIN_MONEY_FOR_TRAP}+ валюты",
            "Подойдите к нему и нажмите T (англ.) или Е (рус.) для завершения игры",
            "При активации квадрата все деньги обнуляются",
            "",
            "СОВЕТ: Используйте пылесос экономно!",
            "Включайте его только когда рядом есть облака",
            "Улучшайте пылесос для большего радиуса действия",
            "Подойдите прямо к квадрату, почти касаясь его",
            "",
            "Собирай зелёные облака → получай валюту",
            "Цель — дойти до 5-го уровня и активировать реактор"
        ]
        y = SCREEN_HEIGHT - 180
        for line in lines:
            arcade.draw_text(line, SCREEN_WIDTH // 2, y, arcade.color.BLACK, 16, anchor_x="center")
            y -= 28
        arcade.draw_text("ESC — вернуться в меню", SCREEN_WIDTH // 2, 50,
                         COLOR_TEXT_DARK, 18, anchor_x="center")

    def on_key_press(self, symbol, _):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


class AboutView(arcade.View):
    def on_draw(self):
        self.clear()
        arcade.draw_text("О ПРОЕКТЕ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
                         arcade.color.BLACK, 32, anchor_x="center")
        text = (
            "Произошла утечка Цезия-137\n"
            "Ты — уборщик радиоактивных облаков.\n"
            "Защити свой мир от радиоктивной катастрофы\n\n"
            "Используй ресурсы мудро!\n"
            "Собирай радиоактивные остатки нейтрализатором, улучшай его и побеждай!\n"
            "Борись за своё существование\n"
            "Ты решаешь — выживет планета или нет...\n\n"
            "ПОСЛЕ...\n"
        )
        arcade.draw_text(text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                         arcade.color.BLACK, 20, anchor_x="center", anchor_y="center",
                         multiline=True, width=700, align="center")
        arcade.draw_text("ESC — назад", SCREEN_WIDTH // 2, 50,
                         COLOR_TEXT_DARK, 18, anchor_x="center")

    def on_key_press(self, symbol, _):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        # Загружаем текстуру облака
        self.cloud_texture = self.load_cloud_texture()

        self.player = Player()
        # Создаем комнаты с передачей текстуры
        self.rooms = [Room(layout, i, self.cloud_texture) for i, layout in enumerate(ROOM_LAYOUTS)]
        self.current_room_idx = 0
        self.current_room = self.rooms[self.current_room_idx]

        self.camera = Camera2D()

        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

        self.mouse_down = False
        self.game_won = False

        self.is_transitioning = False
        self.transition_timer = 0.0
        self.transition_progress = 0.0
        self.next_room_idx = None
        self.transition_message = ""

        spawn_x, spawn_y = self.current_room.get_spawn_position()
        self.player.center_x = spawn_x
        self.player.center_y = spawn_y

        self.update_camera()

    def load_cloud_texture(self):
        try:
            texture = arcade.load_texture("oblako.png")
            print("Текстура облака загружена: oblako.png")
            return texture
        except Exception as e:
            print(" Не найден oblako.png, используется векторное облако")
            return None

    def create_cloud_texture(self):
        # Создаем текстуру 64x64
        texture_size = 64
        texture = arcade.Texture.create_empty("cloud_texture", (texture_size, texture_size))

        # Создаем временную поверхность для рисования
        with arcade.get_window().ctx.default_atlas.render_into_texture(texture) as fbo:
            fbo.clear((0, 0, 0, 0))  # Прозрачный фон

            # Рисуем облако
            center_x = texture_size // 2
            center_y = texture_size // 2

            # Основное тело облака
            arcade.draw_circle_filled(center_x, center_y, 20, COLOR_CLOUD)
            arcade.draw_circle_filled(center_x - 15, center_y + 15, 15, COLOR_CLOUD)
            arcade.draw_circle_filled(center_x + 15, center_y + 15, 15, COLOR_CLOUD)
            arcade.draw_circle_filled(center_x - 25, center_y, 12, COLOR_CLOUD)
            arcade.draw_circle_filled(center_x + 25, center_y, 12, COLOR_CLOUD)

            # Символ радиации
            arcade.draw_text(
                "☢",
                center_x,
                center_y,
                arcade.color.DARK_GREEN,
                24,
                anchor_x="center",
                anchor_y="center"
            )

        print("Текстура облака создана программно")
        return texture

    def update_camera(self):
        self.camera.position = (self.player.center_x, self.player.center_y)

    def find_nearest_cloud(self):
        if not self.current_room.clouds:
            return None

        nearest_cloud = None
        min_distance = float('inf')

        for cloud in self.current_room.clouds:
            distance = math.hypot(
                cloud.center_x - self.player.center_x,
                cloud.center_y - self.player.center_y
            )
            if distance < min_distance:
                min_distance = distance
                nearest_cloud = cloud

        return nearest_cloud

    def start_transition(self, next_room_idx, message=""):
        if self.is_transitioning:
            return

        self.is_transitioning = True
        self.transition_timer = 0.0
        self.transition_progress = 0.0
        self.next_room_idx = next_room_idx
        self.transition_message = message

        self.player.score += 50

    def complete_transition(self):
        if self.next_room_idx is not None:
            self.current_room_idx = self.next_room_idx
            self.current_room = self.rooms[self.current_room_idx]

            spawn_x, spawn_y = self.current_room.get_spawn_position()
            self.player.center_x = spawn_x
            self.player.center_y = spawn_y

            self.update_camera()

        self.is_transitioning = False
        self.transition_timer = 0.0
        self.transition_progress = 0.0
        self.next_room_idx = None
        self.transition_message = ""

    def goto_level(self, level_index):
        if 0 <= level_index < len(self.rooms):
            self.current_room_idx = level_index
            self.current_room = self.rooms[self.current_room_idx]

            spawn_x, spawn_y = self.current_room.get_spawn_position()
            self.player.center_x = spawn_x
            self.player.center_y = spawn_y

            self.update_camera()

    def is_player_near_trap(self):
        if not self.current_room.has_trap:
            return False

        distance = math.hypot(
            self.player.center_x - self.current_room.trap_center_x,
            self.player.center_y - self.current_room.trap_center_y
        )

        activation_distance = 90
        return distance < activation_distance

    def can_activate_trap(self):
        return self.player.score >= MIN_MONEY_FOR_TRAP

    def reset_money(self):
        self.player.score = 0
        self.game_won = True

    def draw_transition_overlay(self):
        if not self.is_transitioning or self.transition_progress <= 0:
            return

        alpha = int(self.transition_progress * 255)
        if self.transition_progress > 0.5:
            alpha = int((1 - self.transition_progress) * 255 * 2)

        arcade.draw_rect_filled(
            arc_rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, alpha)
        )

        if 0.3 <= self.transition_progress <= 0.7 and self.transition_message:
            arcade.draw_text(
                self.transition_message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                40,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            self.current_room.draw(self.player.score)
            self.player.draw()

        arcade.draw_text(f"Валюта: {self.player.score}", 20, SCREEN_HEIGHT - 40,
                         arcade.color.BLACK, 22)
        arcade.draw_text(f"Уровень пылесоса: {self.player.upgrades}", 20, SCREEN_HEIGHT - 75,
                         COLOR_TEXT_DARK, 18)
        arcade.draw_text(f"Текущая комната: {self.current_room_idx + 1}/5", 20, SCREEN_HEIGHT - 110,
                         COLOR_TEXT_DARK, 18)

        if self.current_room_idx == FINAL_LEVEL_INDEX and not self.is_transitioning:
            if self.is_player_near_trap():
                if self.can_activate_trap():
                    arcade.draw_text("✓ РЯДОМ С КВАДРАТОМ! Нажмите T/Е",
                                     SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
                                     arcade.color.RED, 20, anchor_x="center")
                else:
                    arcade.draw_text(f"Нужно {MIN_MONEY_FOR_TRAP}+ валюты! Сейчас: {self.player.score}",
                                     SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
                                     arcade.color.DARK_RED, 18, anchor_x="center")
            else:
                arcade.draw_text("Подойдите к красному квадрату и нажмите T/Е",
                                 SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
                                 arcade.color.DARK_RED, 16, anchor_x="center")

            arcade.draw_text(f"Для активации нужно минимум {MIN_MONEY_FOR_TRAP} валюты",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT - 210,
                             arcade.color.DARK_RED, 14, anchor_x="center")

        self.draw_transition_overlay()

        if self.game_won:
            arcade.draw_rect_filled(
                arc_rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, 0, 0, 180)
            )

            arcade.draw_text(
                "ПОБЕДА!",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 80,
                arcade.color.RED,
                60,
                anchor_x="center"
            )
            arcade.draw_text(
                "Реактор нейтрализован",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 20,
                arcade.color.DARK_RED,
                32,
                anchor_x="center"
            )
            arcade.draw_text(
                f"Вы пожертвовали всеми ресурсами ради мира",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 40,
                arcade.color.WHITE,
                22,
                anchor_x="center"
            )
            arcade.draw_text(
                "ESC — выйти в меню",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 120,
                arcade.color.LIGHT_GRAY,
                18,
                anchor_x="center"
            )

    def on_update(self, delta_time):
        if self.game_won:
            return

        # Обновляем анимацию облаков
        self.current_room.clouds.update()

        if self.player.vacuum_on:
            self.player.pay_vacuum_cost(delta_time)

        if self.is_transitioning:
            self.transition_timer += delta_time
            self.transition_progress = min(self.transition_timer / TRANSITION_DURATION, 1.0)

            if self.transition_progress >= 1.0:
                self.complete_transition()

            return

        dx = dy = 0

        if self.key_up:
            dy += PLAYER_SPEED
        if self.key_down:
            dy -= PLAYER_SPEED
        if self.key_left:
            dx -= PLAYER_SPEED
        if self.key_right:
            dx += PLAYER_SPEED

        old_x = self.player.center_x
        old_y = self.player.center_y

        self.player.center_x += dx
        self.player.center_y += dy

        player_hit = arcade.SpriteSolidColor(self.player.width, self.player.height, arcade.color.TRANSPARENT_BLACK)
        player_hit.position = (self.player.center_x, self.player.center_y)
        if arcade.check_for_collision_with_list(player_hit, self.current_room.walls):
            self.player.center_x = old_x
            self.player.center_y = old_y

        if self.mouse_down and not self.player.vacuum_on and not self.is_transitioning:
            self.player.start_vacuum()

        if not self.mouse_down and self.player.vacuum_on:
            self.player.vacuum_on = False
            self.player.vacuum_active_time = 0.0
            self.player.last_payment_time = 0.0

        nearest_cloud = self.find_nearest_cloud()
        if nearest_cloud:
            self.player.update_vacuum_angle(nearest_cloud.center_x, nearest_cloud.center_y)

        if self.player.vacuum_on:
            to_remove = []
            for cloud in self.current_room.clouds:
                # Увеличили радиус сбора для текстуры
                dist = math.hypot(cloud.center_x - self.player.center_x, cloud.center_y - self.player.center_y)
                if dist < self.player.vacuum_range + 30:
                    self.player.score += cloud.points
                    to_remove.append(cloud)
            for cloud in to_remove:
                self.current_room.clouds.remove(cloud)

        if len(self.current_room.clouds) == 0 and self.current_room_idx != FINAL_LEVEL_INDEX and not self.is_transitioning:
            next_room_idx = self.current_room_idx + 1
            if next_room_idx < len(self.rooms):
                completed_level = self.current_room_idx + 1
                self.start_transition(next_room_idx, f"Этаж {completed_level} пройден!")

        self.update_camera()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F1:
            if not self.is_transitioning and self.current_room_idx != FINAL_LEVEL_INDEX:
                next_room_idx = self.current_room_idx + 1
                if next_room_idx < len(self.rooms):
                    completed_level = self.current_room_idx + 1
                    self.start_transition(next_room_idx, f"Этаж {completed_level} пройден!")
        elif symbol == arcade.key.F2:
            if not self.is_transitioning:
                self.goto_level(0)
        elif symbol == arcade.key.F3:
            if not self.is_transitioning:
                self.goto_level(1)
        elif symbol == arcade.key.F4:
            if not self.is_transitioning:
                self.goto_level(2)
        elif symbol == arcade.key.F5:
            if not self.is_transitioning:
                self.goto_level(3)
        elif symbol == arcade.key.F6:
            if not self.is_transitioning:
                self.goto_level(FINAL_LEVEL_INDEX)

        elif symbol == arcade.key.U or symbol == 1043:
            self.player.try_upgrade()

        elif symbol == arcade.key.T or symbol == 1059:
            if self.current_room_idx == FINAL_LEVEL_INDEX and self.is_player_near_trap() and not self.is_transitioning:
                if self.can_activate_trap():
                    self.reset_money()

        elif symbol == arcade.key.W or symbol == arcade.key.UP:
            self.key_up = True
        elif symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.key_down = True
        elif symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.key_left = True
        elif symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.key_right = True

        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.key_up = False
        elif symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.key_down = False
        elif symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.key_left = False
        elif symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.key_right = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.is_transitioning:
            self.mouse_down = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_down = False


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
        arcade.set_background_color(arcade.color.WHITE_SMOKE)
        self.show_view(MenuView())
        self.activate()


if __name__ == "__main__":
    game = MyGame()
    arcade.run()