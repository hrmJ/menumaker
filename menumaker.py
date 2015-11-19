import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from build_dbs import Dish, Ingredient, MenuMeal
from clinterface import Menu, yesnomenu, multimenu
from menuobjects import Weekmenu, Day, Meal, Con, clearterm


class MainMenu:
    """This class includes all
    the comand line menu options and actions"""
    mainanswers = {    'n': 'Luo uusi ruokalista',
                       'q': 'Lopeta',
                       'a': 'Lisää uusi ruokalaji',
                       'v': 'Tarkastele ruokalajeja'}

    def __init__(self):
        self.menu = multimenu(MainMenu.mainanswers)
        # Selectable options:
        self.selectedwordset = 'none'
        self.selecteddb = 'none'
        #Control the program flow
        self.run = True

    def runmenu(self):
        'Run the main menu'
        clearterm()
        #Build the selected options
        self.menu.question = '''Tervetuloa MenuMaker -ohjelmaan.
                             {}
                             '''.format('\n'*2 + '-'*20 + '\n'*2)
        if Weekmenu.activemenu:
            Weekmenu.activemenu.printmenu()
            MainMenu.mainanswers['e'] = 'Muokkaa nykyistä menua'
            MainMenu.mainanswers['w'] = 'Kirjoita csv nykyisestä menusta'
            MainMenu.mainanswers['s'] = 'Tee ostoslista nykyisestä menusta'
        self.menu.validanswers = MainMenu.mainanswers
        self.menu.prompt_valid()
        self.MenuChooser(self.menu.answer)

    def viewdishes(self):
        res = Con.session.query(Dish).all()
        for dish in res:
            print(dish.name)
        input('...')

    def addDish(self):
        """Add a new dish to database"""
        #Con.loadSession()
        newdish = Dish()
        newdish.addSingleDish(Con.session)
        Con.session.add(newdish)
        Con.session.commit()

    def MenuChooser(self,answer):
        if answer == 'q':
            self.run = False
        elif answer == 'n':
            thismenu = Weekmenu()
        elif answer == 'e':
            Weekmenu.activemenu.editMenu()
        elif answer == 'v':
            self.viewdishes()
        elif answer == 'a':
            self.addDish()
        elif answer == 'w':
            Weekmenu.activemenu.printofile()
        elif answer == 's':
            Weekmenu.activemenu.BuildShoppingList()


menumaker = MainMenu()
while menumaker.run == True:
    menumaker.runmenu()
