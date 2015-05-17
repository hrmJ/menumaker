import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from build_dbs import Dish, Ingredient, MenuMeal
from clinterface import Menu, yesnomenu, multimenu
import codecs
import csv

def clearterm():
    #Clear the terminal:
    os.system('cls' if os.name == 'nt' else 'clear')

class Weekmenu:
    """menu that consists of days"""
    activemenu = False
    def __init__(self):
        self.days = list()
        self.startdate = ""
        self.enddate = ""
        clearterm()
        self.days.append(Day(askDate()))
        self.printmenu()
        #Insert more days:
        insertmore = multimenu({'n':'Syötä seuraava päivä','f':'lopeta listan teko'})
        insertmore.question='{}Jatketaanko?'.format('\n'*3)
        insertmore.prompt_valid()
        while insertmore.answer == 'n':
            clearterm()
            self.printmenu()
            self.days.append(Day(self.getNextDate()))
            clearterm()
            self.printmenu()
            insertmore.prompt_valid()
        #Make this menu the current menu 
        Weekmenu.activemenu = self
        self.WriteToDb()

    def getNextDate(self):
        """increment the day counter"""
        return self.days[-1].date + datetime.timedelta(days=1)


    def printmenu(self,startday=0,endday=False):
        """Prints a command line table showing the menu day by day"""
        clearterm()
        #Make a list of lunch + dinner combinations to print them as columns of table
        mealnames = ['Lounas', 'Päivällinen']
        lengthOfLongest = len(max(mealnames, key=len)) + 1
        lunchstring = ['{0:{width}}|'.format(mealnames[0],width=lengthOfLongest)]
        dinnerstring = ['{0:{width}}|'.format(mealnames[1],width=lengthOfLongest)]
        datestring = ['{0:{width}}|'.format('',width=lengthOfLongest)]
        if not endday:
            daystoprint = self.days[startday:]
        else:
            daystoprint = self.days[startday:endday]
        for day in daystoprint:
            lengthOfLongest = len(max([day.lunch.dish, day.dinner.dish, formatDateString(day.date)], key=len))
            #Build a string of dates
            datestring.append('{date:{width}} | '.format(date=formatDateString(day.date),width=lengthOfLongest))
            #Build a string of lunch names
            lunchstring.append('{lunch:{width}} | '.format(lunch=day.lunch.dish,width=lengthOfLongest))
            #Build a string of dinner names
            dinnerstring.append('{dinner:{width}} | '.format(dinner=day.dinner.dish,width=lengthOfLongest))
        #Transform the lists into a format string object
        daterow  = '{}'*len(datestring)
        lunchrow  = '{}'*len(lunchstring)
        dinnerrow = '{}'*len(dinnerstring)
        #Print the strings as a table
        print(daterow.format(*datestring))
        print('*'*len(dinnerrow.format(*dinnerstring)))
        print(lunchrow.format(*lunchstring))
        print('='*len(dinnerrow.format(*dinnerstring)))
        print(dinnerrow.format(*dinnerstring))
        print('\n'*3)

    def editMenu(self):
        """Edit some of the meals in the menu"""
        self.printmenu()
        datesofdays = dict()
        #Create answers for a cl menu
        for idx, day in enumerate(self.days):
            datesofdays[str(idx)] = formatDateString(day.date)
        daypicker = multimenu(datesofdays)
        daypicker.question = 'Valitse päivä, jonka ateriaa/aterioita haluat muokata:'
        daypicker.prompt_valid()
        pickedDay = int(daypicker.answer)
        #Ask which meal:
        self.printmenu(pickedDay,pickedDay+1)
        mealpicker = multimenu({'1':'Lounas','2':'Päivällinen'})
        mealpicker.question = 'Kumpaa ateriaa muokataan?'
        mealpicker.prompt_valid()
        if mealpicker.answer == '1':
            self.days[pickedDay].lunch = Meal('lounas')
        else:
            self.days[pickedDay].dinner = Meal('päivällinen')

    def printofile(self):
        """Print the menu to a text file"""
        dates = ['']
        lunches = ['Lounas']
        dinners = ['Päivällinen']
        for day in self.days:
            dates.append(formatDateString(day.date))
            lunches.append(day.lunch.dish)
            dinners.append(day.dinner.dish)
        csvlist = [dates,lunches,dinners]
        filename = 'ruokalista{}_{}-{}_{}.csv'.format(self.days[0].date.day,self.days[0].date.month,
                                            self.days[-1].date.day,self.days[-1].date.month)
        with open(filename,'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(csvlist)
        input('Ruokalista kirjoitettiin tiedostoon ' + filename)


    def WriteToDb(self):
        """Write the menu to the database"""
        #delete these dates if in the meal database
        session = createsession()
        #WHY do I have to reduce 1 from start date?
        query = session.query(MenuMeal).filter(MenuMeal.day.between(self.days[0].date - datetime.timedelta(days=1), self.days[-1].date))
        res = query.all()
        for row in res:
            session.delete(row)
        session.commit()
        #Make a new sqlalchemy session for this
        session = createsession()
        #Insert all the meals from this menu to db
        newmeals = list()
        for day in self.days:
            session.add(MenuMeal(day=day.date,dishname=day.lunch.dish,mealtype='lunch'))
            session.add(MenuMeal(day=day.date,dishname=day.dinner.dish,mealtype='dinner'))
        session.commit()


    def BuildShoppingList(self):
        """Write the menu to the database"""
        #Make a new sqlalchemy session for this
        session = createsession()
        #Get all the distinct dishnames to a list
        query = session.query(MenuMeal.dishname).filter(MenuMeal.day.between(self.days[0].date - datetime.timedelta(days=1), 
                                                        self.days[-1].date)).distinct()
        res = query.all()
        dishnames = list()
        for row in res:
            dishnames.append(row.dishname)
        #Get all the ingredients that these dishes take, also distinctly
        subquery = session.query(Dish.id).filter(Dish.name.in_(dishnames)).subquery()
        query = session.query(Ingredient.name).filter(Ingredient.dish_id.in_(subquery)).distinct()
        res = query.all()
        #Make these a shopping list
        self.shoppinglist=list()
        needthis = yesnomenu()
        for row in res:
            needthis.prompt_valid(definedquestion = 'Tarvitaanko kaupasta: {}?'.format(row.name))
            if needthis.answer == 'y':
                self.shoppinglist.append([row.name])
        #Write the list to a file
        filename = '/home/juho/Dropbox/koti/ostoslista.txt'
        with open(filename,'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(self.shoppinglist)
        input('Ostoslista kirjoitettiin tiedostoon ' + filename)


class Day:
    """A day contains two meals"""
    def __init__(self, date):
        # The date attribute is a tuple with a date object as itse first and a string as its second value
        self.date = date
        print('{}\n{}'.format(formatDateString(date),'*'*20))
        self.lunch = Meal('lounas')
        self.dinner = Meal('päivällinen')


class Meal:
    #self.dish
    #self.foodtype
    #self.cookingmethod
    def __init__(self, mealtype):
        """Create a new meal"""
        self.mealtype = mealtype
        print(mealtype + ":")
        viewmenu = multimenu({'1':'Tarkastele tämän ruokalistan ruokia',
                              'a':'Tarkastele kaikkia tietokannan ruokia',
                              'f':'Tarkastele kalaruokia',
                              'c':'Tarkastele kanaruokia',
                              'm':'Tarkastele liharuokia',
                              'v':'Tarkastele kasvisruokia',
                              's':'Tarkastele liedellä valmistettavia',
                              'o':'Tarkastele uunissa valmistettavia',
                              'e':'Ehdota'
                              })
        viewmenu.question = 'Haluatko tutkia tietokantaa? (Voit myös kirjoittaa suoraan vastauksen)'
        viewmenu.prompt_valid(allowlong=True)
        if viewmenu.answer == 'a':
            self.viewdb(foodtype='all')
        elif viewmenu.answer == 'f':
            self.viewdb(foodtype='kala')
        elif viewmenu.answer == 'c':
            self.viewdb(foodtype='kana')
        elif viewmenu.answer == 'm':
            self.viewdb(foodtype='liha')
        elif viewmenu.answer == 'v':
            self.viewdb(foodtype='kasvis')
        elif viewmenu.answer == 's':
            self.viewdb(cookingmethod='liesi')
        elif viewmenu.answer == 'o':
            self.viewdb(cookingmethod='uuni')
        #If a longer string is provided by the user
        else:
            self.dish = viewmenu.answer

    def viewdb(self,foodtype='all',cookingmethod='all'):
        """View the dishes in the database filtered by some criteria and choose one of them"""
        #Evaluate the criteria
        if foodtype == 'all' and cookingmethod == 'all':
            res = Con.session.query(Dish).all()
        elif cookingmethod == 'all':
            query = Con.session.query(Dish).filter(Dish.foodtype == foodtype)
            res = query.all()
        else:
            input(cookingmethod)
            query = Con.session.query(Dish).filter(Dish.cookingmethod == cookingmethod)
            res = query.all()
        #Build a list of results
        dishoptions = dict()
        for idx, dish in enumerate(res):
            dishoptions[str(idx)]=dish.name
        dishoptions['w'] = 'Kirjoita itse'
        dishmenu = multimenu(dishoptions)
        dishmenu.question = 'Valitse {} vaihtoehdoista tai kirjoita itse painamalla w.'.format(self.mealtype)
        dishmenu.prompt_valid(True)
        if dishmenu.answer == 'w':
            self.dish = input("Anna {}:\n>".format(self.mealtype))
        else:
            self.dish = res[int(dishmenu.answer)].name

    def chooseByType(self,foodtype):
        """View all the dishes in the database and choose one of them"""
        res = Con.session.query(Dish).all()
        query = session.query(Dish).filter(Dish.foodtype == foodtype)
        dishoptions = dict()
        for idx, dish in enumerate(res):
            dishoptions[str(idx)]=dish.name
        dishoptions['w'] = 'Kirjoita itse'
        dishmenu = multimenu(dishoptions)
        dishmenu.question = 'Valitse {} vaihtoehdoista tai kirjoita itse painamalla w.'.format(self.mealtype)
        dishmenu.prompt_valid(True)
        if dishmenu.answer == 'w':
            self.dish = input("Anna {}:\n>".format(self.mealtype))
        else:
            self.dish = res[int(dishmenu.answer)].name

class Con:
    engine = create_engine('sqlite:///food.db', echo=False)
    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

def createsession():
    """Create a temporal session object"""
    engine = create_engine('sqlite:///food.db', echo=False)
    # create a Session
    Session = sessionmaker(bind=engine)
    return Session()

def printalldishes():
    pass

def askDate():
    """Ask the user to give a date"""
    askedDays = list()
    thisday = datetime.datetime.today()
    dayanswers = dict()
    for i in range(3):
        askedDays.append(thisday)
        dayanswers[str(i)] = formatDateString(thisday)
        thisday += datetime.timedelta(days=1)
    dayanswers['o'] = 'Jokin muu päivä'
    daymenu = multimenu(dayanswers)
    daymenu.prompt_valid(False, 'Valitse listan ensimmäinen päivä')
    #Return the date object
    return  askedDays[int(daymenu.answer)]

def formatDateString(thisday):
    weekdays = {0:'Ma',1:'ti',2:'ke',3:'to',4:'pe',5:'la',6:'su'}
    return '{} {}.{}.{}'.format(weekdays[thisday.weekday()], thisday.day, thisday.month, thisday.year)


#res = Con.session.query(Ingredient).filter(Ingredient.dish_id==2).all()
