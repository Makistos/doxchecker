'''
Created on 29 Sep 2011

@author: poutima
'''

class SrcMember(object):
    '''
    Represents one member (variable, typedef etc) in the error log.
    '''
    @property
    def name(self):
        ''' Returns the name of this member. '''
        return self.__name
    
    @property
    def memberType(self):
        ''' Returns the member type of this member. '''
        return self.__memberType
    
    @property
    def isMissing(self):
        ''' 
        Tells whether this member is missing documentation or not. 
        Only really used with SrcFunction, with SrcMember type
        objects this should always be true because there are no
        other missing documentation than the description for them. 
        '''
        return self.__isMissing
    
    @isMissing.setter
    def isMissing(self, value):
        ''' Sets the missing flag. '''
        self.__isMissing = value
    
    def __init__(self, memberName, memberType, missing = False):
        '''
        Constructor
        '''
        self.__name = memberName
        self.__memberType = memberType
        self.__isMissing = missing
        self.__parameters = {}
    
    @property
    def parameters(self):
        return self.__parameters

    def addParameter(self, value):
        self.__parameters[value] = value
        
    def __str__(self):
        ''' Overwritten to produce more useable output. '''
        return ("%s (%s) " % (self.__name, self.__type))

    def __repr__(self):
        ''' Overwritten to produce more useable output. '''
        return ("%s, %s " % (self.__name, self.__type))
    
class SrcFunction(SrcMember):
    
    '''
    Represents a function that misses some documentation. Things that
    could be missing are:
    - Function description,
    - One or more missing parameter descriptions,
    - Return value type description.
    '''
    
    def addMissingParameter(self, parameterName):
        ''' Adds a missing parameter to this function. '''
        self.__parameters.append(parameterName)
            
    @property
    def returnValueMissing(self):
        ''' 
        Tells whether this function is missing the return
        value type description. 
        ''' 
        
        return self.__returnValueMissing
    
    @returnValueMissing.setter
    def returnValueMissing(self, value):
        ''' Sets the return value flag on. '''
        self.__returnValueMissing = value
            
    def __init__(self, functionName, missing = False):
        ''' Constructor '''
        super(SrcFunction, self).__init__(functionName, 'function', missing)
        self.__returnValueMissing = False
        
    def __str__(self):
        ''' Overwritten to produce more useable output. '''
        return("%s (%s) " % (self.__name, self.__type))
        
    def __repr__(self):
        ''' Overwritten to produce more useable output. '''
        return("%s, %s " % (self.__name, self.__type))