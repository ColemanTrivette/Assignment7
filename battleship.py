
import random


# This class sets up the players and keeps the game going until somebody wins.
class BattleshipGame:

    def __init__(self, num_of_players):
        # One player means playing against the computer. Two players keeps the original setup.
        if num_of_players == 1:
            self.players = [HumanPlayer("Player 1"), ComputerPlayer("The Computer")]
        else:
            self.players = [HumanPlayer("Player 1"), HumanPlayer("Player 2")]

        # Each player needs to know whose board they will be attacking.
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])

    def play(self):
        # Both players place their boats before anyone starts attacking.
        self.players[0].position_fleet()
        self.players[1].position_fleet()

        input("The boats are ready... it's time to play.  Press enter to begin!")
        winner = False
        first_players_turn = True

        # Take turns until one player has hit all 17 of the other player's boat spaces.
        while not winner:
            if first_players_turn:
                winner = self.players[0].take_turn()
                if winner:
                    print(f"Game over! {self.players[0].player_name} wins!")
            else:
                winner = self.players[1].take_turn()
                if winner:
                    print(f"Game over! {self.players[1].player_name} wins!")

            first_players_turn = not first_players_turn


# This class handles the 10x10 board, including placing boats and recording attacks.
class Board:

    def __init__(self):
        self.grid = [[" _"] * 10 for i in range(10)]
        self.hit_count = 0

    def __str__(self):
        # Show every space, including the boats on the player's own board.
        str_val = "  0 1 2 3 4 5 6 7 8 9\n"
        for i in range(10):
            str_val += str(i)
            for j in range(10):
                str_val += self.grid[i][j]
            if i != 9:
                str_val += "\n"
        return str_val

    def get_public_view(self):
        # Hide boats on the opponent's board, but still show hits and misses.
        str_val = "  0 1 2 3 4 5 6 7 8 9\n"
        for i in range(10):
            str_val += str(i)
            for j in range(10):
                if self.grid[i][j] == " B":
                    str_val += " _"
                else:
                    str_val += self.grid[i][j]
            if i != 9:
                str_val += "\n"
        return str_val

    def add_boat(self, boat):
        # Figure out how much room the boat needs based on its direction.
        width = 1
        height = 1
        if boat.orientation == "v":
            height = boat.size
        else:
            width = boat.size

        # Don't allow a boat to go outside the board.
        if (boat.x < 0) or (boat.y < 0) or (boat.x + width > 10) or (boat.y + height > 10):
            return False

        # Make sure none of the spaces already have another boat.
        for x in range(width):
            for y in range(height):
                if self.grid[boat.y + y][boat.x + x] != " _":
                    return False

        # All the spaces are available, so the boat can be placed here.
        for x in range(width):
            for y in range(height):
                self.grid[boat.y + y][boat.x + x] = " B"
        return True

    def attack(self, x, y):
        # A boat becomes a hit, and an empty space becomes a miss.
        current_value = self.grid[y][x]
        if current_value == " B":
            self.grid[y][x] = " X"
            self.hit_count += 1
            return True
        elif current_value == " _":
            self.grid[y][x] = " O"
            return False
        else:
            return False

    def is_defeated(self):
        # There are 17 boat spaces total between all five boats.
        return self.hit_count == 17


# Each boat stores its size, position, and direction on the board.
class Boat:

    def __init__(self, label, size):
        self.label = label
        self.size = size
        self.x = None
        self.y = None
        self.orientation = None

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_orientation(self, orientation):
        self.orientation = orientation


# Human players choose their own boat positions and attacks.
class HumanPlayer:

    def __init__(self, player_name):
        self.player_name = player_name
        self.board = Board()
        self.fleet = [Boat("Aircraft Carrier", 5), Boat("Battleship", 4),
                      Boat("Submarine", 3), Boat("Destroyer", 3), Boat("Patrol Boat", 2)]
        self.opponent = None

        # Start all the attack statistics at zero for each player.
        self.attacks = 0
        self.hits = 0
        self.misses = 0

    def set_opponent(self, opponent):
        self.opponent = opponent

    def show_stats(self):
        # Display the player's numbers before their next attack, like the sample output.
        print("You have attacked ", self.attacks, " times, with ", self.hits,
              " hits and ", self.misses, " misses.")

    def record_attack(self, hit_flag):
        # Every new attack counts once, whether it hits a boat or not.
        self.attacks += 1
        if hit_flag:
            self.hits += 1
        else:
            self.misses += 1

    def position_fleet(self):
        input(self.player_name + ": Are you ready to position your fleet?  Press enter to begin!")

        # Go through all five boats and ask the player where to put each one.
        for boat in self.fleet:
            self.position_boat(boat)

        print("Your fleet is ready to play.  Your board is positioned as follows:")
        print(self.board)

    def position_boat(self, boat):
        print(self.board)
        print(f"You need to position a {boat.label} of length {boat.size} on the board above.")

        # Keep asking until the player picks a valid direction.
        orientation = None
        while orientation is None:
            orientation = input("Would you like to use a vertical or horizontal orientation? (v/h) ")
            if (orientation != "v") and (orientation != "h"):
                print("You must enter a 'v' or a 'h'.  Please try again.")
                orientation = None

        # The boat needs to fit on the board without covering any other boats.
        position = None
        while position is None:
            try:
                position = input("Please enter the position for the top-left location of the boat. " +
                                 " Use the form x,y (e.g., 1,3): ")
                coords = position.split(",")
                x = int(coords[0])
                y = int(coords[1])
                boat.set_orientation(orientation)
                boat.set_position(x, y)

                if not self.board.add_boat(boat):
                    raise Exception()
            except (ValueError, IndexError):
                print("You must enter a valid position for the boat.  Please try again.")
                position = None
            except Exception:
                print("You must choose a position that is (a) on the board and (b) doesn't intersect " +
                      "with any other boats.")
                position = None

    def take_turn(self):
        # Show the player's boats and only the known parts of the opponent's board.
        print(f"{self.player_name}'s board:")
        print(self.board)
        print()
        print(f"Your view of {self.opponent.player_name}'s board:")
        print(self.opponent.board.get_public_view())
        self.show_stats()

        # Make sure the attack is on the board and hasn't already been tried.
        position = None
        while position is None:
            try:
                position = input("Please enter the position you would like to attack.  Use the form x,y (e.g., 1,3): ")
                coords = position.split(",")
                x = int(coords[0])
                y = int(coords[1])
                if (x < 0) or (x > 9) or (y < 0) or (y > 9):
                    raise ValueError()
                if self.opponent.board.grid[y][x] in (" X", " O"):
                    print("You already attacked that position. Please try again.")
                    position = None
            except (ValueError, IndexError):
                print("You must enter a valid position in the form x,y where both x and y are integers in the range of " +
                      "0-9. Please try again.")
                position = None

        # Attack the selected space and update the statistics.
        hit_flag = self.opponent.board.attack(x, y)
        self.record_attack(hit_flag)
        if hit_flag:
            print("You hit a boat!")
        else:
            print("You missed.")

        return self.opponent.board.is_defeated()


# The computer uses the same basic player setup, but never asks for input.
class ComputerPlayer(HumanPlayer):

    def __init__(self, player_name):
        super().__init__(player_name)

        # Keep a list of all possible attacks so the computer never repeats a spot.
        self.available_attacks = [(x, y) for y in range(10) for x in range(10)]

    def position_fleet(self):
        # Give every boat a random direction and position until it fits on the board.
        for boat in self.fleet:
            placed = False
            while not placed:
                orientation = random.choice(["v", "h"])
                if orientation == "v":
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - boat.size)
                else:
                    x = random.randint(0, 10 - boat.size)
                    y = random.randint(0, 9)

                boat.set_orientation(orientation)
                boat.set_position(x, y)
                placed = self.board.add_boat(boat)

        print("The computer has positioned its fleet.")

    def show_stats(self):
        # The computer also keeps track of hits, misses, and total attacks.
        print("The computer has attacked ", self.attacks, " times, with ", self.hits,
              " hits and ", self.misses, " misses.")

    def take_turn(self):
        self.show_stats()

        # Randomly pick an unused location, then remove it from the available list.
        x, y = random.choice(self.available_attacks)
        self.available_attacks.remove((x, y))

        hit_flag = self.opponent.board.attack(x, y)
        self.record_attack(hit_flag)

        # Tell the human which square the computer attacked and whether it hit.
        if hit_flag:
            print(f"The computer attacked ({x},{y}) and hit a boat!")
        else:
            print(f"The computer attacked ({x},{y}) and missed.")

        return self.opponent.board.is_defeated()
    # ChatGPT helped me to devleop the ComputerPlayer's ability to randomly position ships and attack the players board without repeating locations. It also helped me to come up with how to track game stats.