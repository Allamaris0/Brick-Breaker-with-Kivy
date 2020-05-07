from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, BooleanProperty, DictProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.config import Config

import sys

LabelBase.register('PermanentMarker-Regular',
                   'fonts/PermanentMarker-Regular.ttf')

class RoundedButton(Button):
    pass

# Classes for moving objects
class PongPaddle(Widget):
    score = NumericProperty(0)
    can_bounce = BooleanProperty(False)

    def bounce_ball(self, ball, start):
        if self.can_bounce:
            vx, vy = ball.velocity

            #Top of the paddle
            if (self.x <= ball.x <= self.x + self.width) and 0 <ball.y <= self.height:
                vel = Vector(vx, -1 * vy)
                self.can_bounce = False

                if start==2:
                    #With serve_ball
                    offset = (ball.center_y - self.center_y) / self.height
                    ball.velocity = vel.x, vel.y + offset
                    start += 1
                elif start > 2:
                    ball.velocity = vel.x, vel.y

            #Edges of the paddle
            if (self.center_y < ball.y<= self.height) and (ball.x <= self.right or ball.right >= self.x):
                vel = Vector(-1*vx, vy)
                self.can_bounce = False


        elif not self.collide_widget(ball) and not self.can_bounce and start:
            self.can_bounce = True

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos  # The Vector represents a 2D vector (x, y)


# Klasy ekranów
class MenuWindow(Screen):

    def newgameBtn(self):
        sm.current = "game"

    def scoreBtn(self):
        sm.current = "scores"

    def aboutBtn(self):
        sm.current = "author"

    def keymapBtn(self):
        sm.current = "keys"


class ScoresWindow(Screen):
    pass

class AboutAuthor(Screen):
    pass

class KeyMappingWindow(Screen):
    pass

# Ekran gry
class BrickGame(Screen):
    #Variables for widgets
    layout = ObjectProperty(None)
    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    enter_label = ObjectProperty(None)
    ball_life = ObjectProperty(None)

    dict_bricks = DictProperty()
    start = NumericProperty(0)
    lives = NumericProperty(99)

    def __init__(self, **kwargs):
        super(BrickGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def create_bricks(self):
        # Creating bricks
        columns = 16
        rows = 5
        brick_size = (40, 20)
        start_pos = (self.layout.width / 10, self.layout.height / 2)

        for c in range(columns):
            for r in range(rows):
                with self.layout.canvas:
                    Color(1, 0, 0, group=f'rect {c}{r}')
                    Line(rectangle=[start_pos[0] + brick_size[0] * c, start_pos[1] + brick_size[1] * r,
                                    brick_size[0], brick_size[1]],
                         width=1,
                         group=f'rect {c}{r}')
                    Color(0.5, 0.1, 0, group=f'rect {c}{r}')
                    Rectangle(pos=(start_pos[0] + brick_size[0] * c, start_pos[1] + brick_size[1] * r),
                              size=(brick_size[0], brick_size[1]),
                              group=f'rect {c}{r}')
                self.dict_bricks[(start_pos[0] + brick_size[0] * c, start_pos[1] + brick_size[1] * r,
                                 brick_size[0], brick_size[1])] = f'rect {c}{r}'


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[0] == 275:  # Right arrow
            if self.player.x + self.player.width <= self.layout.width:
                self.player.pos = (self.player.pos[0] + self.player.width * 0.2, self.player.pos[1])
                if self.start <2:
                    self.ball.center_x = self.player.center_x
                    self.ball.y = self.player.height

        elif keycode[0] == 276:  # Left arrow
            if self.player.x >= 0:
                self.player.pos = (self.player.pos[0] - self.player.width * 0.2, self.player.pos[1])
                if self.start < 2:
                    self.ball.center_x = self.player.center_x
                    self.ball.y = self.player.height

        elif keycode[0] == 13 and self.start<2 and sm.current == "game": # the key no. 13 is 'Enter'
            self.start += 1
            if self.start == 1:
                self.enter_label.text = ""
                self.create_bricks()

            if self.start == 2:
                self.serve_ball()
                self.player.can_bounce = True

        elif keycode[1] == 'escape': # Esc
            sys.exit()

        # Return True to accept the key. Otherwise, it will be used by the system.
        return True

    def serve_ball(self, vel=(4, 0)):
        self.ball.center[0] = self.player.center_x
        self.ball.pos[1] = self.player.height
        self.ball.velocity = vel


    def update(self, dt):
        if self.start > 1:
            self.ball.move()

        # bounce ball off a paddle
        self.player.bounce_ball(self.ball, self.start)

        if len(self.dict_bricks) > 0:
            self.remove_brick(self.ball, self.dict_bricks)

        # bounce ball off top
        if self.ball.top >= self.height:
            self.ball.velocity_y *= -1

        # bounce off left and right
        if (self.ball.x <= 0) or (self.ball.right >= self.width):
            self.ball.velocity_x *= -1

        # loss of ball lives
        if self.ball.y <= 0 or (self.ball.x <= 0 and self.ball.y <= 0):
            self.player.score -= 1
            self.lives -= 1
            self.ball.center[0] = self.player.center_x
            self.ball.pos[1] = self.player.height
            self.start = 1
            self.ball_life.text = f'[ref=BREAK BRICKS][color=eb5e28]{self.lives}[/color][/ref]'

    def remove_brick(self, ball, dict_bricks):
        dict_bricks = {**dict_bricks}

        for pos, rect in dict_bricks.items():
            if (pos[0] <= ball.x < pos[0] + pos[2] and pos[1] <= ball.y <= pos[1] + pos[3]):
                self.layout.canvas.remove_group(rect)
                del self.dict_bricks[pos]
                vx, vy = ball.velocity
                vel = Vector(vx, -1*vy)
                ball.velocity = vel.x, vel.y
            elif (pos[0] <= ball.right < pos[0] + pos[2] and pos[1] <= ball.top <= pos[1] + pos[3]):
                self.layout.canvas.remove_group(rect)
                del self.dict_bricks[pos]
                vx, vy = ball.velocity
                vel = Vector(-1 * vx, vy)
                ball.velocity = vel.x, vel.y


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("brickgameapp.kv")
sm = WindowManager()
screens = [MenuWindow(name="menu"), BrickGame(name="game"), ScoresWindow(name="scores"), KeyMappingWindow(name="keys"),
           AboutAuthor(name="author")]
for screen in screens:
    sm.add_widget(screen)
sm.current = "menu"

class BrickGameApp(App):

    def build(self):
        return sm


if __name__ == "__main__":
    BrickGameApp().run()
