import time
import jpegdec

from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_TUFTY_2040

with open("high_score.txt") as f:
    h_score = int(f.readline().strip())

    print(type(h_score))


# --------------------------------
# Display setup
# --------------------------------

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
display.set_backlight(1.0)
display.set_font("bitmap8")

WIDTH, HEIGHT = display.get_bounds()


# --------------------------------
# Button setup
# --------------------------------

button_a = Button(7, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)


# --------------------------------
# JPEG decoder
# --------------------------------

runner_image = jpegdec.JPEG(display)


# --------------------------------
# Colours
# --------------------------------

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
GREEN = display.create_pen(0, 180, 80)
RED = display.create_pen(255, 70, 70)
SKY_BLUE = display.create_pen(135, 206, 235)


# --------------------------------
# World settings
# --------------------------------

GROUND_Y = 195


# --------------------------------
# Player settings
# --------------------------------

player_x = 40

# Change these to match the dimensions
# of each Run0.jpg–Run9.jpg image.
player_width = 40
player_height = 40

player_y = GROUND_Y - player_height

velocity_y = 0
gravity = 1
jump_power = -13


# --------------------------------
# Animation settings
# --------------------------------

frame_number = 0


# Change frame every 100 milliseconds.
animation_delay = 100
last_animation_time = time.ticks_ms()


# --------------------------------
# Obstacle settings
# --------------------------------

obstacle_width = 18
obstacle_height = 25

obstacle_x = WIDTH
obstacle_y = GROUND_Y - obstacle_height
obstacle_speed = 4


# --------------------------------
# Game state
# --------------------------------

score = 0
game_over = False
previous_a_pressed = False

characters = [
    {"name": "MAN", "folder": "run_frames/man", "frame_count": 10},
    {"name": "WIZARD", "folder": "run_frames/wizard", "frame_count": 8},
]

selected_character = 0
character_folder = characters[selected_character]["folder"]
character_frame_count = characters[selected_character]["frame_count"]


def character_select():
    global selected_character
    global character_folder
    global character_frame_count

    previous_a_pressed = False
    previous_up_pressed = False
    previous_down_pressed = False

    while True:
        a_pressed = button_a.is_pressed
        up_pressed = button_up.is_pressed
        down_pressed = button_down.is_pressed

        a_just_pressed = a_pressed and not previous_a_pressed
        up_just_pressed = up_pressed and not previous_up_pressed
        down_just_pressed = down_pressed and not previous_down_pressed

        previous_a_pressed = a_pressed
        previous_up_pressed = up_pressed
        previous_down_pressed = down_pressed

        if up_just_pressed:
            selected_character -= 1

            if selected_character < 0:
                selected_character = len(characters) - 1

        if down_just_pressed:
            selected_character += 1

            if selected_character >= len(characters):
                selected_character = 0

        character = characters[selected_character]

        display.set_pen(BLACK)
        display.clear()

        display.set_pen(WHITE)

        display.text(
            "SELECT CHARACTER",
            38,
            45,
            WIDTH,
            3,
        )

        display.text(
            "< {} >".format(character["name"]),
            95,
            105,
            WIDTH,
            2,
        )

        display.text(
            "UP / DOWN",
            105,
            155,
            WIDTH,
            2,
        )

        display.text(
            "A TO START",
            100,
            200,
            WIDTH,
            2,
        )

        display.update()

        if a_just_pressed:
            character_folder = character["folder"]
            character_frame_count = character["frame_count"]
            return


def player_is_on_ground():
    return player_y >= GROUND_Y - player_height


def collision():
    return (
        player_x < obstacle_x + obstacle_width
        and player_x + player_width > obstacle_x
        and player_y < obstacle_y + obstacle_height
        and player_y + player_height > obstacle_y
    )


def reset_game():
    global player_y
    global velocity_y
    global obstacle_x
    global score
    global game_over
    global frame_number
    global last_animation_time
    global obstacle_speed
    global h_score

    player_y = GROUND_Y - player_height
    velocity_y = 0

    obstacle_x = WIDTH
    if score > h_score:
        h_score = score

    score = 0
    obstacle_speed = 4
    game_over = False

    frame_number = 0
    last_animation_time = time.ticks_ms()


def update_animation():
    global frame_number
    global last_animation_time

    now = time.ticks_ms()

    if time.ticks_diff(now, last_animation_time) >= animation_delay:
        frame_number = (frame_number + 1) % character_frame_count
        last_animation_time = now


def draw_player():
    filename = "{}/Run{}.jpg".format(
        character_folder,
        frame_number,
    )

    runner_image.open_file(filename)

    runner_image.decode(
        player_x,
        int(player_y) - 30,
        jpegdec.JPEG_SCALE_FULL,
    )


character_select()
reset_game()


last_draw = time.ticks_ms()
previous_a_pressed = False

while True:
    now = time.ticks_ms()

    # -------------------------------
    # Read input every loop
    # -------------------------------
    a_pressed = button_a.is_pressed
    a_just_pressed = a_pressed and not previous_a_pressed
    previous_a_pressed = a_pressed

    # -------------------------------
    # Game update
    # -------------------------------
    if game_over:
        if a_just_pressed:
            reset_game()

    else:
        # Jump.
        if a_just_pressed and player_is_on_ground():
            velocity_y = jump_power

        # Gravity.
        velocity_y += gravity
        player_y += velocity_y

        ground_player_y = GROUND_Y - player_height

        if player_y >= ground_player_y:
            player_y = ground_player_y
            velocity_y = 0

        # Animate only while on ground.
        if player_is_on_ground():
            update_animation()
        else:
            frame_number = 0

        # Move obstacle.
        obstacle_x -= obstacle_speed

        if obstacle_x < -obstacle_width:
            obstacle_x = WIDTH * 1.15
            score += 1
            obstacle_speed *= 1.05

        if collision():
            game_over = True

    # -------------------------------
    # Draw at ~30 FPS
    # -------------------------------
    if time.ticks_diff(now, last_draw) >= 33:

        last_draw = now

        display.set_pen(SKY_BLUE)
        display.clear()

        # Ground
        display.set_pen(GREEN)
        display.rectangle(
            0,
            GROUND_Y,
            WIDTH,
            HEIGHT - GROUND_Y,
        )

        # Player
        draw_player()

        # Obstacle
        display.set_pen(RED)
        display.rectangle(
            int(obstacle_x),
            obstacle_y,
            obstacle_width,
            obstacle_height,
        )

        # Score
        display.set_pen(WHITE)
        display.text(
            "SCORE: {}".format(score),
            8,
            8,
            WIDTH,
            2,
        )

        high_score_text = "HIGH SCORE: {}".format(h_score)
        high_score_width = display.measure_text(
            high_score_text,
            2,
        )

        display.text(
            high_score_text,
            WIDTH - high_score_width - 8,
            8,
            high_score_width,
            2,
        )

        if game_over:
            display.set_pen(BLACK)
            display.rectangle(45, 60, 230, 110)

            if score > h_score:
                with open("high_score.txt", "w") as f:
                    f.write(str(score))

            display.set_pen(WHITE)
            display.text(
                "GAME OVER",
                83,
                75,
                180,
                3,
            )

            if score > h_score:
                display.text(
                    "NEW HIGH SCORE!",
                    70,
                    115,
                    200,
                    2,
                )

            else:
                display.text(
                    "SCORE: {}".format(score),
                    105,
                    115,
                    140,
                    2,
                )

            display.text(
                "PRESS A",
                115,
                145,
                120,
                2,
            )

        display.update()
