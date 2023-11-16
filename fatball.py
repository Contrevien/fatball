import pygame
import random
import math
import sys
from csv import writer

###############
# Comment this section out to run
# without training model
################
import numpy as np
from sklearn.tree import DecisionTreeRegressor


data = np.loadtxt("./data.csv", delimiter=",")

train_features = data[:, :3]
train_targets = data[:, 3]

dtr = DecisionTreeRegressor(max_depth=5)

dtr.fit(train_features, train_targets)
## Section end

foods_data = np.loadtxt("./food.csv", delimiter=",")
train_features2 = foods_data[:, :5]
train_targets2 = foods_data[:, 5]

dtr2 = DecisionTreeRegressor(max_depth=5)
dtr2.fit(train_features2, train_targets2)


# General Utility
def generate_random_pixels(screen, padding_x, padding_y, num_pixels):
    pixels = set()

    while len(pixels) < num_pixels:
        x = random.randint(padding_x, screen.get_width() - padding_x)
        y = random.randint(padding_y, screen.get_height() - padding_y)

        # Check if the generated pixel position is not already in the set
        if (x, y) not in pixels:
            pixels.add((x, y))

    return list(pixels)


def write_log(filename, value):
    with open(filename, "a") as f:
        wo = writer(f)
        wo.writerow(value)
        f.close()


# Entities
class FatBall:
    def __init__(self, start_x, start_y):
        self.speed = 1.2
        self.pos = pygame.Vector2(start_x, start_y)
        self.font = pygame.font.SysFont("Arial", 25)
        self.radius = 40
        self.text = ""
        self.color = "white"

    def move(self, target):
        direction_vector = pygame.Vector2(
            target[0] - self.pos[0], target[1] - self.pos[1]
        )
        distance = direction_vector.length()

        if distance >= self.radius:
            normalized_vector = direction_vector.normalize()
            movement = normalized_vector * self.speed
            self.pos += movement
        else:
            return True

        return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        text = self.font.render(self.text, True, "white")
        text_rect = text.get_rect(center=(self.pos.x, self.pos.y + self.radius + 20))
        screen.blit(text, text_rect)


class Meter:
    def __init__(self, width, height, init_value, x, y, limit):
        self.value = init_value
        self.x, self.y = x, y
        self.height = height
        self.width = width
        self.limit = limit

    def needle(self, screen):
        pygame.draw.rect(
            screen,
            "white",
            (
                ((screen.get_width() / self.limit) * self.value) - 20,
                self.y,
                20,
                20,
            ),
        )

    def decrease(self, delta):
        self.value = self.value - delta
        if self.value <= 0:
            return True
        return False

    def increase(self, delta):
        self.value = self.value + delta
        if self.value > self.limit:
            return True
        return False

    def draw(self, screen, color1, color2, color3):
        bar = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height,
        )
        color_rect = pygame.Surface((3, 2))
        pygame.draw.line(color_rect, color1, (0, 0), (0, 1))
        pygame.draw.line(color_rect, color2, (1, 0), (1, 1))
        pygame.draw.line(color_rect, color3, (2, 0), (2, 1))
        color_rect = pygame.transform.smoothscale(color_rect, (bar.width, bar.height))
        screen.blit(color_rect, bar)

        self.needle(screen)


class Foods:
    def __init__(self, screen):
        self.foods = generate_random_pixels(screen, 20, 100, 5)
        self.radius = 3
        self.value = 3
        self.log = []

    def get_all_distances_to_food(self, locus, speed):
        values = []
        for food in self.foods:
            direction_vector = [food[0] - locus[0], food[1] - locus[1]]
            distance = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)
            values.append(int(math.ceil(distance / speed)))
        return values

    def get_min_time_to_food(self, locus, speed):
        values = self.get_all_distances_to_food(locus, speed)
        return min(values), values.index(min(values))

    def eat(self, i):
        self.foods.pop(i)

    def draw(self, screen):
        for food in self.foods:
            pygame.draw.circle(screen, "green", food, self.radius)


class Clock:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.seconds = 0
        self.elapsed_time = 0

    def run(self, callback):
        self.elapsed_time = self.elapsed_time + self.clock.tick() / 1000.0
        if self.seconds < int(self.elapsed_time):
            self.seconds = int(self.elapsed_time)
            callback()


class Turn:
    def __init__(self, screen):
        self.started = False
        self.machine = False
        self.fatball = FatBall(screen.get_width() / 2, screen.get_height() / 2)
        self.thermometer = Meter(
            width=screen.get_width() - 20, height=20, init_value=5, x=10, y=10, limit=10
        )
        self.hungrometer = Meter(
            width=screen.get_width() - 20,
            height=20,
            init_value=10,
            x=10,
            y=40,
            limit=10,
        )
        self.foods = Foods(screen)
        dists = self.foods.get_all_distances_to_food(
            self.fatball.pos, self.fatball.speed
        )
        self.foods.log = dists
        # Prediction for second model
        prediction = dtr2.predict([dists])
        print(f"{dists} - {1 if prediction[0] > 0 else 0}")
        if prediction[0] > 0:
            self.fatball.color = "white"
            self.fatball.text = "Eazy peezy!"
        else:
            self.fatball.color = "red"
            self.fatball.text = "This one's a loss"

        self.clock = Clock()
        self.food_i = -1
        self.tdps_stable = 0.6
        self.tips_moving = 0.4
        self.hips_stable = 0.5
        self.hips_moving = 0.7
        self.log = []

    def draw(self, screen):
        self.foods.draw(screen)
        self.fatball.draw(screen)
        self.thermometer.draw(screen, "blue", "darkgreen", "red")
        self.hungrometer.draw(screen, "red", "yellow", "darkgreen")

    def start(self, machine=False):
        self.started = True
        self.machine = machine

    def callback(self):
        starvation = False
        exhaustion = False
        hypothermia = False
        if self.food_i == -1:
            min_t, _ = self.foods.get_min_time_to_food(
                self.fatball.pos, self.fatball.speed
            )
            self.log.append([self.thermometer.value, self.hungrometer.value, min_t, 0])
            print(f"{self.thermometer.value},{self.hungrometer.value},{min_t},0")
            starvation = self.hungrometer.decrease(self.hips_stable)
            hypothermia = self.thermometer.decrease(self.tdps_stable)
        else:
            starvation = self.hungrometer.decrease(self.hips_moving)
            exhaustion = self.thermometer.increase(self.tips_moving)
        if exhaustion or hypothermia:
            print("Dead because of temperature")
            self.started = False
            self.foods.log.append(0)
            write_log("./food.csv", self.foods.log)
            self.foods.log = []
        if starvation:
            print("Dead because of hunger")
            self.started = False
            if len(self.foods.log):
                self.foods.log.append(0)
                write_log("./food.csv", self.foods.log)

    def run(self):
        self.clock.run(self.callback)
        keys = pygame.key.get_pressed()
        min_t, min_i = self.foods.get_min_time_to_food(
            self.fatball.pos, self.fatball.speed
        )

        should_move = keys[pygame.K_e]
        if self.machine:
            output = dtr.predict(
                [[self.thermometer.value, self.hungrometer.value, min_t]]
            )[0]
            should_move = output > 0

        # When not moving
        if should_move and self.food_i == -1:
            self.food_i = min_i
            self.log.append([self.thermometer.value, self.hungrometer.value, min_t, 1])
            print(f"{self.thermometer.value},{self.hungrometer.value},{min_t},1")

        # When in motion
        if self.food_i != -1:
            done = self.fatball.move(self.foods.foods[self.food_i])
            if done:
                self.foods.eat(self.food_i)
                self.hungrometer.increase(self.foods.value)
                self.food_i = -1
                if not len(self.foods.foods):
                    self.started = False
                    self.foods.log.append(1)
                    write_log("./food.csv", self.foods.log)
                    for log in self.log:
                        write_log("./test_data.csv", log)


class Game:
    def __init__(self):
        self.width, self.height = 1280, 720
        self.ball_radius = 20
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.turn = Turn(self.screen)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")

            self.turn.draw(self.screen)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_s] and not self.turn.started:
                self.turn = Turn(self.screen)
                self.turn.start()

            if keys[pygame.K_m]:
                self.turn = Turn(self.screen)
                self.turn.start(True)

            if self.turn.started:
                self.turn.run()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
