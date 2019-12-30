from machine import Pin, I2C
import ssd1306
from time import sleep
import math
import random

class Joshua:
    """
    Provides basic functions like tic tac toe
    grid and the symbols
    """

    def __init__(self):
        self.oled = self.init_display()

    def init_display(self):
        """
        Initialize the display with the correct rotation
        """
        i2c = I2C(-1, scl=Pin(22), sda=Pin(21))
        oled = ssd1306.SSD1306_I2C(width=128, height=64, i2c=i2c)
        oled.rotate(0)
        return oled

    def refresh(self):
        """
        Draw changes to LCD
        """
        self.oled.show()

    def draw_grid(self):
        """
        Draw a tic tac toe grid
        """
        self.oled.fill(0)
        for hline in (int(round(self.oled.height / 3)), int(round(self.oled.height / 3 * 2))):
            self.oled.framebuf.hline(0, hline, 128, 1)

        for vline in (int(round(self.oled.width / 3)), int(round(self.oled.width / 3 * 2))):
            self.oled.framebuf.vline(vline, 0, 64, 1)

    def draw_circle(self, x, y, padding=2):
        """
        Draw a circle to a tic tac toe field
        """
        # cell size
        cell_width = int(round(self.oled.width / 3))
        cell_height = int(round(self.oled.height / 3))

        # offset
        offseth = x * cell_width + x
        offsetv = y * cell_height + y

        # center point and radius length
        centerx = offseth + int(round(cell_width/2))
        centery = offsetv + int(round(cell_height/2))
        radius = ((cell_width if cell_width < cell_height else cell_height) / 2) - (2 * padding)

        # draw
        self.oled.circle(centerx, centery, 8)

    def draw_x(self, x, y, padding=5):
        """
        Draw an X to a tic tac toe field
        """
        # cell size
        cell_width = int(round(self.oled.width / 3))
        cell_height = int(round(self.oled.height / 3))

        # center in cell
        centerV = False
        line_width = -1

        if cell_height < cell_width:
            line_width = cell_height
            centerV = False
        else:
            line_width = cell_width
            centerV = True

        diff = (cell_height if cell_height > cell_width else cell_width) - line_width
        width_diff = int(round(diff / 2))

        # offset
        offseth = x * cell_width
        offsetv = y * cell_height

        # add diff to offset to center in cell
        if centerV:
            offsetv += width_diff
        else:
            offseth += width_diff

        # start/end points for the lines
        tl = (offseth + padding, offsetv + padding)
        br = (offseth + line_width - padding, offsetv + line_width - padding)
        bl = (offseth + padding, offsetv + line_width - padding)
        tr = (offseth + line_width - padding, offsetv + padding)

        # from up-left to down-right
        self.oled.framebuf.line(tl[0], tl[1], br[0], br[1], 1)
        # from down-left to up-right
        self.oled.framebuf.line(bl[0], bl[1], tr[0], tr[1], 1)

class JoshuaMove:
    """
    Represents a move on the tic tac toe grid
    """
    def __init__(self, x, y, circle=False):
        self.x = x
        self.y = y
        self.circle = circle

    def clone(self):
        return JoshuaMove(self.x, self.y, self.circle)

class JoshuaAnimation:
    """
    Tic Tac Toe animation
    """
    def __init__(self):
        self.josh = Joshua()
        self.move_speed = 0.5
        self.moves = (
            JoshuaMove(1, 1, True),
            JoshuaMove(0, 0, False),
            JoshuaMove(0, 1, True),
            JoshuaMove(2, 1, False),
            JoshuaMove(1, 0, True),
            JoshuaMove(1, 2, False),
            JoshuaMove(2, 0, True),
            JoshuaMove(0, 2, False),
            JoshuaMove(2, 2, True),
        )

    def clone_moves(self):
        """
        Clone all moves to process them in
        the flip functions
        """
        for move in self.moves:
            yield move.clone()

    def flip_nothing(self, moves):
        """
        Use the original moves
        """
        return moves

    def flip_symbol(self, moves):
        """
        Flip X and Circle symbol
        """
        for move in moves:
            move.circle = not move.circle
            yield move

    def flip_horizontal(self, moves):
        """
        Flip moves horizontally
        """
        for move in moves:
            if move.x != 1:
                move.x = 0 if move.x == 2 else 2
            yield move

    def flip_vertical(self, moves):
        """
        Flip moves vertically
        """
        for move in moves:
            if move.y != 1:
                move.y = 0 if move.y == 2 else 2
            yield move

    def flip_verhor(self, moves):
        """
        Flip moves vertically and horizontally
        """
        return self.flip_horizontal(self.flip_vertical(moves))

    def random_flip(self):
        """
        Return a random flip function
        """
        funcs = [
            self.flip_nothing,
            self.flip_horizontal,
            self.flip_vertical,
            self.flip_verhor
        ]

        i = random.randrange(0, len(funcs))
        print(str(i))
        return (funcs[i])

    def speed_generator(self):
        """
        Generate move speed
        """
        for speed_percent in (100, 75, 25):
           yield speed_percent

        for i in range(0, 11, 1):
            yield 0

    def grid(self):
        """
        Draw the grid
        """
        self.josh.draw_grid()
        self.josh.refresh()

    def move(self, x, y, circle=True, speed=0.4):
        """
        Simulates a tic tac toe move
        """
        sleep(speed)
        if circle:
            self.josh.draw_circle(x, y)
        else:
            self.josh.draw_x(x, y)

        self.josh.refresh()

    def run(self):
        """
        Start the animation
        """
        # one game per speed from generator
        i = random.randrange(0, 2)
        for speed_percent in self.speed_generator():
            speed = self.move_speed / 100 * speed_percent
            print('Current speed: '+str(speed))

            # draw grid
            self.grid()

            if speed > 0:
                sleep(1)

            # flip moves for pseudo entropy
            flipfunc = self.random_flip()
            moves = flipfunc(self.clone_moves())

            # flip starter symbol
            if i % 2 == 0:
                moves = self.flip_symbol(moves)

            # draw moves
            for move in moves:
                self.move(move.x, move.y, move.circle, speed)

            # draw stalemate screen
            if speed > 0:
                sleep(0.4)
                self.josh.oled.fill(1)
                self.josh.oled.text('STALEMATE.', 25, 25, 0)
                self.josh.refresh()
                sleep(1)

            i += 1

        # tilt screen
        self.josh.oled.fill(1)
        self.josh.refresh()
        sleep(2)

        # end title
        self.josh.oled.fill(0)
        self.josh.refresh()
        sleep(1)
        self.josh.oled.text('A STRANGE GAME.', 0, 10)
        self.josh.refresh()
        sleep(1)
        self.josh.oled.text('THE ONLY WINNING', 0, 20)
        self.josh.refresh()
        sleep(0.3)
        self.josh.oled.text('MOVE IS NOT TO', 0, 30)
        self.josh.refresh()
        sleep(0.3)
        self.josh.oled.text('PLAY.', 0, 40)
        self.josh.refresh()
        sleep(5)

def main():
    jo = JoshuaAnimation()
    jo.run()

if __name__ == "__main__":
    main()
