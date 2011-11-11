'''
Created on 28 Sep 2011

@author: poutima
'''

import logging
from SrcMember import *

class SrcFile(object):
    '''
    Holds information for one file that misses at least one type of documentation 
    according to the error log produced by Doxygen.
    '''
    
    @property
    def members(self):
        ''' Returns the list of members. '''
        return self.__members
    
    @property
    def classes(self):
        ''' Returns the list of classes. '''
        return self.__classes
    
    @property
    def name(self):
        ''' Returns the name of this file. '''
        return self.__name
    
    # Public functions
    def addUncommentedMember(self, memberName, memberType, missing):
        ''' Adds an uncommented member to the __members dictionary. '''
        if str(memberName) not in self.__members:
            if memberType == "function":
                self.__addFunc(memberName)
                member = self.__members[memberName]
            else:
                member = SrcMember(memberName, memberType, missing)
        else:
            member = self.__members[memberName]
        
        member.isMissing = True    
        self.__members[memberName] = member

    def addUncommentedClassMember(self, className, memberName, memberType, missing):
        ''' Adds a uncommented class to the __classes dictionary. '''
        if str(className) not in self.__classes:
            self.__addClass(str(className))
        
        if memberType == 'function':
            member = SrcFunction(memberName, missing)
        else:
            member = SrcMember(memberName, memberType, missing)
        
        exists = False
        
        for m in self.__classes[className].parameters:
            if m == memberName:
                exists = True
                
        if exists == False:
            self.__classes[className].addParameter(member)
    
    def addUncommentedParameter(self, functionName, paramName):
        ''' Adds an uncommented parameter to the function missing it. '''
        if str(functionName) not in self.__members:
            self.__addFunc(str(functionName))
        
        exists = False

        # For some reason Doxygen reports some missing __parameters more than one time
        func = self.__members[functionName]
        params = func.parameters
        try:
            for f in params:
                if paramName in f:
                    exists = True
        except AttributeError:
            logging.error('AttributeError')
        
        if exists == False:
            try:
                self.__members[functionName].addMissingParameter(paramName)
            except AttributeError:
                pass
    def addUncommentedReturnValue(self, filename, functionName):
        ''' 
        Turns on the notification that the given function is missing
        comments about the return value.
        '''
        
        if str(functionName) not in self.__members:
            self.__addFunc(str(functionName))
        
        member = self.__members[functionName]
        member.returnValueMissing = True
            
    # Private functions            
    def __addFunc(self, functionName):
        ''' Adds a new function to the __members dictionary. '''
        if functionName not in self.__members:
            #self.__funcs[functionName] = SrcFunction(functionName)
            self.__members[functionName] = SrcFunction(functionName)

    def __addClass(self, className):
        ''' Adds a new class to the __classes dictionary. '''
        if className not in self.__classes:
            self.__classes[className] = SrcMember(className, "class")
        
    def __init__(self, filename):
        '''
        Constructor
        '''
        self.__name = str(filename)
        # __members is an array holding all the uncommented members. This also includes uncommented functions.
        self.__members = {}
        # The classes that have missing members. Classes are defined as they are by Doxygen, so any lines
        # where Doxygen uses the word "class" is considered part of this.
        self.__classes = {}
