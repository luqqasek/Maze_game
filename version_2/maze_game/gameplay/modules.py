from PIL import Image, ImageTk
import os
import pygame

BLOCK_TYPES = {"#": "wall",
               " ": "black",
               "E": "exit",
               "I": "obstacle",
               "C": "coin"}


class BuildingBlock:
    """
    This abstract class is used to store information about basic building block of a maze.
    # Attributes
    ___________
    x_coordinate: int
        x coordinate of block
    y_coordinate: int
        y coordinate of block
    accessible: bool
        indicate if block is accessible by player
    destructible: bool
        indicate if block is destructible by player
    is_exit_block: bool
        indicate if block is an exit from a maze
    block_type: str
        type of block, can be equal to {"#", " ", "E", "I", "C"}
    is_open: bool
        indicates if doors are open, used only on door block

    # Methods
    ___________
    draw(canvas, size: int)
        draw block on given canvas and with given size
    """

    def __init__(self,
                 x_coordinate: int,
                 y_coordinate: int,
                 accessible: bool,
                 destructible: bool,
                 is_exit_block: bool,
                 block_type: str,
                 is_open: bool = True):
        """
        # Parameters
        ____________
        :param x_coordinate: int
            x coordinate of block
        :param y_coordinate: int
            y coordinate of block
        :param accessible: bool
            indicate if block is accessible by player
        :param destructible: bool
            indicate if block is destructible by player
        :param is_exit_block: bool
            indicate if block is an exit from a maze
        :param block_type: str
            type of block, can be equal to {"#", " ", "E", "I", "C"}
        :param is_open: bool, default = True
            indicates if doors are open, used only on door block
        """
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.accessible = accessible
        self.is_exit_block = is_exit_block
        self.destructible = destructible
        self.block_type = block_type
        self.is_open = is_open

    def draw(self,
             canvas,
             size: int):
        """
        Draws building block on a given canvas
        
        :param canvas: tkinter Canvas class
            Tkinter canvas where block should be drawn
        :param size: int
            size of the block in pixels
        """
        canvas_origin = canvas.canvas_origin
        
        block_type = BLOCK_TYPES[self.block_type]
        # finding if exit is open or closed
        if block_type == "exit":
            if self.is_open: 
                block_type = "exit_open"
            else: 
                block_type = "exit_closed"

        image = ImageTk.PhotoImage(Image.open(f"{os.getcwd()}/../resources/graphics/building_block/{block_type}.png").\
                                   resize((int(size),
                                           int(size)),
                                   Image.ANTIALIAS))
        
        # to prevent the image from being deleted by garbage collected save it in dict.
        canvas.images[self.block_type+str(self.x_coordinate)+"_"+str(self.y_coordinate)] = image
        canvas.create_image(self.x_coordinate*size + canvas_origin[0],
                            self.y_coordinate*size + canvas_origin[1],
                            image=canvas.images[self.block_type+str(self.x_coordinate)+"_"+str(self.y_coordinate)],
                            anchor="nw")


class LevelMap:
    """
    This abstract class is used to store information about level of maze and load this information from a text file.

    # Attributes
    ___________
    x_size: int = 0,
        width of level
    y_size: int = 0,
        height of level
    player_starting_coordinate_x: int = 0,
        player starting coordinate x
    player_starting_coordinate_y: int = 0,
        player starting coordinate y
    level_map=None,
        level map stored as list of rows, where each row is a BuildingBlock class object
    number_of_coins: int = 0
        number of coins left to collect to open exit in current level

    # Methods
    ___________
    load_from_file(path: str)
        Loads a level from text file which is in given directory
    """
    def __init__(self,
                 x_size: int = 0,
                 y_size: int = 0,
                 player_starting_coordinate_x: int = 0,
                 player_starting_coordinate_y: int = 0,
                 level_map=None,
                 number_of_coins: int = 0):
        """
        # Parameters
        ____________
        :param x_size: int = 0,
            width of level
        :param y_size: int = 0,
            height of level
        :param player_starting_coordinate_x: int = 0,
            player starting coordinate x
        :param player_starting_coordinate_y: int = 0,
            player starting coordinate y
        :param level_map=None,
            level map stored as list of rows, where each row is a BuildingBlock class object
        :param number_of_coins: int = 0
            number of coins left to collect to open exit in current level
        """
        self.x_size = x_size
        self.y_size = y_size
        self.player_starting_coordinate_x = player_starting_coordinate_x
        self.player_starting_coordinate_y = player_starting_coordinate_y
        self.level_map = level_map
        self.number_of_coins = number_of_coins

    def load_from_file(self,
                       path: str):
        """
        Loads level from .txt file. First row of file has width and height of level described in number of blocks.
        Next rows describe consecutive rows of level. "#" character describes wall, " " describes empty space,
        accessible by player, "I" describes destructible block and "C" describes coin.

        # Parameters
        loads text file that has specific format used by game
        ____________
        :param path:
            path to textfile that will be loaded to LevelMap class
        """
        # clear current level
        self.level_map = []
        level_file = open(path, 'r')
        lines = level_file.readlines()
        for i, line in enumerate(lines):
            # first line always store map size
            if i == 0:
                self.x_size = int(line.rstrip().split(",")[0])
                self.y_size = int(line.rstrip().split(",")[1])

            # the rest of rows are describing level map
            else:
                row = line.rstrip()
                if any(el == "P" for el in row):
                    self.player_starting_coordinate_x = row.index("P")
                    self.player_starting_coordinate_y = i-1
                    row = row.replace("P", " ")
                if any(el == "E" for el in row):
                    exit_coord = (row.index("E"), i-1)

                # counts total number of coins in loaded level
                self.number_of_coins = self.number_of_coins + line.count("C")

                block_list = [BuildingBlock(x_coordinate=x,
                                            y_coordinate=i-1,
                                            accessible=False if block in ["#", "I"] else True,
                                            destructible=True if block == "I" else False,
                                            is_exit_block=True if block == "E" else False,
                                            block_type=block) for x, block in enumerate(row)]
                self.level_map.append(block_list)

        # if map has coins to collect, changes exit block to be closed and unaccessible for player
        if self.number_of_coins:
            self.level_map[exit_coord[1]][exit_coord[0]].is_open = False
            self.level_map[exit_coord[1]][exit_coord[0]].accessible = False


class Player:
    """
    This abstract class is used to store information about player and perform all the operation that player can do.
    This is why player is connected to Tkinter canvas where level is displayed and also has information about current
    level to which he is connected. This class is a bridge between GUI and played level.

    # Attributes
    ___________
    current_coordinate_x: int
        current x coordinate of player on map
    current_coordinate_y: int
        current y coordinate of player on map
    level_map: LevelMap class
        map level of a current level the player is playing
    canvas
        Tkinter object that is used to display Player
    size: int
        size in pixels of player block
    direction: tuple
        tuple indicating direction player is facing (1,0) indicates east direction, (-1,0) indicates west direction,
        (0,1) indicates north direction, (0,-1) indicates south direction
    coins_collected: int
        total number of coins player collected through whole game
    # Methods
    ___________
    move(move_x: int, move_y: int)
        changes position of player on map
    open_exit()
        opens exit if player collected all coins
    destroy_block()
        destroys block player is facing if it is possible
    draw(size)
        draws player on canavs
    """
    def __init__(self,
                 canvas,
                 level_map,
                 size: int,
                 direction: tuple = (0, 1),
                 coins_collected: int = 0):
        """
        # Parameters
        ____________
        :param canvas: tkinter Canvas class
            tkinter canvas at which player should be displayed
        :param level_map: LevelMap class
            LevelMap object that current player can interact with
        :param size:
            size in pixels of a player
        :param direction: tuple
            direction that a player is currently facing:
            (1,0) - East
            (0,1) - North
            (-1,0) - West
            (0,-1) - South
        :param coins_collected: int
            number of coins a player collected
        """
        self.current_coordinate_x = level_map.player_starting_coordinate_x
        self.current_coordinate_y = level_map.player_starting_coordinate_y
        self.level_map = level_map
        self.canvas = canvas
        self.size = size
        self.direction = direction
        self.coins_collected = coins_collected
        self.draw(size=size)

    def move(self,
             move_x: int,
             move_y: int):
        """
        This method moves a player around his level and changes its appearance on a canvas

        # Parameters
        ____________
        :param move_x: int
            Parameter specifying how many blocks should player move on the x axis, positive numbers indicate movement to
            the east direction, negative to the west direction
        :param move_y: int
            Parameter specifying how many blocks should player move on the y axis, positive numbers indicate movement to
            the north direction, negative to the south direction
        """
        self.direction = (move_x, move_y)
        self.draw(self.size)

        # check whether movement finishes out of map that a player is currently on
        if self.current_coordinate_y + move_y > self.level_map.y_size - 1 or \
           self.current_coordinate_y + move_y < 0 or \
           self.current_coordinate_x + move_x > self.level_map.x_size - 1 or \
           self.current_coordinate_x + move_x < 0:
            return 0

        # check whether movement finishes on accessible block
        target_block = self.level_map.level_map[self.current_coordinate_y + move_y][self.current_coordinate_x + move_x]
        if not target_block.accessible:
            return 0

        # check whether movement finishes on a coin block
        if target_block.block_type == "C":
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/coin_pick.wav"))
            self.coins_collected = self.coins_collected + 1
            self.level_map.number_of_coins = self.level_map.number_of_coins - 1
            target_block.block_type = " "
            if self.level_map.number_of_coins == 0:
                self.open_exit()
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/door_unlock.wav"))

        current_block = self.level_map.level_map[self.current_coordinate_y][self.current_coordinate_x]
        current_block.draw(canvas=self.canvas,
                           size=self.size)

        # updating player coordinates
        self.current_coordinate_y = self.current_coordinate_y + move_y
        self.current_coordinate_x = self.current_coordinate_x + move_x

        self.draw(size=self.size)

    def open_exit(self):
        """
        This method opens the doors when its run
        """
        for y, row in enumerate(self.level_map.level_map):
            for x, block in enumerate(row):
                if block.is_exit_block == 1:
                    block.is_open = True
                    block.accessible = True
                    block.draw(canvas=self.canvas,
                               size=self.size)

    def destroy_block(self):
        """
        This method destroys a block if it is possible that a player is currently facing
        """
        # check whether block is destructible
        target_block = self.level_map.level_map[self.current_coordinate_y + self.direction[1]]\
            [self.current_coordinate_x + self.direction[0]]
        if not target_block.destructible:
            return 0
        target_block.accessible = True
        target_block.destructible = False
        target_block.block_type = " "
        target_block.draw(canvas=self.canvas,
                          size=self.size)

        pygame.mixer.Channel(0).play(pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/digging.wav"))

    def draw(self,
             size):
        """
        This method draws a player on a canvas associated with a player
        # Parameters
        ____________

        :param size: int
            size in pixels of a side of a player block representing player
        """
        # Dict of file names describing facing direction of gnome
        gnome_image = {"(1, 0)": "gnome_e",
                       "(0, 1)": "gnome_s",
                       "(0, -1)": "gnome_n",
                       "(-1, 0)": "gnome_w"}

        canvas_origin = self.canvas.canvas_origin
        image = ImageTk.PhotoImage(Image.open(f"{os.getcwd()}/../resources/graphics/gnome/{gnome_image[str(self.direction)]}.png").
                                   resize((int(size), int(size)),
                                   Image.ANTIALIAS))

        # to prevent the image from being deleted by garbage collector we save it in dict.
        self.canvas.images["gnome"] = image
        self.canvas.create_image(self.current_coordinate_x * size + canvas_origin[0],
                                 self.current_coordinate_y * size + canvas_origin[1],
                                 image=self.canvas.images["gnome"],
                                 anchor="nw")
