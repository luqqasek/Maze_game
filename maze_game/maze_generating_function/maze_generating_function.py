from mazelib import Maze
from mazelib.generate.HuntAndKill import HuntAndKill
import random
import os


class MazeGenerator:
    """
    This abstract class allows to generate simple random level with given size using mazelib package and
    HuntAndKill algorithm. Generated level consists only of wall blocks, starting position and ending position.
    Implemented class methods allow to add additional special objects like coins and destructible walls and save
    generated model into text file.

    # Attributes
    ___________
    height: int
        Height of generated maze in number of blocks
    width: int
        Width of generated maze in number of blocks
    occupied_coordinates: ndarray
        ndarray of rows of generated level with 1 if block is a wall, exit or entrance and 0 otherwise
    max_additional_objects: int
        maximal number of additional objects that can be added to maze
    level_map: list
        list of rows of generated levels described in format used by game module

    # Methods
    ___________
    add_object(object_type: str,number_of_objects: int)
        adds special blocks to generated maze
    save_to_file(level_name: str)
        saves generated maze as text file
    """
    def __init__(self,
                 height: int = 9,
                 width: int = 9):
        """
        # Parameters
        ____________
        :param height: int, default = 9
            Height of generated maze in number of blocks. The minimal and default value equals to 9 as this is a
            limitation given by mazelib package
        :param width: int, default = 9
            Width of generated maze in number of blocks.The minimal and default value equals to 9 as this is a
            limitation given by mazelib package
        """
        height = int((height-1)/2)
        width = int((width-1)/2)
        m = Maze()
        m.generator = HuntAndKill(width, height)
        m.generate()
        m.generate_entrances(True, True)

        self.occupied_coordinates = m.grid
        self.max_additional_objects = (2*height+1)*(2*width+1) - m.grid.sum()
        self.height = height
        self.width = width

        # translating map into format that can be read by game module
        level_map = [list(row) for row in m.tostring().split("\n")]
        level_map[m.start[0]][m.start[1]] = "P"
        level_map[m.end[0]][m.end[1]] = "E"
        self.level_map = level_map

    def add_objects(self,
                    object_type: str,
                    number_of_objects: int):
        """
        This method allows to add special objects to initially generated maze. It randomly chooses places where to
        add one of two types of block: destructible block which can be destroyed by player or coin which can be
        collected by player.

        # Parameters
        :param object_type: {“interactive_block”, “coin”}, str
            Type of the block that will be added to maze. "interactive_block" is a destructible block.
        :param number_of_objects: int
            Number of special blocks that will be added to the maze.
        """

        possible_places = []
        # find places which aren't wall blocks, starting position or ending position

        for y, row in enumerate(self.occupied_coordinates):
            for x, occupied in enumerate(row):
                if occupied == 0:
                    possible_places.append((x, y))

        # out of possible places choose random places to add special block
        drawn_places = random.sample(possible_places, number_of_objects)
        for cord in drawn_places:
            self.occupied_coordinates[cord[1]][cord[0]] = 1
            if object_type == "interactive_block":
                self.level_map[cord[1]][cord[0]] = "I"
            elif object_type == "coin":
                self.level_map[cord[1]][cord[0]] = "C"

    def save_to_file(self,
                     level_name: str):
        """
        This method allows to save generated maze into a .txt file that can be read by a game module.

        # Parameters
        :param level_name: str
            Name of the text file in which a maze will be saved. Maze is saved in /levels/ folder which is located in
            the same directory as maze_generating_function.py file.
        """
        text_file = open(f"{os.getcwd()}/../resources/levels/{level_name}.txt", "w")
        text_file.write(f"{self.height*2+1},{self.width*2+1}\n")
        for element in self.level_map:
            text_file.write("".join(element) + "\n")
        text_file.close()
