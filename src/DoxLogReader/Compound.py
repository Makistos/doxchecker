'''
Created on 25 Oct 2011

@author: poutima
'''

from abc import ABCMeta

from SrcMember import SrcMember, SrcFunction

class Compound(object):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @property
    def compoundType(self):
        return self.__compoundType
    
    @property 
    def isMissing(self):
        return self.__isMissing

    @isMissing.setter
    def isMissing(self, value):
        ''' Sets the missing flag. '''
        self.__isMissing = value
    
    @property
    def members(self):
        ''' Returns the list of members. '''
        return self.__members

    @property
    def name(self):
        ''' Returns the name of this file. '''
        return self.__name

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        self.__filename = value
        
    def addMember(self, memberName, memberType, missing = True):
        if memberName not in self.__members:
            if memberType == 'function':
                member = SrcFunction(memberName, missing)
            else:
                member = SrcMember(memberName, missing)
            
            self.__members[memberName] = member
    
    def memberDescriptionMissing(self, memberName):
        try:
            self.__members[memberName].isMissing = True
        except KeyError:
            member = SrcFunction(memberName)
            self.__members[memberName] = member
            self.__members[memberName].isMissing = True
    
    def memberParameterMissing(self, memberName, paramName):
        try:
            self.__members[memberName].addParameter(paramName)
        except KeyError:
            member = SrcFunction(memberName)
            self.__members[memberName] = member
            self.__members[memberName].addParameter(paramName)
        
    def memberReturnValueMissing(self, memberName):
        try:
            self.__members[memberName].returnValueMissing = True
        except KeyError:
            member = SrcFunction(memberName)
            self.__members[memberName] = member
            self.__members[memberName].returnValueMissing = True
            
    def __init__(self, name, compoundType, filename = ''):
        '''
        Constructor
        '''
        self.__members = {}
        self.__name = name
        self.__filename = filename
        self.__compoundType = compoundType
        self.__isMissing = False
        
class CompoundClass(Compound):
    
    def __init__(self, name, ):
        super(CompoundClass, self).__init__(name, "class")
        
class CompoundFile(Compound):
    
    def __init__(self, name):
        super(CompoundFile, self).__init__(name, "file")
        
class CompoundGroup(Compound):
    
    def __init__(self, name):
        super(CompoundGroup, self).__init__(name, "group")
        
class CompoundStruct(Compound):
    
    def __init__(self, name):
        super(CompoundStruct, self).__init(name, "struct")
        