from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

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
