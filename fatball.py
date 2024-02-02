import pygame
import random
import math
import sys
from csv import writer
from learner import Learner


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
    def __init__(self, width, height, init_value, x, y, limit, label):
        self.value = init_value
        self.label = label
        self.font = pygame.font.SysFont("Arial", 20)
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
                self.y + 25,
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
            self.y + 25,
            self.width,
            self.height,
        )
        color_rect = pygame.Surface((3, 2))
        pygame.draw.line(color_rect, color1, (0, 0), (0, 1))
        pygame.draw.line(color_rect, color2, (1, 0), (1, 1))
        pygame.draw.line(color_rect, color3, (2, 0), (2, 1))
        color_rect = pygame.transform.smoothscale(color_rect, (bar.width, bar.height))
        screen.blit(color_rect, bar)
        text = self.font.render(self.label, True, "white")
        screen.blit(text, (self.x, self.y))
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

    def do_every_second(self, callback):
        self.elapsed_time = self.elapsed_time + self.clock.tick() / 1000.0
        if self.seconds < int(self.elapsed_time):
            self.seconds = int(self.elapsed_time)
            return callback()
        return None

    def do_after_x_seconds(self, x, callback):
        self.elapsed_time = self.elapsed_time + self.clock.tick() / (x * 1000.0)
        if self.seconds < int(self.elapsed_time):
            self.seconds = int(self.elapsed_time)
            return callback()
        return None


class Turn:
    def __init__(self, screen):
        self.started = False
        self.screen = screen
        self.fatball = FatBall(screen.get_width() / 2, screen.get_height() / 2)
        self.thermometer = Meter(
            width=screen.get_width() - 20,
            height=20,
            init_value=5,
            x=10,
            y=10,
            limit=10,
            label="Temperature",
        )
        self.hungrometer = Meter(
            width=screen.get_width() - 20,
            height=20,
            init_value=10,
            x=10,
            y=60,
            limit=20,
            label="Energy",
        )
        self.font = pygame.font.SysFont("Arial", 25)
        self.instructions = [
            "Press S to play manually, M to let machine play",
            "Press E once to approach food",
        ]
        self.foods = Foods(screen)
        dists = self.foods.get_all_distances_to_food(
            self.fatball.pos, self.fatball.speed
        )
        self.foods.log = dists

        self.moving = False
        self.waiting = False
        self.died = False
        self.eaten = False
        self.food_i = -1
        self.tdps_stable = 0.3
        self.tips_moving = 0.4
        self.hips_stable = 0.2
        self.hips_moving = 0.4
        self.log = []
        self.score = 0

    def draw(self, screen):
        self.foods.draw(screen)
        self.fatball.draw(screen)
        self.thermometer.draw(screen, "blue", "darkgreen", "red")
        self.hungrometer.draw(screen, "red", "yellow", "darkgreen")

    def start(self):
        self.started = True

    def environment(self):
        starvation = False
        exhaustion = False
        hypothermia = False

        if not self.moving:
            min_t, _ = self.foods.get_min_time_to_food(
                self.fatball.pos, self.fatball.speed
            )
            starvation = self.hungrometer.decrease(self.hips_stable)
            hypothermia = self.thermometer.decrease(self.tdps_stable)
        else:
            starvation = self.hungrometer.decrease(self.hips_moving)
            exhaustion = self.thermometer.increase(self.tips_moving)
        if exhaustion or hypothermia:
            print("Dead because of temperature")
            self.died = True
            self.started = False
        if starvation:
            print("Dead because of hunger")
            self.died = True
            self.started = False

    
    def get_state(self):
        state = [0,0]
        if self.thermometer.value < 3:
            state[0] = -1
        elif self.thermometer.value > 7:
            state[0] = 1

        state[1] = math.floor(self.hungrometer.value)
        
        return state
    

    def move(self):
        if self.moving:
            if self.eaten:
                _, min_i = self.foods.get_min_time_to_food(
                    self.fatball.pos, self.fatball.speed
                )
                self.food_i = min_i
                self.eaten = False
            done = self.fatball.move(self.foods.foods[self.food_i])
            if done:
                self.foods.eat(self.food_i)
                self.hungrometer.increase(self.foods.value)
                self.eaten = True
                self.score += 1
                if not len(self.foods.foods):
                    self.foods = Foods(screen=self.screen)
    
    def stop_moving(self):
        self.moving = False

    def step(self, action):
        min_t, min_i = self.foods.get_min_time_to_food(
            self.fatball.pos, self.fatball.speed
        )

        self.eaten = False

        if action == "move" and not self.moving:
            self.moving = True
            self.food_i = min_i
        
        if action == "wait":
            self.waiting = True
        


class Game:
    def __init__(self):
        self.width, self.height = 1280, 720
        self.ball_radius = 20
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.ingame_clock = Clock()
        self.waiting_clock = Clock()
        self.game_count = 0
        self.font = pygame.font.SysFont("Arial", 25)
        self.last_score = 0

        self.turn = Turn(self.screen)

    def run(self):
        while True:
            learner.Reset()
            self.turn.start()
            self.game_count += 1
            print(f"Game count: {self.game_count}, Last score: {self.last_score}")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                self.screen.fill("black")

                self.ingame_clock.do_every_second(self.turn.environment)

                if self.turn.waiting:
                    done = self.waiting_clock.do_after_x_seconds(3, self.turn.get_state)
                    if done:
                        self.turn.waiting = False
                elif self.turn.moving:
                    self.turn.move()
                    self.waiting_clock.do_after_x_seconds(3, self.turn.stop_moving)
                else:
                    learner.UpdateQValues(self.turn.died)
                    if self.turn.died:
                        break
                    state = self.turn.get_state()
                    action_value = learner.act(state, self.game_count)
                    self.turn.step(action_value)

                self.turn.draw(self.screen)

                text = self.font.render(f"Game count: {self.game_count}, Last score: {self.last_score}", True, "white")
                text_rect = text.get_rect(
                    center=(self.screen.get_width() - 200, self.screen.get_height() - 50)
                )
                self.screen.blit(text, text_rect)

                pygame.display.update()
                self.clock.tick(60)
            self.last_score = self.turn.score
            self.turn = Turn(self.screen)
            if self.game_count % 50 == 0: # Save qvalues every 100 games
                print("Save Qvals")
                learner.SaveQvalues()
        
learner = Learner()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
