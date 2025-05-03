import numpy as np
import random
import matplotlib.pyplot as plt

random.seed()

Nd = 9  # Number of digits (in the case of standard Sudoku puzzles, this is 9).

class Population(object):
    """ A set of candidate solutions to the Sudoku puzzle. These candidates are also known as the chromosomes in the population. """

    def __init__(self):
        self.candidates = []
        return

    def seed(self, Nc, given):
        self.candidates = []

        # Determine the legal values that each square can take.
        helper = Candidate()
        helper.values = [[[] for j in range(0, Nd)] for i in range(0, Nd)]
        for row in range(0, Nd):
            for column in range(0, Nd):
                for value in range(1, 10):
                    if((given.values[row][column] == 0) and not (given.is_column_duplicate(column, value) or given.is_block_duplicate(row, column, value) or given.is_row_duplicate(row, value))):
                        # Value is available.
                        helper.values[row][column].append(value)
                    elif(given.values[row][column] != 0):
                        # Given/known value from file.
                        helper.values[row][column].append(given.values[row][column])
                        break

        # Seed a new population.
        for p in range(0, Nc):
            g = Candidate()
            for i in range(0, Nd): # New row in candidate.
                row = np.zeros(Nd)

                # Fill in the givens.
                for j in range(0, Nd): # New column j value in row i.

                    # If value is already given, don't change it.
                    if(given.values[i][j] != 0):
                        row[j] = given.values[i][j]
                    # Fill in the gaps using the helper board.
                    elif(given.values[i][j] == 0):
                        row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j])-1)]

                # If we don't have a valid board, then try again. There must be no duplicates in the row.
                while(len(list(set(row))) != Nd):
                    for j in range(0, Nd):
                        if(given.values[i][j] == 0):
                            row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j])-1)]

                g.values[i] = row

            self.candidates.append(g)

        # Compute the fitness of all candidates in the population.
        self.update_fitness()

        print("Seeding complete.")

        return

    def update_fitness(self):
        """ Update fitness of every candidate/chromosome. """
        for candidate in self.candidates:
            candidate.update_fitness()
        return

    def sort(self):
        """ Sort the population based on fitness. """
        self.candidates.sort(key=lambda candidate: candidate.fitness, reverse=True)
        return


class Candidate(object):
    """ A candidate solutions to the Sudoku puzzle. """
    def __init__(self):
        self.values = np.zeros((Nd, Nd), dtype=int)
        self.fitness = None
        return

    def update_fitness(self):
        """ The fitness of a candidate solution is determined by how close it is to being the actual solution to the puzzle. The actual solution (i.e. the 'fittest') is defined as a 9x9 grid of numbers in the range [1, 9] where each row, column and 3x3 block contains the numbers [1, 9] without any duplicates (see e.g. http://www.sudoku.com/); if there are any duplicates then the fitness will be lower. """

        row_count = np.zeros(Nd)
        column_count = np.zeros(Nd)
        block_count = np.zeros(Nd)
        row_sum = 0
        column_sum = 0
        block_sum = 0

        for i in range(0, Nd):  # For each row...
            for j in range(0, Nd):  # For each number within it...
                row_count[self.values[i][j]-1] += 1  # ...Update list with occurrence of a particular number.

            row_sum += (1.0/len(set(row_count)))/Nd
            row_count = np.zeros(Nd)

        for i in range(0, Nd):  # For each column...
            for j in range(0, Nd):  # For each number within it...
                column_count[self.values[j][i]-1] += 1  # ...Update list with occurrence of a particular number.

            column_sum += (1.0 / len(set(column_count)))/Nd
            column_count = np.zeros(Nd)

        # For each block...
        for i in range(0, Nd, 3):
            for j in range(0, Nd, 3):
                block_count[self.values[i][j]-1] += 1
                block_count[self.values[i][j+1]-1] += 1
                block_count[self.values[i][j+2]-1] += 1

                block_count[self.values[i+1][j]-1] += 1
                block_count[self.values[i+1][j+1]-1] += 1
                block_count[self.values[i+1][j+2]-1] += 1

                block_count[self.values[i+2][j]-1] += 1
                block_count[self.values[i+2][j+1]-1] += 1
                block_count[self.values[i+2][j+2]-1] += 1

                block_sum += (1.0/len(set(block_count)))/Nd
                block_count = np.zeros(Nd)

        # Calculate overall fitness.
        if (int(row_sum) == 1 and int(column_sum) == 1 and int(block_sum) == 1):
            fitness = 1.0
        else:
            fitness = column_sum * block_sum

        self.fitness = fitness
        return

    def mutate(self, mutation_rate, given):
        """ Mutate a candidate by picking a row, and then picking two values within that row to swap. """

        r = random.uniform(0, 1.1)
        while(r > 1): # Outside [0, 1] boundary - choose another
            r = random.uniform(0, 1.1)

        success = False
        if (r < mutation_rate):  # Mutate.
            while(not success):
                row1 = random.randint(0, 8)
                row2 = random.randint(0, 8)
                row2 = row1

                from_column = random.randint(0, 8)
                to_column = random.randint(0, 8)
                while(from_column == to_column):
                    from_column = random.randint(0, 8)
                    to_column = random.randint(0, 8)

                # Check if the two places are free...
                if(given.values[row1][from_column] == 0 and given.values[row1][to_column] == 0):
                    # ...and that we are not causing a duplicate in the rows' columns.
                    if(not given.is_column_duplicate(to_column, self.values[row1][from_column])
                       and not given.is_column_duplicate(from_column, self.values[row2][to_column])
                       and not given.is_block_duplicate(row2, to_column, self.values[row1][from_column])
                       and not given.is_block_duplicate(row1, from_column, self.values[row2][to_column])):

                        # Swap values.
                        temp = self.values[row2][to_column]
                        self.values[row2][to_column] = self.values[row1][from_column]
                        self.values[row1][from_column] = temp
                        success = True

        return success


class Given(Candidate):
    """ The grid containing the given/known values. """

    def __init__(self, values):
        self.values = values
        return

    def is_row_duplicate(self, row, value):
        """ Check whether there is a duplicate of a fixed/given value in a row. """
        for column in range(0, Nd):
            if(self.values[row][column] == value):
               return True
        return False

    def is_column_duplicate(self, column, value):
        """ Check whether there is a duplicate of a fixed/given value in a column. """
        for row in range(0, Nd):
            if(self.values[row][column] == value):
               return True
        return False

    def is_block_duplicate(self, row, column, value):
        """ Check whether there is a duplicate of a fixed/given value in a 3 x 3 block. """
        i = 3*(int(row/3))
        j = 3*(int(column/3))

        if((self.values[i][j] == value)
           or (self.values[i][j+1] == value)
           or (self.values[i][j+2] == value)
           or (self.values[i+1][j] == value)
           or (self.values[i+1][j+1] == value)
           or (self.values[i+1][j+2] == value)
           or (self.values[i+2][j] == value)
           or (self.values[i+2][j+1] == value)
           or (self.values[i+2][j+2] == value)):
            return True
        return False

class Sudoku(object):
    """ Solves the Sudoku puzzle using a Genetic Algorithm. """

    def __init__(self, population_size, mutation_rate, max_generations):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.population = Population()
        self.given = None
        self.fitness_history = []
        return

    def load(self, filename):
        """ Load the initial Sudoku puzzle from file. """
        self.given = Given(np.loadtxt(filename, dtype=int))
        print("Puzzle loaded.")
        return

    def load_from_data(self, data):
        """ Load the initial Sudoku puzzle from hardcoded data array. """
        self.given = Given(np.array(data, dtype=int))
        print("Puzzle loaded from data.")
        return

    def solve(self):
        """ Solve the puzzle. """

        # Seed initial population.
        self.population.seed(self.population_size, self.given)

        # Evolve the population.
        for generation in range(0, self.max_generations):

            # Print status.
            print(f"Generation {generation}, Best Fitness: {self.population.candidates[0].fitness}")
            print(self.population.candidates[0].values) # Print current best candidate values

            # Track fitness history
            self.fitness_history.append(self.population.candidates[0].fitness)

            # Check to see if we have found the solution.
            self.population.sort()
            if(self.population.candidates[0].fitness == 1):
                print(f"Solution found at generation {generation}!")
                print(self.population.candidates[0].values)
                break

            # Create the next generation.
            next_population = Population()

            # Elitism - add the fittest solutions to the next generation.
            elite_size = int(0.1 * self.population_size)
            next_population.candidates.extend(self.population.candidates[:elite_size])

            # Crossover.
            while(len(next_population.candidates) < self.population_size):
                parent1 = self.tournament_selection()
                parent2 = self.tournament_selection()
                child1, child2 = self.crossover(parent1, parent2)
                next_population.candidates.append(child1)
                next_population.candidates.append(child2)

            # Mutate the next generation.
            for candidate in next_population.candidates[elite_size:]:
                candidate.mutate(self.mutation_rate, self.given)

            # Update population.
            self.population = next_population

            # Update fitness.
            self.population.update_fitness()

        # Plot the fitness over generations
        plt.plot(self.fitness_history)
        plt.title('Fitness Over Generations')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.show()

        print("No solution found.")
        return

    def tournament_selection(self):
        """ Select a parent solution for crossover using tournament selection. """
        tournament_size = 5
        tournament = random.sample(self.population.candidates, tournament_size)
        tournament.sort(key=lambda candidate: candidate.fitness, reverse=True)
        return tournament[0]

    def crossover(self, parent1, parent2):
        """ Perform crossover between two parents to produce two children. """
        child1 = Candidate()
        child2 = Candidate()

        crossover_point = random.randint(1, Nd-2)

        for i in range(0, crossover_point):
            child1.values[i] = parent1.values[i]
            child2.values[i] = parent2.values[i]

        for i in range(crossover_point, Nd):
            child1.values[i] = parent2.values[i]
            child2.values[i] = parent1.values[i]

        return child1, child2


if __name__ == "__main__":
    # Define a hardcoded Sudoku puzzle (example)
    puzzle = [
      [5, 3, 0, 0, 7, 0, 0, 0, 0],
      [6, 0, 0, 1, 9, 5, 0, 0, 0],
      [0, 9, 8, 0, 0, 0, 0, 6, 0],
      [8, 0, 0, 0, 6, 0, 0, 0, 3],
      [4, 0, 0, 8, 0, 3, 0, 0, 1],
      [7, 0, 0, 0, 2, 0, 0, 0, 6],
      [0, 6, 0, 0, 0, 0, 2, 8, 0],
      [0, 0, 0, 4, 1, 9, 0, 0, 5],
      [0, 0, 0, 0, 8, 0, 0, 7, 9]
  ]

    # Initialize the Sudoku solver
    solver = Sudoku(population_size=1000, mutation_rate=0.1, max_generations=10000)

    # Load the puzzle from the hardcoded data
    solver.load_from_data(puzzle)

    # Solve the puzzle
    solver.solve()