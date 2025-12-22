import concurrent.futures
import math
import random
import os
import pickle
from agent import Agent
from network import NeuralNetwork

POPULATION_size = 100
GENERATION_TIME = 20.0 # seconds per generation
ELITISM = 0.2

class Population:
    def __init__(self, size=POPULATION_size):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.agents = [Agent(NeuralNetwork(4, 8, 1)) for _ in range(size)]
        self.generation = 1
        self.best_fitness = 0.0
        
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def update(self, dt):
        # Multithreaded Update
        # Chunking might be needed if update is too fast, but phyics is lightweight.
        # Python GIL might limit perf gains here, but for I/O or simply organizing valid parallel tasks it works.
        # Ideally, we batch update.
        
        # Simple parallel map
        # But update modifies state.
        
        futures = []
        chunk_size = 25
        for i in range(0, len(self.agents), chunk_size):
            chunk = self.agents[i : i + chunk_size]
            futures.append(self.executor.submit(self.update_chunk, chunk, dt))
            
        concurrent.futures.wait(futures)

    @staticmethod
    def update_chunk(agents, dt):
        for agent in agents:
            agent.update(dt)

    def is_generation_done(self, time_elapsed):
        # Done if time up OR all dead
        if time_elapsed >= GENERATION_TIME:
            return True
        
        # Check alive
        any_alive = False
        for a in self.agents:
            if a.alive:
                any_alive = True
                break
        return not any_alive

    def evolve(self):
        # Sort by fitness
        self.agents.sort(key=lambda a: a.fitness, reverse=True)
        self.best_fitness = self.agents[0].fitness
        
        print(f"Gen {self.generation} Best Fitness: {self.best_fitness:.2f}")
        
        # Save Best
        self.save_best(self.agents[0].network)
        
        # Selection
        cutoff = int(len(self.agents) * ELITISM)
        elites = self.agents[:cutoff]
        
        new_agents = []
        
        # Elitism (Keep best as is)
        for e in elites:
            new_agents.append(Agent(e.network.copy()))
            
        # Reproduction
        while len(new_agents) < len(self.agents):
            parent = random.choice(elites)
            child_net = parent.network.copy()
            child_net.mutate(rate=0.2, power=0.2)
            new_agents.append(Agent(child_net))
            
        self.agents = new_agents
        self.generation += 1

    def save_best(self, network):
        filename = os.path.join(self.output_dir, f"best_gen_{self.generation}.pkl")
        network.save(filename)
        
    def shutdown(self):
        self.executor.shutdown()
