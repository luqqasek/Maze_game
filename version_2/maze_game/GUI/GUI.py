import tkinter as tk
import time
from gameplay.modules import *
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageTk
from maze_generating_function.maze_generating_function import *
import shutil
import pandas as pd
from datetime import datetime
import pygame

# Constant variables
# latin alphabet is a set of possible characters in players name that have image in graphics directory
LATIN_ALPHABET = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
                  'u', 'w', 'x', 'y', 'z')
INFO_PANEL_SIZE = 80
# padding of exit button
PADDING_X = 40
# Time limit to finish level/s
TIME_LIMIT = 180
# Number of coins in adventure mode
COINS = 9
# Number of destructible blocks in adventure mode
DESTRUCTIBLE_BLOCKS = 20
# Level width and height for adventure mode
LEVEL_WIDTH = 15
LEVEL_HEIGHT = 15


def validate(P):
    if len(P) == 0:
        return True
    elif len(P) <= 5 and set(list(P)).issubset(LATIN_ALPHABET):
        return True
    else:
        return False


class App(tk.Tk):
    """
    This abstract class runs the application. It is a tkinter object and therefore inherits from tk.Tk.

    # Attributes
    ___________
    width: int
        Width of the tkinter application
    height: int,
        Height of the tkinter application
    container: tk.Frame
        A tkinter frame

    # Methods
    ___________
    show_frame()
        displays a specific tkinter frame or widget
    """
    def __init__(self):
        super().__init__()

        pygame.mixer.init()

        # Setting window configs
        self.width = 1280
        self.height = 720
        self.title('Maze game')
        self.geometry(str(self.width) + 'x' + str(self.height))
        self.resizable(False, False)

        # Centering window in user's screen
        position_right = int(self.winfo_screenwidth() / 2 - self.width / 2)
        position_down = int(self.winfo_screenheight() / 2 - self.height / 2)
        self.geometry("+{}+{}".format(position_right, position_down))

        # Creating container
        self.container = tk.Frame(self)
        self.container.pack()

        # Displaying Main Menu
        self.current_tab = None
        self.show_frame(GameMenu)

        # Loading menu music
        pygame.mixer.music.load(f"{os.getcwd()}/../resources/sounds/menu_ost.wav")
        pygame.mixer.music.play(loops=-1)

    def show_frame(self,
                   new_page,
                   level_name=None,
                   player_name=None):
        """
        Method to display specific tkinter frame

        # Parameters
        ____________
        :param new_page: str,
            Name of the frame to display
        :param level_name: string
            When displaying GameScreen, carries the name of the level file to be loaded if playing solo mode
        :param player_name: string
            When displaying GameScreen, carries the player name for the leaderboard
        """
        if new_page.__name__ == "GameScreen":
            # Initializing game with given level and player name
            tab = new_page(parent=self.container, controller=self, level_name=level_name, player_name=player_name)
        else:
            tab = new_page(parent=self.container, controller=self)

        # Removing currently shown tab
        if self.current_tab:
            self.current_tab.grid_remove()

        # Displaying desired tab
        self.current_tab = tab
        tab.grid(row=0, column=0, sticky="nsew")


class GameMenu(tk.Canvas):
    """
    This abstract class manages the game menu. It is a tkinter canvas and therefore inherits from tk.Canvas.

    # Methods
    ___________
    add_button()
        creates main menu button
    """
    def __init__(self,
                 parent,
                 controller):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window ,
            parent tkinter widget
        :param controller: class,
            Refers back to the app class for control and interactions between tkinter widgets
        """
        self.controller = controller

        # Creating Canvas and background
        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height)
        bg = ImageTk.PhotoImage(Image.open(f"{os.getcwd()}/../resources/graphics/menu_bg.png").resize((controller.width,
                                                                                          controller.height),
                                                                                         Image.ANTIALIAS))
        self.create_image(0, 0, anchor="nw", image=bg)
        self.image = bg

        # Positioning button on canvas
        button_names = {"start_game_button": ModeChooser,
                        "generate_level_button": LevelGenerator,
                        "instruction_button": Instruction,
                        "leaderboard_button": Leaderboard}

        for i, name in enumerate(button_names.keys()):
            if i < 2:
                self.add_button(4.2 * controller.width / 10, (i + 5) * controller.height / 9, name, button_names[name])
            else:
                self.add_button(5.8 * controller.width / 10, (i + 3) * controller.height / 9, name, button_names[name])
        self.add_button(5 * controller.width / 10, 7 * controller.height / 9, "exit_button", "quit")

    def add_button(self,
                   x: int,
                   y: int,
                   button_name: str,
                   function):
        """
        Method to create main menu button

        # Parameters
        ____________
        :param x: int,
            X coordinate to position the button on canvas
        :param y: int,
            Y coordinate to position the button on canvas
        :param button_name: str,
            Button name
        :param function: str
            Function triggered by button, usually opening a tkinter widget
        """
        button1 = CustomButton(master=self,
                               image_path=f"{os.getcwd()}/../resources/graphics/buttons/{button_name}.png",
                               command=lambda: [(quit() if function == "quit" else
                                                 self.controller.show_frame(function)),
                                                pygame.mixer.Channel(0).play(
                                                    pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])
        self.create_window(x, y, window=button1)


class GameScreen(tk.Canvas):
    """
    This abstract class manages the current game screen. It is a tkinter canvas and therefore inherits from tk.Canvas.

    # Attributes
    ___________
    controller: App class
        Refers back to the app class for control and interactions between tkinter widgets
    level_name: string
        Carries the name of the level file to be loaded if playing solo mode
    player_name: string
        Carries the player name for the leaderboard
    player.current_coins: int
        Current number of coins picked up by player in the level
    images: dict
        Dictionary of images displayed during some specific events
    canvas_origin: tuple
        Coordinates of the origin of the canvas
    P: class
        An instance of a player class

    # Methods
    ___________
    pause()
        pauses the game on and off
    update_timer()
        keeps the timer up to date, takes into account whether game is paused or not
    action(event=None)
        manages player keyboard inputs
    check_if_next_level()
        checks if exit is reached and if requirements for next level are met
    draw_level()
        calls maze generating function to draw a new level. Also loads specific level if solo mode is selected
    end_of_game()
        triggers the end of the game, and stores final score into leaderboard
    """
    def __init__(self,
                 parent,
                 controller,
                 level_name=None,
                 player_name=None):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        :param level_name: string
            Carries the name of the level file to be loaded if playing solo mode
        :param player_name: string
            Carries the player name for the leaderboard
        """
        self.controller = controller
        self.level_name = level_name
        self.player_name = "unknw" if player_name == "" else player_name
        self.current_coins = 0
        self.images = {}
        self.canvas_origin = None
        self.P = None

        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height, bg='black')

        exit_button = CustomButton(master=self,
                                   image_path=f"{os.getcwd()}/../resources/graphics/buttons/go_back_button.png",
                                   command=lambda: [controller.show_frame(GameMenu),
                                                    pygame.mixer.music.load(f"{os.getcwd()}/../resources/sounds/menu_ost.wav"),
                                                    pygame.mixer.music.set_volume(1),
                                                    pygame.mixer.music.play(loops=-1),
                                                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(
                                                        f"{os.getcwd()}/../resources/sounds/button.wav"))])

        self.create_window(PADDING_X, INFO_PANEL_SIZE / 2, window=exit_button)

        self.draw_level()

        self.focus_set()  # initially frame doesn't have focus so binding doesn't work without this part

        # Timer and pause functionalities initialization
        self.is_paused = False
        self.pause_label = tk.Label(self, text="GAME PAUSED", fg="dark red", bg="black", font="Helvetica 40 bold")
        global start_time
        start_time = time.time()
        global timer
        timer = tk.Label(self, text="Remaining time: 300", fg="dark red", bg="black", font="Helvetica 20 bold")
        timer.place(relx=0.99, rely=0.01, anchor="ne")
        self.update_timer()

        # Adding music
        pygame.mixer.music.load(f"{os.getcwd()}/../resources/sounds/game_ost.mp3")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(loops=-1)

        # Binding keyboard
        self.bind('<Key>', self.action)

    def pause(self):
        """
        This method allows to pause the current game, simply switching a boolean variable on and off, unbinding
        keys so player can't move, as well as the music and the pause label.　
        """
        if self.is_paused:
            self.pause_label.place_forget()
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            self.pause_label.place(relx=0.5, rely=0.5, anchor="center")
            pygame.mixer.music.pause()
            self.is_paused = True

    def update_timer(self):
        """
        This method manages the timer feature of the game, which is only allowed to run when the game isn't paused.
        Elapsed time is measured in seconds and subtracted from the time limit, displayed on a counter via a label.
        When the time limit is reached, the game ends itself.
        The function uses global variables to make sure we keep track of the timer between different instances of
        the game screen.
        The function calls itself repeatedly every second to update itself.
        When the game is paused, we update the start_time with the current time for when the timer resumes.
        """
        global start_time
        global elapsed_time
        if not self.is_paused:
            elapsed_time = time.time() - start_time
            if elapsed_time > TIME_LIMIT:
                self.end_of_game()

                timer.configure(text="Remaining time: 0")
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/victory.wav"))
                return

            timer.configure(text="Remaining time: "+str(TIME_LIMIT - int(elapsed_time)))
            self.after(ms=1000, func=self.update_timer)
        else:
            start_time = time.time() - elapsed_time
            self.after(ms=1000, func=self.update_timer)

    def action(self,
               event=None):
        """
        This method manages player input and related actions, mainly player movements, block destruction
        and pause button. It also checks whether the exit has been reached after each movement input.
        # Parameters
        :param event:
            player keyboard input
        """
        # Check if game is paused and limit player action if true
        if self.is_paused:
            if event.char == "p":
                self.pause()
        else:
            if event.char == "a":
                self.P.move(move_x=-1, move_y=0)
            elif event.char == "d":
                self.P.move(move_x=1, move_y=0)
            elif event.char == "w":
                self.P.move(move_x=0, move_y=-1)
            elif event.char == "s":
                self.P.move(move_x=0, move_y=1)
            elif event.char == "e":
                self.P.destroy_block()
            elif event.char == "p":
                self.pause()

        # Check if after movement player found an exit
        if event.char in ["a", "d", "w", "s"]:
            self.check_if_next_level()

    def check_if_next_level(self):
        """
        This method checks if player has reached the exit of the level and if requirements for switching
        to the next level are cleared.
        """
        x = self.P.current_coordinate_x
        y = self.P.current_coordinate_y
        level_map = self.P.level_map.level_map
        current_block = level_map[y][x]

        if not current_block.is_exit_block:
            return 0

        # play a sound to tell the player he successfully went through the door
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/door_unlock.wav"))

        # check which mode is currently on, if adventure mode then generate random level if solo mode, show end game
        # information
        if self.level_name:
            self.end_of_game()
        else:
            self.draw_level()

    def draw_level(self):
        """
        This method draws the next level using either the maze generator function or a level saved in files,
        depending on which mode is played.
        """
        level = LevelMap()

        # depending on the mode functions generate level or loads it from file
        if self.level_name:
            level.load_from_file(f"{os.getcwd()}/../resources/levels/{self.level_name}.txt")
        else:
            maze = MazeGenerator(width=LEVEL_WIDTH,
                                 height=LEVEL_HEIGHT)
            maze.add_objects("interactive_block", DESTRUCTIBLE_BLOCKS)
            maze.add_objects("coin", COINS)
            maze.save_to_file("tmp")
            level.load_from_file(f"{os.getcwd()}/../resources/levels/tmp.txt")

        block_size = int(min(int(self.controller.width) / level.x_size,
                             (int(self.controller.height) - INFO_PANEL_SIZE) / level.y_size))

        # calculates coordinates of canvas origin because level may not always be a square
        if int(self.controller.width / level.x_size) == block_size:
            display_origin = (0, int((self.controller.height + INFO_PANEL_SIZE - block_size * level.y_size) / 2))
        else:
            display_origin = (int((self.controller.width - block_size * level.x_size) / 2),
                              int((self.controller.height + INFO_PANEL_SIZE - block_size * level.y_size) / 2))

        # passes display origin to canvas class because building blocks and players are drawn based on canvas origin
        self.canvas_origin = display_origin

        for row in level.level_map:
            for i in range(len(row)):
                row[i].draw(canvas=self,
                            size=block_size)

        # If player plays adventure mode we need to save number of total coins collected by him, therefore when this is
        # not the first level in adventure mode, number of so far collected coins are passed to player class
        if self.P:
            # if player already exists so he may have collected coins its number is passed to class
            self.P = Player(canvas=self,
                            level_map=level,
                            size=block_size,
                            coins_collected=self.P.coins_collected)
        else:
            self.P = Player(canvas=self,
                            level_map=level,
                            size=block_size)

    def end_of_game(self):
        """
        This method triggers the end of the game, allowing player to save his score to leaderboard and go back
        to main menu.
        """
        # Loading end game info
        end_game_image = ImageTk.PhotoImage(
            Image.open(f"{os.getcwd()}/../resources/graphics/end_game_info.png").resize((600, 480), Image.ANTIALIAS))
        self.create_image(340, 135, anchor="nw", image=end_game_image)
        self.images["end"] = end_game_image

        # Calculating final score
        score = max(0, self.P.coins_collected * 5 - TIME_LIMIT / 10 + DESTRUCTIBLE_BLOCKS)

        # Creating go back to menu button
        go_back_to_menu = CustomButton(master=self,
                                       image_path=f"{os.getcwd()}/../resources/graphics/buttons/go_back_to_menu_button.png",
                                       command=lambda: [self.controller.show_frame(GameMenu),
                                                        pygame.mixer.music.load(f"{os.getcwd()}/../resources/sounds/menu_ost.wav"),
                                                        pygame.mixer.music.set_volume(1),
                                                        pygame.mixer.music.play(loops=-1),
                                                        pygame.mixer.Channel(0).play(
                                                            pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])

        self.create_window(640, 540, window=go_back_to_menu)
        # Losing focus on Game Screen so player can't move
        go_back_to_menu.focus()

        # Drawing score
        numbers = list(str(int(score)))
        for i, number in enumerate(numbers):
            num_photo = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/numbers/{number}.png")
            # to prevent the image from being deleted by garbage collector we save it in dict.
            self.images["num" + str(i)] = num_photo
            self.create_image(640 + 27 * (i + 1 - len(numbers) / 2), 420, image=self.images["num" + str(i)], anchor='e')

        # Checking if current score is in top 9 and updating current leaderboard
        leaderboard = pd.read_csv(f"{os.getcwd()}/../resources/leaderboard/leaderboard.csv", header=None)
        leaderboard = leaderboard.append({0: self.player_name, 1: int(score)}, ignore_index=True)
        leaderboard.sort_values(by=1, inplace=True, ascending=False)
        leaderboard.iloc[:9, :].to_csv(f"{os.getcwd()}/../resources/leaderboard/leaderboard.csv", header=False, index=False)


class ModeChooser(tk.Canvas):
    """
    This abstract class manages the game mode selection screen when clicking start game in the main menu.
    It is a tkinter canvas and therefore inherits from tk.Canvas.

    # Attributes
    ___________
    controller: App class
        Refers back to the app class for control and interactions between tkinter widgets
    images: dict
        Dictionary of images displayed during some specific events

    # Methods
    ___________
    choose_levels(mode: int)
        creates a new window to enter player name, load level file if solo mode selected, and start game
    """
    def __init__(self,
                 parent,
                 controller):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        """
        self.controller = controller
        self.images = {}
        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height)

        # Creating button for adventure mode
        adv_mode = CustomButton(master=self,
                                image_path=f"{os.getcwd()}/../resources/graphics/buttons/adventure_mode_button.png",
                                command=lambda: self.choose_levels(mode=0))
        self.create_window(0, 0,
                           anchor="nw",
                           window=adv_mode)

        # Creating button for solo mode
        solo_mode = CustomButton(master=self,
                                 image_path=f"{os.getcwd()}/../resources/graphics/buttons/solo_mode_button.png",
                                 command=lambda: self.choose_levels(mode=1))
        self.create_window(controller.width / 2, 0,
                           anchor="nw",
                           window=solo_mode)

        # Creating exit button
        CustomButton.exit_button(self)

    def choose_levels(self,
                      mode: int):
        """
        Method to create a new window so that player can enter its name, load level from file if playing solo mode,
        and start game.

        # Parameters
        ____________
        :param mode: int,
            0 -> Adventure mode
            1 -> Solo mode
        """
        # Creating window on top of current window
        new_window = tk.Toplevel(self.controller)
        new_window.geometry("200x300")
        new_window.resizable(False, False)
        new_window.overrideredirect(True)
        self.controller.eval(f'tk::PlaceWindow {str(new_window)} center')

        # Creating canvas to place widgets there
        tmp_canvas = tk.Canvas(new_window, width=200, height=300, bg="black")
        tmp_canvas.pack()

        # Creating write player name info
        pl_name_image = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/texts/player_name.png")
        # to prevent the image from being deleted by garbage collector we save it in dict.
        self.images["player_name"] = pl_name_image
        tmp_canvas.create_image(100, 0, image=self.images["player_name"], anchor="n")

        # Creating entry widget with restrictions to 5 latin alphabet characters
        player_name = tk.StringVar()
        vcmd = (tmp_canvas.register(validate), '%P')
        ent = tk.Entry(tmp_canvas, validate="key", validatecommand=vcmd, textvariable=player_name)
        tmp_canvas.create_window(100, 52, anchor="n", window=ent)

        # If solo mode is clicked, adding option to choose level
        if mode:
            choose_level_img = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/texts/choose_level.png")
            # to prevent the image from being deleted by garbage collector we save it in dict.
            self.images["choose_level_img"] = choose_level_img
            tmp_canvas.create_image(100, 72, image=self.images["choose_level_img"], anchor="n")

            my_path = f"{os.getcwd()}/../resources/levels/"
            files_name = [f.replace('.txt', '') for f in listdir(my_path) if isfile(join(my_path, f))]

            # Setting default option of level
            lvl = tk.StringVar(new_window)
            lvl.set(files_name[0])
            lvl_menu = tk.OptionMenu(tmp_canvas, lvl, *files_name)
            tmp_canvas.create_window(100, 124, anchor="n", window=lvl_menu)

        # Creating Start Game Button
        start_game = CustomButton(master=tmp_canvas,
                                  image_path=f"{os.getcwd()}/../resources/graphics/buttons/start_game_button.png",
                                  command=lambda: [self.controller.show_frame(GameScreen,
                                                                              level_name=lvl.get() if mode else None,
                                                                              player_name=player_name.get()),
                                                   new_window.destroy()])
        tmp_canvas.create_window(100, 174,
                                 anchor="n",
                                 window=start_game)

        # Creating Close Button
        close_button = CustomButton(master=tmp_canvas,
                                    image_path=f"{os.getcwd()}/../resources/graphics/buttons/exit_button.png",
                                    command=lambda: [new_window.destroy(),
                                                     pygame.mixer.Channel(0).play(pygame.mixer.Sound(
                                                       f"{os.getcwd()}/../resources/sounds/button.wav"))])
        tmp_canvas.create_window(100, 224,
                                 anchor="n",
                                 window=close_button)


class LevelGenerator(tk.Canvas):
    """
    This abstract class manages the level generator screen when clicking generate level in the main menu.
    It is a tkinter canvas and therefore inherits from tk.Canvas.

    # Attributes
    ___________
    controller: App class
        Refers back to the app class for control and interactions between tkinter widgets
    images: dict
        Dictionary of images displayed during some specific events
    canvas_origin: tuple
        Coordinates of the origin of the canvas
    P: Player class
        An instance of a player class
    current_values: dict
        Dictionary containing current setting values for level to be generated
    increments: dict
        Dictionary containing increment steps for when clicking on the arrows to modify a setting value
    limit_values: dict
        Dictionary containing limit values on the setting values

    # Methods
    ___________
    save()
        saves level to file
	add_option(x:int, y:int, text_name:str, increment_step:int)
		adds option on canvas
	update_numbers(self, number_str: str, x: int, y: int, option_name: str)
		transforms numerical setting value into graphical display
	change(self, button_name: str, by: int, x: int, y: int)
		modifies setting numerical value
	generate_and_display()
		runs the generation algorithm and displays the result
    """
    def __init__(self, parent, controller):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        """
        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height, bg='black')
        self.controller = controller
        self.images = {}
        self.P = None
        self.canvas_origin = None
        self.current_values = {"width": 9,
                               "height": 9,
                               "number_of_coins": 7,
                               "number_of_obstacles": 9}
        self.increments = {"width": 2,
                           "height": 2,
                           "number_of_coins": 1,
                           "number_of_obstacles": 1}
        self.limit_values = {"width_max": 51, "width_min": 9,
                             "height_max": 51, "height_min": 9,
                             "number_of_coins_max": 99, "number_of_coins_min": 0,
                             "number_of_obstacles_max": 99, "number_of_obstacles_min": 0}

        # it's an attribute of class co method can access it and properly display change of numbers
        self.space_between_buttons = (controller.height - (51 * 8 + 75)) / (len(self.current_values) + 3)

        # Create exit button
        CustomButton.exit_button(self)

        # Adding options to generate level
        for i, option_name in enumerate(self.current_values.keys()):
            self.add_option(x=PADDING_X,
                            y=75 + i * (51 + self.space_between_buttons),
                            text_name=option_name,
                            increment_step=self.increments[option_name])

        # Adding generate level button
        generate_lvl_button = CustomButton(master=self,
                                           image_path=f"{os.getcwd()}/../resources/graphics/buttons/generate_button.png",
                                           command=lambda: [self.generate_and_display(), pygame.mixer.Channel(0).play(
                                               pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])
        self.create_window(PADDING_X,
                           75 + (i + 1) * (51 + self.space_between_buttons),
                           anchor="nw",
                           window=generate_lvl_button)

        # Adding save level button
        save_button = CustomButton(master=self,
                                   image_path=f"{os.getcwd()}/../resources/graphics/buttons/save_button.png",
                                   command=lambda: [self.save(), pygame.mixer.Channel(0).play(
                                       pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])
        self.create_window(PADDING_X,
                           75 + (i + 2) * (51 + self.space_between_buttons),
                           anchor="nw",
                           window=save_button)

    @staticmethod
    def save():
        """
        Method to save the generated level in a file.
        A static method is used here because it does not depend on the object.
        """
        now = datetime.now()
        level_name = "gen_lvl_" + now.strftime("%d_%m_%Y_%H_%M_%S") + ".txt"
        src = str(os.getcwd()) + r"\..\resources\levels\tmp.txt"
        dst = str(os.getcwd()) + fr"\..\resources\levels\{level_name}"
        shutil.copyfile(src, dst)

    def add_option(self,
                   x: int,
                   y: int,
                   text_name: str,
                   increment_step: int):
        """
        Method used to add the different options and settings.

        # Parameters
        ____________
        :param x: int,
            x coordinate for option position on canvas
        :param y: int,
            y coordinate for option position on canvas
        :param text_name: str,
            option name
        :param increment_step: int
            increment step for that option
        """
        # Adding option description
        image = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/texts/{text_name}.png")
        # to prevent the image from being deleted by garbage collector we save it in dict.
        self.images[text_name] = image
        self.create_image(x, y, image=self.images[text_name], anchor="nw")

        # Adding increase button
        increase_button = CustomButton(master=self,
                                       image_path=f"{os.getcwd()}/../resources/graphics/buttons/increase_button.png",
                                       command=lambda: [self.change(button_name=text_name,
                                                                    by=increment_step,
                                                                    x=x,
                                                                    y=y),
                                                        pygame.mixer.Channel(0).play(
                                                            pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])
        self.create_window(x + 154,
                           y,
                           anchor="nw",
                           window=increase_button)
        # Adding decrease button
        decrease_button = CustomButton(master=self,
                                       image_path=f"{os.getcwd()}/../resources/graphics/buttons/decrease_button.png",
                                       command=lambda: [
                                           self.change(button_name=text_name, by=-increment_step, x=x, y=y),
                                           pygame.mixer.Channel(0).play(
                                               pygame.mixer.Sound(f"{os.getcwd()}/../resources/sounds/button.wav"))])
        self.create_window(x + 154,
                           y + 25,
                           anchor="nw",
                           window=decrease_button)

        # Displaying initial numbers
        self.update_numbers(number_str="{:02d}".format(self.current_values[text_name]),
                            x=x,
                            y=y,
                            option_name=text_name)

    def update_numbers(self,
                       number_str: str,
                       x: int,
                       y: int,
                       option_name: str):
        """
        Method used to transform the numerical setting values into graphical number displayed.

        # Parameters
        ____________
        :param number_str: str,
            string containing the current numerical value for the setting
        :param x: int,
            x coordinate for option position on canvas
        :param y: int,
            y coordinate for option position on canvas
        :param option_name: str,
            option name
        """
        dec = number_str[0]
        unity = number_str[1]
        n1 = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/numbers/{dec}.png")
        n2 = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/numbers/{unity}.png")
        # to prevent the image from being deleted by garbage collector we save it in dict..
        self.images[option_name + "_n1"] = n1
        self.images[option_name + "_n2"] = n2
        self.create_image(x + 100, y, image=self.images[option_name + "_n1"], anchor="nw")
        self.create_image(x + 127, y, image=self.images[option_name + "_n2"], anchor="nw")

    def change(self,
               button_name: str,
               by: int,
               x: int,
               y: int):
        """
        Method used to update different option/setting values.

        # Parameters
        ____________
        :param button_name: str,
            option name
        :param by: int,
            increment step by which to increase/decrease setting value
        :param x: int,
            x coordinate for option position on canvas
        :param y: int,
            y coordinate for option position on canvas
        """
        # Checks whether changed value will be still in limits
        if self.current_values[button_name] + by > self.limit_values[button_name + "_max"] or \
                self.current_values[button_name] + by < self.limit_values[button_name + "_min"]:
            return 0

        # Updating dictionary with values and displaying numbers
        self.current_values[button_name] = self.current_values[button_name] + by
        self.update_numbers(number_str="{:02d}".format(self.current_values[button_name]),
                            x=x,
                            y=y,
                            option_name=button_name)

    def generate_and_display(self):
        """
        Method used to call the maze generating function with current settings and generate level.
        Level is also drawn and displayed on the side of the screen.
        """
        maze = MazeGenerator(width=self.current_values["width"],
                             height=self.current_values["height"])
        # Checking whether number of additional objects is not higher than maximal additional object that can
        # be added to level.
        if self.current_values["number_of_obstacles"] + self.current_values["number_of_coins"] > \
                maze.max_additional_objects:
            self.current_values["number_of_obstacles"] = min(self.current_values["number_of_obstacles"],
                                                             maze.max_additional_objects)
            self.current_values["number_of_coins"] = max(
                maze.max_additional_objects - self.current_values["number_of_obstacles"], 0)
            self.update_numbers(number_str="{:02d}".format(self.current_values["number_of_obstacles"]),
                                x=PADDING_X,
                                y=75 + 3 * (51 + self.space_between_buttons),
                                option_name="number_of_obstacles")
            self.update_numbers(number_str="{:02d}".format(self.current_values["number_of_coins"]),
                                x=PADDING_X,
                                y=75 + 2 * (51 + self.space_between_buttons),
                                option_name="number_of_coins")

        # Adding special blocks to level
        if self.current_values["number_of_obstacles"] > 0:
            maze.add_objects("interactive_block", self.current_values["number_of_obstacles"])
        if self.current_values["number_of_coins"] > 0:
            maze.add_objects("coin", self.current_values["number_of_coins"])

        # Saving file as tmp.txt and loading it
        maze.save_to_file("tmp")
        level = LevelMap()
        level.load_from_file(f"{os.getcwd()}/../resources/levels/tmp.txt")

        left_panel_size = 181 + 2 * PADDING_X

        # Resetting Display
        self.create_rectangle((left_panel_size, 0, self.controller.width, self.controller.height),
                              fill="black",
                              width=0)

        block_size = int(
            min((self.controller.width - left_panel_size) / level.x_size, self.controller.height / level.y_size))

        # calculates coordinates of canvas origin
        if int(self.controller.height / level.y_size) == block_size:
            display_origin = (int((left_panel_size + self.controller.width - block_size * level.x_size)) / 2, 0)
        else:
            display_origin = (left_panel_size, int((self.controller.height - block_size * level.y_size) / 2))

        self.canvas_origin = display_origin

        # Displaying level
        for row in level.level_map:
            for i in range(len(row)):
                row[i].draw(canvas=self,
                            size=block_size)

        # Drawing player
        self.P = Player(canvas=self,
                        level_map=level,
                        size=block_size)


class Leaderboard(tk.Canvas):
    """
    This abstract class manages the leaderboard when clicking leaderboard in the main menu.
    It is a tkinter canvas and therefore inherits from tk.Canvas.

    # Attributes
    ___________
    controller: App class
        Refers back to the app class for control and interactions between tkinter widgets
    images: dict
        Dictionary of images displayed during some specific events

    # Methods
    ___________
    draw_position(position: int, y:int)
        Draws the ranking position of the player in the leaderboard
    draw_name(position: int, name: str, y:int
        Draws the name of the player in the leaderboard
    draw_score(position: int, score: int, y:int
        Draws the name of the player in the leaderboard
    """
    def __init__(self, parent, controller):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        """
        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height)
        # Creating background
        bg = ImageTk.PhotoImage(
            Image.open(f"{os.getcwd()}/../resources/graphics/leaderboard_tab.png").resize((controller.width, controller.height),
                                                                             Image.ANTIALIAS))
        self.create_image(0, 0, anchor="nw", image=bg)
        self.images = {"bg": bg}
        self.controller = controller

        # Creating exit button
        CustomButton.exit_button(self)

        # Loading and displaying leaderboard
        leaderboard = pd.read_csv(f"{os.getcwd()}/../resources/leaderboard/leaderboard.csv", header=None)
        for position, row in leaderboard.iterrows():
            y = 7 * 25 + 60 * position
            self.draw_position(position=position + 1, y=y)
            self.draw_name(position=position + 1, name=row[0], y=y)
            self.draw_score(position=position + 1, score=row[1], y=y)

    def draw_position(self,
                      position: int,
                      y: int):
        """
        Method to draw the ranking position of the player on the Leaderboard canvas.

        # Parameters
        ____________
        :param position: int,
            Integer representing the ranking on the leaderboard
        :param y: int,
            Y coordinate to position player score on canvas
        """
        image = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/numbers/{str(position)}.png")
        # to prevent the image from being deleted by garbage collector we save it in dict.
        self.images[position] = image
        self.create_image(250, y, image=self.images[position], anchor="nw")

    def draw_name(self,
                  position: int,
                  name: str,
                  y: int):
        """
        Method to draw the player name on the Leaderboard canvas.

        # Parameters
        ____________
        :param position: int,
            Integer representing the ranking on the leaderboard
        :param name: str,
            Player name
        :param y: int,
            Y coordinate to position player score on canvas
        """
        name = name.lower()
        for i, char in enumerate(name):
            image = ImageTk.PhotoImage(
                Image.open(f"{os.getcwd()}/../resources/graphics/characters/{char}.png").resize((51, 51), Image.ANTIALIAS))
            # to prevent the image from being deleted by garbage collector we save it in dict.
            self.images[char + str(position) + str(i)] = image
            self.create_image(500 + i * 51, y, image=self.images[char + str(position) + str(i)], anchor="nw")

    def draw_score(self,
                   position: int,
                   score: int,
                   y: int):
        """
        Method to draw the player score on the Leaderboard canvas.

        # Parameters
        ____________
        :param position: int,
            Integer representing the ranking on the leaderboard
        :param score: int,
            Player score
        :param y: int,
            Y coordinate to position player score on canvas
        """
        score = str(score)
        for i, num in enumerate(score):
            image = ImageTk.PhotoImage(Image.open(f"{os.getcwd()}/../resources/graphics/numbers/{num}.png"))
            # to prevent the image from being deleted by garbage collector we save it in dict..
            self.images[num + str(position) + str(i)] = image
            self.create_image(975 + i * 27, y, image=self.images[num + str(position) + str(i)], anchor="nw")


class Instruction(tk.Canvas):
    """
    This abstract class displays the instructions for the game when clicking instructions in the main menu.
    It is a tkinter canvas and therefore inherits from tk.Canvas.
    It also displays a narrative introduction to the game.

    # Attributes
    ___________
    controller: App class
        Refers back to the app class for control and interactions between tkinter widgets
    images: dict
        Dictionary of images displayed during some specific events
    """
    def __init__(self, parent, controller):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        """
        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height)
        bg = ImageTk.PhotoImage(
            Image.open(f"{os.getcwd()}/../resources/graphics/instruction_tab.png").resize((controller.width, controller.height),
                                                                             Image.ANTIALIAS))
        self.create_image(0, 0, anchor="nw", image=bg)
        self.controller = controller
        self.image = bg

        # Creating exit button
        CustomButton.exit_button(self)


class CustomButton(tk.Button):
    """
    This abstract class manages the button creation for other classes.
    It is a tkinter button and therefore inherits from tk.Button.
    """
    def __init__(self,
                 image_path: str,
                 *args,
                 **kwargs):
        """
        # Parameters
        ____________
        :param image_path: str,
            Contains the path to image used to represent button
        """
        photo = tk.PhotoImage(file=image_path)
        tk.Button.__init__(self, image=photo, *args, **kwargs)
        self.image = photo
        self['bg'] = 'black'
        self["activebackground"] = "black"
        self["border"] = 0

    @staticmethod
    def exit_button(master):
        """
        Method for the exit button, used often in the code.

        # Parameters
        ____________
        :param master: tkinter parent window,
            Refers to the tkinter widget on which to create the button
        """
        image_path = f"{os.getcwd()}/../resources/graphics/buttons/go_back_button.png"
        exit_button = CustomButton(master=master,
                                   image_path=image_path,
                                   command=lambda: [master.controller.show_frame(GameMenu),
                                                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(
                                                        f"{os.getcwd()}/../resources/sounds/button.wav"))])
        master.create_window(PADDING_X, 40, window=exit_button)
