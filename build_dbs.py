from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from clinterface import multimenu
import os

engine = create_engine('sqlite:///food.db', echo=False)
Base = declarative_base()

class Dish(Base):
    """Dishes consist of ingredients. """
    __tablename__ = "dishes"
 
    id = Column(Integer, primary_key=True)
    name = Column(String)  
    # Foodtype: meat, fish, chicken, vege etc
    foodtype = Column(String)  
    # cookingmethod: stove, oven etc
    cookingmethod = Column(String)

    def addSingleDish(self, session):
        """Add a single dish manually from the command line"""
        os.system('cls' if os.name == 'nt' else 'clear')
        # Fill in the information about the Dish
        newdishmenu =  multimenu(validanswers={'c':'kana','f':'kala','v':'kasvis','m':'liha'})
        self.foodtype = newdishmenu.prompt_valid(definedquestion='Anna ruokalajin tyyppi', returnKey=False)
        self.cookingmethod = newdishmenu.prompt_valid(definedquestion='Anna valmistustapa',returnKey=False, redefinedAnswers={'o':'uuni', 's':'liesi'})
        self.name = input('Anna ruokalajin nimi:')
        # Add ingredients:
        newdishmenu.validanswers = {'n':'syötä seuraava aines', 'q': 'lopeta ainesten syöttäminen'}
        while newdishmenu.prompt_valid(definedquestion='Ruokalajiin tarvittavat ainekset:') == 'n':
            os.system('cls' if os.name == 'nt' else 'clear')
            thisIngredient = input('Anna ruoka-aineen nimi tai kirjoita sen osa:\n>')
            res = session.query(Ingredient).filter(Ingredient.name.like('%{}%'.format(thisIngredient))).all()
            #If there are ingredients in the database that match what the user wrote:
            if res:
                ingredientmenu = multimenu({})
                idx = 1
                for matchIngredient in res:
                    ingredientmenu.validanswers[str(idx)] = matchIngredient.name
                    idx += 1
                ingredientmenu.validanswers['c'] = 'Ei, lisää uusi aine'
                ingredientmenu.prompt_valid(definedquestion='Tarkoititko jotain näistä tietokannassa jo olevista aineista?')
                if ingredientmenu.answer != 'c':
                    thisIngredient = ingredientmenu.validanswers[ingredientmenu.answer]
            # add the Ingredient as a new db object
            self.ingredients.append(Ingredient(thisIngredient))
 

class Ingredient(Base):
    """Ingredients are linked to dishes by the linkid column"""
    __tablename__ = "ingredients"
 
    id = Column(Integer, primary_key=True)
    name = Column(String)  
    # If you want to clssify ingerdients some way
    iclass = Column(String)
    # Price is also optional
    price = Column(Float)
    #Link this table with the dishes table
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    dish = relationship("Dish", backref=backref("ingredients", order_by=id))
 
    def __init__(self, name):
        """initialize so that column names don't have to be specified"""
        self.name = name   

class MenuMeal(Base):
    """Dishes consist of ingredients. """
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True)
    day = Column(Date)  
    # Foodtype: meat, fish, chicken, vege etc
    mealtype = Column(String)  
    # cookingmethod: stove, oven etc
    dish_id = Column(Integer)
    dishname = Column(String)

# create tables
Base.metadata.create_all(engine)
