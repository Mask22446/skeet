import arcade
import math
import random
from abc import ABC
from abc import abstractmethod

#defining of global constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

ANGLE = 45

RIFLE_WIDTH = 100
RIFLE_HEIGHT = 20
RIFLE_COLOR = arcade.color.ANDROID_GREEN

BULLET_RADIUS = 3
BULLET_COLOR = arcade.color.BLACK_BEAN
BULLET_SPEED = 10

ULT_BULLET_RADIUS = 7
ULT_BULLET_COLOR = arcade.color.BLEU_DE_FRANCE
ULT_BULLET_SPEED = 5

TARGET_RADIUS = 20
TARGET_COLOR = arcade.color.YELLOW_ORANGE
TARGET_SAFE_COLOR = arcade.color.AIR_SUPERIORITY_BLUE
TARGET_SAFE_RADIUS = 15
TARGET_BONUS_RADIUS = 10
TARGET_BONUS_COLOR = arcade.color.YELLOW_ROSE

STANDART_POINT = 1
STRONG_POINT = 7
SAFE_POINT = -10
STRONG_LIVES = 3

class Point:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

class Velocity:
    def __init__(self):
        self.dx = 0.0
        self.dy = 0.0

class Rifle:
    def __init__(self):
        self.center = Point()

        self.center.x = 0.0
        self.center.y = 0.0

        self.angle = 45

    def draw(self):
        arcade.draw_rectangle_filled(self.center.x, self.center.y, RIFLE_WIDTH, RIFLE_HEIGHT, RIFLE_COLOR, self.angle)


class FlyBase(ABC):
    def __init__(self):
        self.center = Point()
        self.velocity = Velocity()
        self.radius = 0.0
        self.alive =True

    #asbstract base function
    @abstractmethod
    def draw(self):
        pass

    def advance(self):
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy

    def is_off_screen(self, screen_width, screen_height):
        #checking position
        if (self.center.x > screen_width or self.center.y > screen_height):
            return True
        else:
            return False        

class Bullet(FlyBase):
    def __init__(self):
        super().__init__()
        self.radius = BULLET_RADIUS
        self.color = BULLET_COLOR
        

    def draw(self):
        arcade.draw_circle_filled(self.center.x, self.center.y, self.radius, self.color)

    def fire(self, angle):
        self.velocity.dx = math.cos(math.radians(angle)) * BULLET_SPEED
        self.velocity.dy = math.sin(math.radians(angle)) * BULLET_SPEED

class Target(FlyBase, ABC):
    def __init__(self):
        super().__init__()
        self.center.y = random.uniform(SCREEN_HEIGHT/2, SCREEN_HEIGHT)
        self.velocity.dx = random.uniform(1,5)
        self.velocity.dy = random.uniform(-2,2)
        self.radius = TARGET_RADIUS
        self.color = TARGET_COLOR
        self.point = 0
        self.type = "unknown"
    @abstractmethod
    def draw(self):
        pass
    @abstractmethod
    def hit(self):
        pass

class StandardTarget(Target):
    def __init__(self):
        super().__init__()
        self.type = "Standard"
        self.point = STANDART_POINT

    def draw(self):
        arcade.draw_circle_filled(self.center.x, self.center.y, self.radius, self.color)
    
    def hit(self):
        self.alive = False
        return self.point


class SafeTarget(Target):
    def __init__(self):
        super().__init__()
        self.color = TARGET_SAFE_COLOR
        self.radius = TARGET_SAFE_RADIUS
        self.type = "Safe"
    
    def draw(self):
        arcade.draw_rectangle_filled(self.center.x, self.center.y, self.radius, self.radius, self.color)

    def hit(self):
        self.point = SAFE_POINT
        self.alive = False
        return self.point


class StrongTarget(Target):
    def __init__(self):
        super().__init__()
        self.velocity.dx = random.uniform(1,3)
        self.velocity.dy = random.uniform(-2,2)
        self.type = "Strong"
        self.point = STRONG_POINT
        self.lives = STRONG_LIVES

    def draw(self):
        arcade.draw_rectangle_filled(self.center.x, self.center.y, self.radius, self.radius, self.color)
    
    def hit(self):
        self.point = SAFE_POINT
        
        self.alive = False
        return self.point

class BonusTarget(Target):
    def __init__(self):
        super().__init__()
        self.velocity.dx = random.uniform(3,5)
        self.velocity.dy = random.uniform(-2,2)
        self.radius = TARGET_BONUS_RADIUS
        self.color = TARGET_BONUS_COLOR
        self.type = "Bonus"

    def draw(self):
        arcade.draw_circle_filled(self.center.x, self.center.y, self.radius, self.color)
        
    def hit(self, targets):
        self.alive = False
        for target in targets:
            self.point += target.point
            target.alive = False
        return self.point


class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.rifle = Rifle()
        self.score = 0
        
        self.bullets = []
        self.targets = []

        arcade.set_background_color(arcade.color.WHITE_SMOKE)

    def on_draw(self):
        arcade.start_render()

        self.rifle.draw()

        for bullet in self.bullets:
            bullet.draw()

        for target in self.targets:
            target.draw()

        self.draw_score()
        if self.score <= -30:
            self.draw_game_over()
            arcade.finish_render()

    def draw_score(self):
        score_text = "Score: {}".format(self.score)
        start_x = 10
        start_y = SCREEN_HEIGHT - 20
        arcade.draw_text(score_text, start_x=start_x, start_y=start_y, font_size=12, color=arcade.color.BLACK)

    def update(self, data_time):
        self.check_collisions()
        self.check_off_screen()

        if random.randint(1,50) == 1:
            self.create_target()

        for bullet in self.bullets:
            bullet.advance()

        for target in self.targets:
            target.advance()

    def create_target(self):
        if random.randint(1, 4) == 1:
            target = StandardTarget()
            self.targets.append(target)
        
        elif random.randint(1, 4) == 2:
            target = StrongTarget()
            self.targets.append(target)
        
        elif random.randint(1, 4) == 3:
            target = BonusTarget()
            self.targets.append(target)

        elif random.randint(1, 4) == 4:
            target = SafeTarget()
            self.targets.append(target)

    def check_collisions(self):
        for bullet in self.bullets:
            for target in self.targets:
                if bullet.alive and target.alive:
                    too_close=bullet.radius + target.radius

                    if (abs(bullet.center.x - target.center.x) < too_close and abs(bullet.center.y - target.center.y) < too_close):
                        if target.type == "Bonus":
                            bullet.alive = False
                            self.score += target.hit(self.targets)
                        else:
                            bullet.alive = False
                            self.score += target.hit()
                        

        self.cleanup_zombies()

    def cleanup_zombies(self):
        for bullet in self.bullets:
            if not bullet.alive:
                self.bullets.remove(bullet)
    def check_off_screen(self):
        for bullet in self.bullets:
            if bullet.is_off_screen(SCREEN_WIDTH, SCREEN_HEIGHT):
                self.bullets.remove(bullet)

        for target in self.targets:
            if target.is_off_screen(SCREEN_WIDTH, SCREEN_HEIGHT):
                self.targets.remove(target)

    def on_mouse_motion(self, x:float, y:float, dx:float, dy:float):
        self.rifle.angle = self._get_angle_degrees(x, y)
        return self.rifle.angle

    def on_mouse_press(self, x:float, y:float, button:int, modifiers:int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            angle =self._get_angle_degrees(x,y)
            bullet = Bullet()
            bullet.fire(angle)

            self.bullets.append(bullet)
        
        if button == arcade.MOUSE_BUTTON_RIGHT:
            angle = self._get_angle_degrees(x, y)

            bullet = Bullet()
            bullet.radius = ULT_BULLET_RADIUS
            bullet.color = ULT_BULLET_COLOR
            bullet.fire(angle)
            bullet.velocity.dx = math.cos(math.radians(angle)) * ULT_BULLET_SPEED
            bullet.velocity.dy = math.sin(math.radians(angle)) * ULT_BULLET_SPEED

        
            self.bullets.append(bullet)
    
    def _get_angle_degrees(self, x, y):
        angle_radians = math.atan2(y, x)

        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def draw_game_over(self):
        gameover = "GAME OVER"
        start_x = SCREEN_WIDTH / 2 - 50
        start_y = SCREEN_HEIGHT / 2
        arcade.draw_text(gameover,start_x=start_x, start_y=start_y,font_size=20,color=arcade.color.GIANTS_ORANGE)

window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()