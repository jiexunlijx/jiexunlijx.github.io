import pygame
import random
import neat
import os
import pickle

# Set up the screen
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480
BLOCK_SIZE = 20
GRID_SIZE = SCREEN_WIDTH // BLOCK_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()
pygame.display.set_caption("NEAT Snake")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.body = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = random.choice(["up", "down", "left", "right"])

    def move(self):
        x, y = self.body[0]

        if self.direction == "up":
            y -= 1
        elif self.direction == "down":
            y += 1
        elif self.direction == "left":
            x -= 1
        elif self.direction == "right":
            x += 1

        self.body.insert(0, (x, y))
        self.body.pop()

    def change_direction(self, direction):
        if direction == "up" and self.direction != "down":
            self.direction = "up"
        elif direction == "down" and self.direction != "up":
            self.direction = "down"
        elif direction == "left" and self.direction != "right":
            self.direction = "left"
        elif direction == "right" and self.direction != "left":
            self.direction = "right"

    def draw(self):
        for x, y in self.body:
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, GREEN, rect)

    def collide_with_food(self, food):
        return self.body[0] == food.position

    def collide_with_wall(self):
        x, y = self.body[0]
        return x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE

    def collide_with_self(self):
        return self.body[0] in self.body[1:]

class Food:
    def __init__(self):
        self.position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    def draw(self):
        rect = pygame.Rect(self.position[0] * BLOCK_SIZE, self.position[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, RED, rect)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        best = neat.Genome(-1, None, 1, 0)
        best.fitness = float('-inf')        
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        snake = Snake()
        food = Food()

        while True:
            # Get the snake's current state
            x, y = snake.body[0]
            left = (x - 1 < 0 or (x - 1, y) in snake.body)
            right = (x + 1 >= GRID_SIZE or (x + 1, y) in snake.body)
            up = (y - 1 < 0 or (x, y - 1) in snake.body)
            down = (y + 1 >= GRID_SIZE or (x, y + 1) in snake.body)

            # Get the network's output
            output = net.activate((left, right, up, down))

            # Decide on the direction to move
            direction = ["up", "right", "down", "left"][output.index(max(output))]
            snake.change_direction(direction)

            # Move the snake
            snake.move()

            # Check for collisions
            if snake.collide_with_wall() or snake.collide_with_self():
                break

            if snake.collide_with_food(food):
                genome.fitness += 1.0
                snake.body.append(snake.body[-1])
                food = Food()

            genome.fitness += 0.1

        # Remove the genome if it fails to survive
        genomes.remove((genome_id, genome))

def run(config_file):
    # Load the NEAT configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Create the population and add a reporter
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the simulation
    winner = population.run(eval_genomes, 100)

    # Save the winner's genome to a file
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    # Set up the configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    # Run the simulation
    run(config_path)
