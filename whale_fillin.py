import random
import math


def dist(x1, y1, x2, y2):
    return int(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))  # L_2

########################################################################


class Whale:
    whale_range = 10     # 10

    def __init__(self):
        self.x = random.randrange(self.whale_range)
        self.y = random.randrange(self.whale_range)

    def move(self):
        moves = [-1, 0, 1]
        x1, y1 = self.x, self.y

        while (x1 == self.x and y1 == self.y) or not(0 <= x1 < self.whale_range) or not(0 <= y1 < self.whale_range):
            x1 = self.x + random.choice(moves)
            y1 = self.y + random.choice(moves)

        self.x, self.y = x1, y1

    def estimated_by(self, ship):
        ship.measure(dist(self.x, self.y, ship.x, ship.y))

    def found_by(self, ship):
        return dist(self.x, self.y, ship.x, ship.y) == 0

    def __repr__(self):
        return "Whale blows at %d,%d" % (self.x, self.y)

########################################################################


class Ship:
    def __init__(self, xwhale, ywhale):
        self.x_range = xwhale
        self.y_range = ywhale

        # this is the a priori probability
        p_w = {}
        for x in range(xwhale):
            for y in range(ywhale):
                p_w[x, y] = 1/(self.x_range*self.y_range)

        self.p_w = p_w

        self.x = random.randrange(self.x_range)
        self.y = random.randrange(self.y_range)

    # characteristics of distance measure: p(d|x,y) where x,y is a
    # possible position of the whale (remember the mine problem)

    def p_d_cond_w(self, d, x, y):
        return int(dist(x, y, self.x, self.y) == d)

    def measure(self, d):
        # Copy original dictionary and updates each coordinate to zero
        p_w_cond_d = self.p_w.copy()
        p_w_cond_d.update((x, y * 0) for x, y in p_w_cond_d.items())

        total = 0
        w = [-1, 0, 1]

        for x, y in [(x, y) for x in range(self.x_range) for y in range(self.y_range)]:
            # Check if whale can be in position (x,y)
            if self.p_d_cond_w(d, x, y):
                # Get whale surrounding moves
                for whale_moves in [(x1+c1, y1+c2) for (x1, y1) in self.p_w for c1 in w for c2 in w if
                        x1 == x and y1 == y and 0 <= x1+c1 < self.x_range and 0 <= y1+c2 < self.y_range]:

                    # Update current whale possible position (x,y) with new value
                    p_w_cond_d[x, y] += self.p_w[whale_moves]
                    total += self.p_w[whale_moves]

        # Update values to be between 0 and 1
        p_w_cond_d.update((x, y * (1 / total)) for x, y in p_w_cond_d.items())
        self.p_w = p_w_cond_d

    def show_model(self):
        print("(0,", self.y_range-1, ")", sep='')
        for y in reversed(range(self.y_range)):
            print("   ", end=" ")
            spaces = ""

            for x in range(self.x_range):
                percentage_value = "%.1f" % (self.p_w[x, y] * 100) + "%"
                print("|", end=" ")

                if x == self.x and y == self.y:
                    print("Ship ", end="")
                elif self.p_w[x, y] == 0:
                    print(" 0%  ", end="")
                else:
                    print(percentage_value, end="")
                    if self.p_w[x, y] < 0.0996:
                        print(end=" ")

                spaces += "       "
            print("|")

        print("(0,0)", spaces, "(", self.x_range-1, ",0)", sep='')

    def move(self):
        # If ship on top of whale, don't move
        if self.p_w[self.x, self.y] == 1:
            return

        # Add to a list the highest probability positions of the whale
        best_whale_positions = []
        max_prob = 0
        for x, y in [(x, y) for x in range(self.x_range) for y in range(self.y_range)]:
            if self.p_w[x, y] > max_prob:
                max_prob = self.p_w[x, y]
                best_whale_positions = [[x, y]]
            elif max_prob != 0 and self.p_w[x, y] == max_prob:
                best_whale_positions.append([x, y])

        # Add to a list the possible moves of the Ship
        ship_moves = []
        w = [-1, 0, 1]
        for x, y in [(x, y) for x in w for y in w]:
            temp_x, temp_y = self.x+x, self.y+y
            if 0 <= temp_x < self.x_range and 0 <= temp_y < self.y_range and (temp_x, temp_y) != (self.x, self.y):
                ship_moves.append([temp_x, temp_y])

        # Add to a list the best movements for the Ship to take
        best_move = []
        best_move_cont = 0
        for ship_x, ship_y in ship_moves:
            points = 0
            for whale_x, whale_y in best_whale_positions:
                ship_whale_initial = dist(self.x, self.y, whale_x, whale_y)
                ship_whale_final = dist(ship_x, ship_y, whale_x, whale_y)

                # Add 1 point if Ship is closer to the Whale
                if ship_whale_final < ship_whale_initial: points += 1
                # Add 2 points if Ship is on top of a possible Whale position
                elif ship_whale_final == 0: points += 2

            # If score is higher than the previous possible Ship move replace best_move, else add new move to list
            if points > best_move_cont:
                best_move, best_move_cont = [(ship_x, ship_y)], points
            elif points == best_move_cont:
                best_move.append((ship_x, ship_y))

        # Choose a move at random from the best moves
        best_move = random.choice(best_move)
        self.x, self.y = best_move[0], best_move[1]

    def __repr__(self):
        return "Ship at %d,%d" % (self.x, self.y) # pretty print

########################################################################


def run(whale, ship):
    while not whale.found_by(ship):
        input()
        whale.move()
        whale.estimated_by(ship)    # ship gets distance

        ship.show_model()           # show current Bayesian model
        ship.move()                 # to be filled in
        print(ship)
    print("Whale found")


whale = Whale()
ship = Ship(whale.whale_range, whale.whale_range)
run(whale, ship)



