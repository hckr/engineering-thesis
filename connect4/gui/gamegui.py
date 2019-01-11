# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font

from . import simpl10n as l10n
from .configfile import get_config
from .imageimporter import import_images
from .simpl10n import translate as _

IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'images')
DEFAULT_CHIP_SIZE = 45


class GameGUI:
    def __init__(self, game_controller, title, rows, cols, chip_size):
        self.game_controller = game_controller
        self.title = title
        self.rows = rows
        self.cols = cols
        self.chip_size = chip_size
        self.bound_events = None

    def start(self, pos=None):
        root = tk.Tk()
        root.title(self.title)
        root.resizable(False, False)
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        width = self.cols * (self.chip_size + 3) + 1
        height = self.rows * (self.chip_size + 3) + 1
        if pos is None:
            pos_x = (screen_w / 2) - (width / 2)
            pos_y = (screen_h / 2) - (height / 2)
        else:
            pos_x, pos_y = pos
        root.geometry('%dx%d+%d+%d' % (width, height, pos_x, pos_y))

        menubar = tk.Menu(root)
        
        gamemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label=_('Game'), menu=gamemenu)
        gamemenu.add_command(label=_('New game'), command=self.game_controller.on_new_game, accelerator='F2')
        root.bind('<F2>', self.game_controller.on_new_game)
        gamemenu.add_command(label=_('Restart game'), command=self.game_controller.on_restart_game, accelerator='F3')
        root.bind('<F3>', self.game_controller.on_restart_game)
        gamemenu.add_command(label=_('Quit'), command=self.quit, accelerator='Alt+F4')
        
        optionsmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label=_('Options'), menu=optionsmenu)
        languagemenu = tk.Menu(menubar, tearoff=False)
        optionsmenu.add_cascade(label=_('Language'), menu=languagemenu)
        tk_str_lang_code = tk.StringVar()
        tk_str_lang_code.set(self.game_controller.get_current_lang())
        for lang_code, lang_name in l10n.AVAILABLE_LANGS.items():
            languagemenu.add_radiobutton(
                label=lang_name, variable=tk_str_lang_code, value=lang_code,
                command=lambda: self.game_controller.set_lang_and_restart_gui(
                    tk_str_lang_code.get()
                )
            )
        chipsizemenu = tk.Menu(menubar, tearoff=False)
        optionsmenu.add_cascade(label=_('Chip size'), menu=chipsizemenu)
        tk_int_chip_size = tk.IntVar()
        tk_int_chip_size.set(get_config('chip_size', DEFAULT_CHIP_SIZE))
        for chip_size in (45, 60, 85, 100):
            chipsizemenu.add_radiobutton(
                label=str(chip_size), variable=tk_int_chip_size, value=chip_size,
                command=lambda: self.game_controller.set_chip_size_and_restart_gui(
                    tk_int_chip_size.get()
                )
            )
        
        
        algomenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label=_('Algorithm'), menu=algomenu)
        tk_bool_learning = tk.BooleanVar()
        tk_bool_exploration = tk.BooleanVar()
        algomenu.add_checkbutton(label=_('Learning'), onvalue=True, offvalue=False, variable=tk_bool_learning,
                                    command=lambda: setattr(self.game_controller, 'learning', tk_bool_learning.get()))
        algomenu.add_checkbutton(label=_('Exploration'), onvalue=True, offvalue=False, variable=tk_bool_exploration,
                                    command=lambda: self.game_controller.set_exploration(tk_bool_exploration.get()))
        
        helpmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label=_('Help'), menu=helpmenu)
        helpmenu.add_command(label=_('About'), command=self.show_about_window, accelerator='F1')
        root.bind('<F1>', self.show_about_window)
        root.config(menu=menubar)

        images = import_images(os.path.join(IMAGES_DIR, 'chip_*.png'), self.chip_size)
        transparent_images = import_images(os.path.join(IMAGES_DIR, 'chip_*.png'), self.chip_size, 150)
        self.players_images = {
            1: {
                'normal': images['chip_blue'],
                'transparent': transparent_images['chip_blue']
            },
            2: {
                'normal': images['chip_red'],
                'transparent': transparent_images['chip_red']
            }
        }
        self.board = GameBoardGUI(root, self.rows, self.cols, self.players_images, self.chip_size)
        self.rebind_events()
        self.refresh_board()
        self.root = root
        self.board.mainloop()

    def restart(self):
        old_pos = [ int(x) for x in self.root.winfo_geometry().split('+')[1:] ]
        self.root.destroy()
        self.start(old_pos)

    def quit(self, *args):
        self.root.destroy()
        exit()

    def refresh_board(self, suggestion=None):
        board_state = self.game_controller.get_board_state()
        if board_state is not None:
            self.board.refresh(board_state.board, suggestion)

    def bind_events(self, *args):
        self.board.bind_events(*args)
        self.bound_events = args

    def rebind_events(self):
        if self.bound_events is not None:
            self.bind_events(*self.bound_events)

    def unbind_events(self):
        self.board.unbind_events()
        self.bound_events = None

    def pos_x_to_col(self, pos_x):
        col = int(pos_x / self.board.field_size)
        if col < self.cols:
            return col
        return self.cols - 1

    def last_mouse_pos_x(self):
        return self.board.last_mouse_pos_x

    def select_players(self, options, callback):
        root = self.root
        dialog = tk.Toplevel(root)
        dialog.title(_('New game'))
        body = tk.Frame(dialog)
        body.pack()
        pos_x = root.winfo_rootx() - 100
        pos_y = root.winfo_rooty()
        dialog.geometry("+%d+%d" % (pos_x, pos_y))
        font = Font(size=15)
        tk.Label(body, text=_('Player') + ' 1', font=font, image=self.players_images[1]['transparent'],
                 compound=tk.CENTER).grid(row=0, column=0)
        tk.Label(body, text=_('Player') + ' 2', font=font, image=self.players_images[2]['transparent'],
                 compound=tk.CENTER).grid(row=0, column=1)
        p1_var = tk.StringVar(value=options[0])
        p1_opt = tk.OptionMenu(body, p1_var, *options)
        p1_opt.configure(width=40)
        p1_opt.grid(row=1, column=0)
        p2_var = tk.StringVar(value=options[1] if len(options) > 1 else options[0])
        p2_opt = tk.OptionMenu(body, p2_var, *options)
        p2_opt.configure(width=40)
        p2_opt.grid(row=1, column=1)

        def button_command():
            dialog.destroy()
            callback(options.index(p1_var.get()), options.index(p2_var.get()))

        tk.Button(body, text=_('Start game'), command=button_command).grid(row=2, column=0, columnspan=2)
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()

    @staticmethod
    def show_info(title, text):
        messagebox.showinfo(title, text)

    def show_about_window(self, *args):
        self.show_info(_('About'), _('about_text'))


class GameBoardGUI(tk.Frame):
    def __init__(self, parent, rows, cols, players_images, chip_size):
        tk.Frame.__init__(self, parent)
        self.players_images = players_images
        canvas = tk.Canvas(width=(chip_size + 3) * cols, height=(chip_size + 3) * rows)
        canvas.pack()
        self.canvas = canvas
        self.rows = rows
        self.cols = cols
        self.chip_size = chip_size
        self.field_size = chip_size + 3
        self.last_mouse_pos_x = None

    def refresh(self, board_state, suggestion=None):
        self.canvas.delete('all')
        for row in range(0, self.rows, 2):
            self.canvas.create_rectangle(
                0,
                row * self.field_size,
                self.field_size * self.cols,
                (row + 1) * self.field_size,
                width=1
            )
        for col in range(0, self.cols, 2):
            self.canvas.create_rectangle(
                col * self.field_size,
                0,
                (col + 1) * self.field_size,
                self.field_size * self.rows,
                width=1
            )
        for row in range(self.rows):
            for col in range(self.cols):
                player_id = board_state[row][col]
                if player_id is not None:
                    self.canvas.create_image(
                        (
                            (col + 0.5) * self.chip_size + 3 * (col + 1) - 2,
                            (row + 0.5) * self.chip_size + 3 * (row + 1) - 2
                        ),
                        image=self.players_images[player_id]['normal']
                    )
        if suggestion is not None:
            self.canvas.create_image(
                (
                    (suggestion['col'] + 0.5) * self.chip_size + 3 * (suggestion['col'] + 1) - 2,
                    (suggestion['row'] + 0.5) * self.chip_size + 3 * (suggestion['row'] + 1) - 2
                ),
                image=self.players_images[suggestion['player_id']]['transparent']
            )
        self.canvas.update()

    def bind_events(self, mousemove, clickend):
        def on_move(event):
            self.last_mouse_pos_x = event.x
            mousemove(self.last_mouse_pos_x)

        def on_click_end(event):
            if self.last_mouse_pos_x:
                clickend(self.last_mouse_pos_x)

        self.canvas.bind('<Motion>', on_move)
        self.canvas.bind('<ButtonRelease-1>', on_click_end)

    def unbind_events(self):
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
