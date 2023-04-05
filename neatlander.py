import gymnasium as gym
import neat

# Define the fitness function for the NEAT algorithm
def eval_genome(genome, config):
    env = gym.make('LunarLander-v2')
    observation = env.reset()
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitness = 0.0
    done = False
    while not done:
        action = net.activate(observation)
        observation, reward, done, info = env.step(action)
        fitness += reward
    env.close()
    return fitness

# Load the NEAT configuration file
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'neat_config.ini')

# Create the NEAT population
pop = neat.Population(config)

# Run the NEAT algorithm
winner = pop.run(eval_genome)

# Test the winning genome on the Lunar Lander environment
env = gym.make('LunarLander-v2')
observation = env.reset()
net = neat.nn.FeedForwardNetwork.create(winner, config)
done = False
while not done:
    action = net.activate(observation)
    observation, reward, done, info = env.step(action)
    env.render()
env.close()