from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from pimoroni import Button
from machine import ADC, Pin
import random
import time

# Get display
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
WIDTH, HEIGHT = display.get_bounds()

# Get buttons
button_c = Button(9, invert=False)
button_a = Button(7, invert=False)

# Light sensor pin
sensor_power = Pin(27, Pin.OUT)
sensor_power.value(1)
light_sensor = ADC(Pin(26))

# Get Led 
led = Pin(25, Pin.OUT)

# Set Colours
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)
SKY = display.create_pen(135, 206, 235)
GRASS = display.create_pen(50, 205, 50)
YELLOW = display.create_pen(255, 220, 0)
ORANGE = display.create_pen(255, 140, 0)
DARK_GREEN = display.create_pen(30, 150, 50)
GREY = display.create_pen(100, 100, 100)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 100, 255)
PINK = display.create_pen(255, 100, 150)
BROWN = display.create_pen(139, 69, 19)
GRAY = display.create_pen(128, 128, 128)


# Ducky state enum
class DuckyState:
    STANDING = 1
    SLEEPING = 2
    SLEEPY = 3
    HUNGRY = 4
    STARVING = 5
    THIRSTY = 6
    PARCHED = 7


# States for the scene to add new
class SceneState:
    NORMAL = 1
    FOOD = 2
    WATER = 3
    EMPTY = 4


# Create Blobby
class Ducky:
    def __init__(self) -> None:
        self.energy = 100
        self.hunger = 0
        self.thirst = 0
        self.state = DuckyState.STANDING
        self.scene_state = SceneState.NORMAL
        self.water_display = 0

        self.food_display = 0
        self.disappointed = 0

    def update(self):
        if self.disappointed == 15:
            return
        else:
            led.value(0)

        if self.state == DuckyState.SLEEPING:
            self.energy += 4
            self.hunger += 1
            self.thirst += 1
        else:
            self.energy -= 1
            self.hunger += 2
            self.thirst += 2

        light_level = light_sensor.read_u16()

        self.energy = max(0, min(100, self.energy))
        self.hunger = max(0, min(100, self.hunger))
        self.thirst = max(0, min(100, self.thirst))

        if self.thirst >= 95:
            self.state = DuckyState.PARCHED
        elif self.hunger >= 95:
            self.state = DuckyState.STARVING
        elif light_level < 1500:
            self.state = DuckyState.SLEEPING
        elif light_level < 2500:
            self.state = DuckyState.SLEEPY
        elif self.energy <= 20:
            self.state = DuckyState.SLEEPING
        elif self.energy <= 45:
            self.state = DuckyState.SLEEPY
        elif self.hunger >= 75:
            self.state = DuckyState.HUNGRY
        elif self.thirst >= 75:
            self.state = DuckyState.THIRSTY
        else:
            self.state = DuckyState.STANDING

        if self.hunger >= 100 and self.thirst >= 100:
            self.disappointed += 1
            led.value(1)
            if self.disappointed == 15:
                self.scene_state = SceneState.EMPTY
        else:
            self.disappointed = max(0, self.disappointed - 1)

    def feed(self):
        if self.disappointed == 15:
            return

        self.food_display = 12
        self.scene_state = SceneState.FOOD

        self.hunger -= random.randint(2, 20)
        self.hunger = max(0, min(100, self.hunger))

        if self.hunger >= 95:
            self.state = DuckyState.STARVING
        elif self.hunger >= 75:
            self.state = DuckyState.HUNGRY
        else:
            self.state = DuckyState.STANDING

    def water(self):
        if self.disappointed == 15:
            return

        self.water_display = 12
        self.scene_state = SceneState.WATER

        self.thirst -= random.randint(2, 20)
        self.thirst = max(0, min(100, self.thirst))

        if self.thirst >= 95:
            self.state = DuckyState.PARCHED
        elif self.thirst >= 75:
            self.state = DuckyState.THIRSTY
        else:
            self.state = DuckyState.STANDING

    def draw(self):
        if self.state == DuckyState.STANDING:
            # Duck body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Duck head
            display.circle(120, 110, 20)

            # Beak
            display.set_pen(ORANGE)
            display.rectangle(113, 120, 15, 8)

            # Eyes
            display.set_pen(BLACK)
            display.circle(113, 105, 3)
            display.circle(127, 105, 3)

            # Feet on grass
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            display.set_pen(YELLOW)
            display.circle(98, 145, 10)

            display.set_pen(YELLOW)
            display.circle(142, 145, 10)
        elif self.state == DuckyState.SLEEPING:
            # Sleepy duck body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Sleepy duck head
            display.circle(120, 110, 20)

            # Beak
            display.set_pen(ORANGE)
            display.rectangle(113, 120, 15, 8)

            # Sleepy eyes (closed)
            display.set_pen(BLACK)
            display.line(108, 105, 116, 105, 2)
            display.line(124, 105, 132, 105, 2)

            # Eyelids for a sleepy look
            display.set_pen(YELLOW)
            display.rectangle(107, 102, 10, 4)
            display.rectangle(123, 102, 10, 4)

            # Feet on grass
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Wings
            display.set_pen(YELLOW)
            display.circle(98, 145, 10)
            display.circle(142, 145, 10)

            # Sleep "Zzz"
            display.set_pen(BLACK)
            display.text("Z", 145, 85, 3)
            display.text("z", 155, 75, 2)
            display.text("z", 163, 68, 1)
        elif self.state == DuckyState.SLEEPY:
            # Duck body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Duck head
            display.circle(120, 110, 20)

            # Beak
            display.set_pen(ORANGE)
            display.rectangle(113, 120, 15, 8)

            # Half-closed sleepy eyes
            display.set_pen(BLACK)
            display.circle(113, 105, 3)
            display.circle(127, 105, 3)

            # Droopy eyelids (cover top half of eyes)
            display.set_pen(YELLOW)
            display.rectangle(109, 102, 8, 3)
            display.rectangle(123, 102, 8, 3)

            # Feet on grass
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Wings
            display.set_pen(YELLOW)
            display.circle(98, 145, 10)
            display.circle(142, 145, 10)

            # Sleep "Zzz"
            display.set_pen(BLACK)
            display.text("Z", 145, 85, 3)
            display.text("z", 155, 75, 2)
            display.text("z", 163, 68, 1)
        elif self.state == DuckyState.HUNGRY:
            # Duck body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Duck head
            display.circle(120, 110, 20)

            # Hungry open beak
            display.set_pen(ORANGE)
            display.rectangle(113, 120, 15, 10)

            # Beak line
            display.set_pen(BLACK)
            display.line(113, 125, 128, 125)

            # Hungry eyes
            display.circle(113, 106, 3)
            display.circle(127, 106, 3)

            # Feet
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Wings
            display.set_pen(YELLOW)
            display.circle(98, 145, 10)
            display.circle(142, 145, 10)

            # Speech bubble
            display.set_pen(WHITE)
            display.rectangle(135, 65, 55, 25)

            # Bubble tail
            display.rectangle(140, 90, 8, 8)

            # Bubble outline
            display.set_pen(BLACK)
            display.rectangle(135, 65, 55, 1)  # top
            display.rectangle(135, 89, 55, 1)  # bottom
            display.rectangle(135, 65, 1, 25)  # left
            display.rectangle(189, 65, 1, 25)  # right

            # Text
            display.text("FOOD", 140, 72, 1)
        elif self.state == DuckyState.STARVING:
            # Very hungry duck body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Duck head
            display.circle(120, 110, 20)

            # Big open hungry beak
            display.set_pen(ORANGE)
            display.rectangle(110, 120, 20, 12)

            # Beak opening
            display.set_pen(BLACK)
            display.rectangle(110, 126, 20, 3)

            # Worried eyes
            display.circle(113, 104, 3)
            display.circle(127, 104, 3)

            # Eyebrows (worried look)
            display.line(109, 100, 116, 102, 1)
            display.line(124, 102, 131, 100, 1)

            # Feet
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Wings
            display.set_pen(YELLOW)
            display.circle(98, 145, 10)
            display.circle(142, 145, 10)

            # Big speech bubble
            display.set_pen(WHITE)
            display.rectangle(125, 55, 80, 30)

            # Bubble tail
            display.rectangle(135, 85, 10, 8)

            # Bubble outline
            display.set_pen(BLACK)
            display.rectangle(125, 55, 80, 1)
            display.rectangle(125, 84, 80, 1)
            display.rectangle(125, 55, 1, 30)
            display.rectangle(204, 55, 1, 30)

            # Text
            display.text("FOOD!!!", 132, 65, 1)
        elif self.state == DuckyState.THIRSTY:
            # Body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Head (slightly lower)
            display.circle(120, 115, 20)

            # Drooping wings
            display.circle(98, 150, 10)
            display.circle(142, 150, 10)

            # Open beak
            display.set_pen(ORANGE)
            display.rectangle(113, 125, 15, 3)
            display.rectangle(113, 130, 15, 3)

            # Droopy eyes
            display.set_pen(BLACK)
            display.rectangle(109, 110, 8, 1)
            display.rectangle(123, 110, 8, 1)

            # Tongue
            display.set_pen(PINK)
            display.rectangle(118, 131, 4, 2)

            # Feet
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Sweat drops
            display.set_pen(BLUE)
            display.circle(136, 108, 2)
            display.circle(141, 113, 3)
            display.circle(135, 118, 2)
        elif self.state == DuckyState.PARCHED:
            # Body
            display.set_pen(YELLOW)
            display.circle(120, 145, 25)

            # Head (lower, tired-looking)
            display.circle(120, 115, 20)

            # Droopy wings
            display.circle(98, 152, 10)
            display.circle(142, 152, 10)

            # Very open beak
            display.set_pen(ORANGE)
            display.rectangle(112, 123, 16, 5)
            display.rectangle(114, 130, 12, 5)

            # Sad tired eyes
            display.set_pen(BLACK)
            display.circle(113, 110, 3)
            display.circle(127, 110, 3)

            # Eyebrows (worried look)
            display.line(109, 105, 116, 107)
            display.line(124, 107, 131, 105)

            # Tongue hanging out
            display.set_pen(PINK)
            display.rectangle(117, 135, 6, 4)

            # Feet
            display.set_pen(ORANGE)
            display.rectangle(110, 170, 8, 5)
            display.rectangle(122, 170, 8, 5)

            # Big sweat drops
            display.set_pen(BLUE)
            display.circle(138, 102, 4)
            display.circle(144, 112, 3)
            display.circle(136, 120, 2)


def draw_scene():
    # Sky
    display.set_pen(SKY)
    display.clear()

    # Hills (behind the grass)
    display.set_pen(DARK_GREEN)
    display.circle(50, 210, 60)
    display.circle(150, 210, 80)
    display.circle(260, 210, 70)

    # Grass
    display.set_pen(GRASS)
    display.rectangle(0, 175, WIDTH, 75)

    # Clouds
    display.set_pen(WHITE)

    # Cloud 1
    display.circle(50, 50, 15)
    display.circle(70, 45, 20)
    display.circle(90, 50, 15)
    display.rectangle(50, 50, 40, 15)

    # Cloud 2
    display.circle(180, 80, 12)
    display.circle(200, 70, 18)
    display.circle(220, 80, 12)
    display.rectangle(180, 80, 40, 12)

    # Food tag
    display.set_pen(WHITE)
    display.rectangle(215, 210, 70, 25)

    display.set_pen(BLACK)
    display.text("FOOD", 228, 215, scale=2)

    # Water tag
    display.set_pen(WHITE)
    display.rectangle(32, 210, 70, 25)

    display.set_pen(BLACK)
    display.text("WATER", 41, 215, scale=2)


def draw_water_bowl():
    # Bowl outside
    display.set_pen(BROWN)
    display.rectangle(160, 168, 30, 10)

    # Bowl rim
    display.set_pen(GRAY)
    display.rectangle(158, 166, 34, 4)

    # Water inside
    display.set_pen(BLUE)
    display.rectangle(162, 167, 26, 5)

    # Water shine
    display.set_pen(WHITE)
    display.rectangle(168, 168, 5, 1)


def draw_food():
    # Seeds (small grain shapes)
    display.set_pen(YELLOW)

    display.rectangle(75, 185, 6, 3)
    display.rectangle(85, 190, 7, 3)
    display.rectangle(95, 183, 6, 3)
    display.rectangle(105, 188, 7, 3)
    display.rectangle(115, 182, 6, 3)
    display.rectangle(125, 190, 7, 3)
    display.rectangle(135, 185, 6, 3)
    display.rectangle(145, 189, 7, 3)

    # Darker seeds
    display.set_pen(ORANGE)

    display.rectangle(80, 193, 6, 3)
    display.rectangle(92, 187, 5, 3)
    display.rectangle(102, 194, 7, 3)
    display.rectangle(118, 188, 6, 3)
    display.rectangle(132, 193, 6, 3)
    display.rectangle(142, 183, 5, 3)

    # A few scattered seeds
    display.rectangle(70, 195, 5, 2)
    display.rectangle(152, 194, 5, 2)
    display.rectangle(110, 196, 5, 2)


def ducky_left():
    # Centre text box
    box_w = 160
    box_h = 60
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2

    # Box background
    display.set_pen(WHITE)
    display.rectangle(box_x, box_y, box_w, box_h)

    # Border
    display.set_pen(BLACK)
    display.rectangle(box_x, box_y, box_w, 2)
    display.rectangle(box_x, box_y + box_h - 2, box_w, 2)
    display.rectangle(box_x, box_y, 2, box_h)
    display.rectangle(box_x + box_w - 2, box_y, 2, box_h)

    # Text centred in box
    display.text("Ducky has", 115, 105, scale=2)
    display.text("left", 140, 125, scale=2)


def draw_stats(ducky):
    panel_x = 220
    panel_y = 5
    panel_w = 100
    panel_h = 85

    display.set_pen(WHITE)
    display.rectangle(panel_x, panel_y, panel_w, panel_h)
    display.set_pen(BLACK)

    display.text("NAME: DUCKY", 222, 10, scale=1)

    stats = [
        ("ENERGY", ducky.energy, GREEN),
        ("FOOD", 100 - ducky.hunger, RED),
        ("WATER", 100 - ducky.thirst, BLUE),
    ]

    y = 25

    for name, value, colour in stats:
        display.set_pen(BLACK)
        display.text(name, 222, y, scale=1)

        display.set_pen(GREY)
        display.rectangle(265, y + 2, 45, 6)

        width = int(value * 0.45)

        if value < 25:
            display.set_pen(RED)
        elif value < 50:

            display.set_pen(ORANGE)
        else:
            display.set_pen(colour)

        display.rectangle(265, y + 2, width, 6)

        y += 18

    display.set_pen(BLACK)

    moods = {
        DuckyState.STANDING: "HAPPY",
        DuckyState.SLEEPING: "SLEEP",
        DuckyState.SLEEPY: "TIRED",
        DuckyState.HUNGRY: "FOOD!",
        DuckyState.STARVING: "STARVE!",
        DuckyState.THIRSTY: "WATER!",
        DuckyState.PARCHED: "DRY!",
    }

    display.text("MOOD: " + moods[ducky.state], 222, 77, scale=1)


ducky = Ducky()

last_main = time.ticks_ms()
last_buttons = time.ticks_ms()
last_display = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # Runs every 100ms
    if time.ticks_diff(now, last_buttons) >= 100:
        last_buttons = now
        if button_c.is_pressed:
            ducky.feed()

        if button_a.is_pressed:
            ducky.water()

    # Run every 250ms
    if time.ticks_diff(now, last_display) >= 250:
        last_display = now
        display.clear()

        draw_scene()

        if ducky.scene_state == SceneState.FOOD:
            draw_food()
            ducky.food_display -= 1
            if ducky.food_display == 0:
                ducky.scene_state = SceneState.NORMAL
        elif ducky.scene_state == SceneState.WATER:
            draw_water_bowl()
            ducky.water_display -= 1
            if ducky.water_display == 0:
                ducky.scene_state = SceneState.NORMAL

        if ducky.scene_state != SceneState.EMPTY:
            draw_stats(ducky)

            ducky.draw()
        else:
            ducky_left()

        display.update()

    # Runs every 1000ms
    if time.ticks_diff(now, last_main) >= 1000:
        last_main = now
        ducky.update()

    time.sleep_ms(1)
