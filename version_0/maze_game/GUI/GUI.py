import tkinter as tk
from gameplay.modules import *
from os import listdir
from os.path import isfile, join

# Constant varaibles
# latin alphabet is a set of possible characters in players name that have image in graphics directory
LATIN_ALPHABET = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
                  'u', 'w', 'x', 'y', 'z')
INFO_PANEL_SIZE = 80
# padding of exit button
PADDING_X = 40


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
	choose_level()
		opens up window to enter player name, load level from file and start game
    """
    def __init__(self):
        super().__init__()

        # Setting window configs
        self.width = 1280
        self.height = 720
        self.title('Maze game')
        self.geometry(str(self.width) + 'x' + str(self.height))
        self.resizable(False, False)
        self.images = {}

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

    def show_frame(self,
                   new_page,
                   level_name=None):
        """
        Method to display specific tkinter frame

        # Parameters
        ____________
        :param new_page: str,
            Name of the frame to display
        :param level_name: string
            When displaying GameScreen, carries the name of the level file to be loaded if playing solo mode
        """

        if new_page == "choose_level":
            self.choose_levels()
            return 0

        if new_page.__name__ == "GameScreen":
            # Initializing game with given level and player name
            tab = new_page(parent=self.container, controller=self, level_name=level_name)
        else:
            tab = new_page(parent=self.container, controller=self)

        # Removing currently shown tab
        if self.current_tab:
            self.current_tab.grid_remove()

        # Displaying desired tab
        self.current_tab = tab
        tab.grid(row=0, column=0, sticky="nsew")

    def choose_levels(self):
        """
        Method to create a new window so that player can enter its name, load level from file if playing solo mode,
        and start game.
        """
        # Creating window on top of current window
        new_window = tk.Toplevel(self)
        new_window.geometry("200x250")
        new_window.resizable(False, False)
        new_window.overrideredirect(True)
        self.eval(f'tk::PlaceWindow {str(new_window)} center')

        # Creating canvas to place widgets there
        tmp_canvas = tk.Canvas(new_window, width=200, height=300, bg="black")
        tmp_canvas.pack()

        # Creating information window to choose level
        choose_level_img = tk.PhotoImage(file=f"{os.getcwd()}/../resources/graphics/texts/choose_level.png")
        # to prevent the image from being deleted by garbage collector we save it in dict.
        self.images["choose_level_img"] = choose_level_img
        tmp_canvas.create_image(100, 20, image=self.images["choose_level_img"], anchor="n")

        my_path = f"{os.getcwd()}/../resources/levels/"
        files_name = [f.replace('.txt', '') for f in listdir(my_path) if isfile(join(my_path, f))]

        # Setting default option of level
        lvl = tk.StringVar(new_window)
        lvl.set(files_name[0])
        lvl_menu = tk.OptionMenu(tmp_canvas, lvl, *files_name)
        tmp_canvas.create_window(100, 74, anchor="n", window=lvl_menu)

        # Creating Start Game Button
        start_game = CustomButton(master=tmp_canvas,
                                  image_path=f"{os.getcwd()}/../resources/graphics/buttons/start_game_button.png",
                                  command=lambda: [self.show_frame(GameScreen,
                                                                   level_name=lvl.get()),
                                                   new_window.destroy()])
        tmp_canvas.create_window(100, 124,
                                 anchor="n",
                                 window=start_game)

        # Creating Close Button
        close_button = CustomButton(master=tmp_canvas,
                                    image_path=f"{os.getcwd()}/../resources/graphics/buttons/exit_button.png",
                                    command=lambda: new_window.destroy())
        tmp_canvas.create_window(100, 174,
                                 anchor="n",
                                 window=close_button)


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
        :param controller: App class,
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

        self.add_button(controller.width / 2, 5 * controller.height / 9, "start_game_button", "choose_level")
        self.add_button(controller.width / 2, 6 * controller.height / 9, "instruction_button", Instruction)
        self.add_button(controller.width / 2, 7 * controller.height / 9, "exit_button", "quit")

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
                               command=lambda: (quit() if function == "quit" else
                                                self.controller.show_frame(function)))
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
    action(event=None)
        manages player keyboard inputs
    check_if_next_level()
        checks if exit is reached
    draw_level()
        calls maze generating function to draw a new level. Also loads specific level if solo mode is selected
    end_of_game()
        triggers the end of the game
    """
    def __init__(self,
                 parent,
                 controller,
                 level_name=None):
        """
        # Parameters
        ____________
        :param parent: tkinter parent window,
            parent tkinter widget
        :param controller: App class,
            Refers back to the app class for control and interactions between tkinter widgets
        :param level_name: string
            Carries the name of the level file to be loaded if playing solo mode
        """
        self.controller = controller
        self.level_name = level_name
        self.images = {}
        self.canvas_origin = None
        self.P = None

        tk.Canvas.__init__(self, parent, width=controller.width, height=controller.height, bg='black')

        exit_button = CustomButton(master=self,
                                   image_path=f"{os.getcwd()}/../resources/graphics/buttons/go_back_button.png",
                                   command=lambda: controller.show_frame(GameMenu))

        self.create_window(PADDING_X, INFO_PANEL_SIZE / 2, window=exit_button)

        self.draw_level()
        self.focus_set()  # initially frame doesn't have focus so binding doesn't work without this part

        # Pause game functionality
        self.is_paused = False
        self.pause_label = tk.Label(self, text="GAME PAUSED", fg="dark red", bg="black", font="Helvetica 40 bold")

        # Binding keyboard
        self.bind('<Key>', self.action)

    def pause(self):
        """
        This method allows to pause the current game, simply switching a boolean variable on and off, unbinding
        keys so player can't move, as well as the music and the pause label.　
        """
        if self.is_paused:
            self.pause_label.place_forget()
            self.is_paused = False
        else:
            self.pause_label.place(relx=0.5, rely=0.5, anchor="center")
            self.is_paused = True

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
            elif event.char == "p":
                self.pause()

        # Check if after movement player found an exit
        if event.char in ["a", "d", "w", "s"]:
            self.check_if_next_level()

    def check_if_next_level(self):
        """
        This method checks if player has reached the exit of the level
        """
        x = self.P.current_coordinate_x
        y = self.P.current_coordinate_y
        level_map = self.P.level_map.level_map
        current_block = level_map[y][x]

        if not current_block.is_exit_block:
            return 0

        # show end game information
        self.end_of_game()

    def draw_level(self):
        """
        This method draws level chosen by player on a screen
        """
        level = LevelMap()

        # depending on the mode functions generate level or loads it from file
        level.load_from_file(f"{os.getcwd()}/../resources/levels/{self.level_name}.txt")

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

        # drawing BuildingBlocks
        for row in level.level_map:
            for i in range(len(row)):
                row[i].draw(canvas=self,
                            size=block_size)

        # Creates player on the level
        self.P = Player(canvas=self,
                        level_map=level,
                        size=block_size)

    def end_of_game(self):
        """
        This method triggers the end of the game information window
        """
        # Loading end game info
        end_game_image = ImageTk.PhotoImage(
            Image.open(f"{os.getcwd()}/../resources/graphics/end_game_info.png").resize((600, 480), Image.ANTIALIAS))
        self.create_image(340, 135, anchor="nw", image=end_game_image)
        self.images["end"] = end_game_image

        # Creating go back to menu button
        go_back_to_menu = CustomButton(master=self,
                                       image_path=f"{os.getcwd()}/../resources/graphics/buttons/go_back_to_menu_button.png",
                                       command=lambda: self.controller.show_frame(GameMenu))

        self.create_window(640, 540, window=go_back_to_menu)
        # Losing focus on Game Screen so player can't move
        self.is_paused = True
        go_back_to_menu.focus()


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
                                   command=lambda: master.controller.show_frame(GameMenu))
        master.create_window(PADDING_X, 40, window=exit_button)
