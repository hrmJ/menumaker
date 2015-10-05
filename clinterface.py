#! /usr/bin/env python

class Menu:
    """Any command line menus that are used to ask the user for input"""
    def prompt_valid(self, reverseorder=False, definedquestion='',allowlong=False,returnKey=True,redefinedAnswers=False):
            if definedquestion:
                self.question = definedquestion
            if redefinedAnswers:
                self.validanswers = redefinedAnswers
            #Make a printable string from the dict:
            options = '\n                '.join("{!s}: {!s}".format(key,val) for (key,val) in sorted(self.validanswers.items()))
            question = "{}\n{}{}\n>".format(self.question,'                ',options)
            if reverseorder:
                options = '\n               '.join("{!s}: {!s}".format(key,val) for (key,val) in sorted(self.validanswers.items()))
                question = "{}{}\n\n\n{}\n>".format('\n               ', options, self.question)
            self.answer=input(question)
            while self.answer not in self.validanswers.keys():
                if allowlong and len(self.answer) > 3:
                    break
                self.answer = input("Please give a valid answer.\n {}".format(question))
            if returnKey:
                return self.answer
            else:
                return self.validanswers[self.answer]

    def prompt(self):
            #Make a printable string from the dict:
            question = "{}".format(self.question)
            self.answer=input(question)

class yesnomenu(Menu):
    validanswers = { 'y':'yes','n':'no' }
    def __init__(self, question = ''):
        self.question = question


class multimenu(Menu):
    '''Create a menu object that has the possible values listed as a dictionary,
    where the keys represent answers and the values represent explanations of each answer'''
    def __init__(self, validanswers,promptnow=''):
        self.validanswers=validanswers
        if promptnow:
            self.question = promptnow
            self.prompt_valid()

class freemenu(Menu):
    def __init__(self, question):
        self.question = question

