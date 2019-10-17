import asyncio
import curses
import itertools
import random
import time

from curses_tools import draw_frame, get_frame_size, read_controls


def read_frame(path):
    with open(path, 'r') as frame_file:
        frame = frame_file.read()
        return frame


async def blink(canvas, row, column, symbol):
    while True:
        for _ in range(random.randint(1, 30)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, frames):
    frame_rows, frame_columns = get_frame_size(frames[0])
    canvas_size_y, canvas_size_x = canvas.getmaxyx()

    for frame in itertools.cycle(frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if (0 < row + rows_direction < canvas_size_y - frame_rows):
            row += rows_direction
        if (0 < column + columns_direction < canvas_size_x - frame_columns):
            column += columns_direction

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas):
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)

    canvas_size_y, canvas_size_x = canvas.getmaxyx()

    frames = (read_frame('rocket_frames/rocket_frame_1.txt'), read_frame('rocket_frames/rocket_frame_2.txt'))
    coroutines = []

    stars_count = 100

    for _ in range(stars_count):
        coroutines.append(blink(
            canvas,
            random.randint(2, canvas_size_y - 2),
            random.randint(2, canvas_size_x - 2),
            symbol=random.choice('+*.:'),
        ))

    gun_shot = fire(canvas, canvas_size_y//2-1, canvas_size_x//2+2)
    coroutines.append(gun_shot)

    spaceship = animate_spaceship(canvas, canvas_size_y//2, canvas_size_x//2, frames)
    coroutines.append(spaceship)

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                break
            except RuntimeError:
                pass
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
