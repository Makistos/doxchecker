'''
Created on 25 Oct 2011

@author: poutima
'''

import os
import re
import sys
from Compound import *

class LogLine(object):
    
    def __init__(self, line):
        self.__line = line
        

        
class LogReader(object):
    '''
    classdocs
    '''

    # Static variables for __handleLine function
    __state = 0
    __currFile = ''
    __currCompound = ''
    __currFunc = ''
    __MEMBER_TYPES = 'function|variable|define|enum|enumvalue|typedef|enumeration'

    @property
    def compounds(self):
        return self.__compounds

    def readFile(self, filename):
        ''' 
        Reads a file and returns an array without any comment lines. 
        Comment lines start with a hash mark '#'.
        
        @param filename Name of file to handle.
        
        '''
        try:
            f = open(filename, 'r')
        except IOError:
            print 'File ' + filename + ' not found.'
            sys.exit(2)
        
        lines = filter(lambda x: not x.startswith('#'), f.readlines()) # Remove comment lines, if any
        
        f.close()
        return lines
    
    def __addCompound(self, name, compoundType, filename = ''):
        compound = None
    
        if name not in self.__compounds:
            if compoundType == 'file':
                compound = CompoundFile(name)
            elif compoundType == 'struct' or compoundType == 'file' or compoundType == 'group' or compoundType == 'class':
                compound = CompoundClass(name)
            elif compoundType == 'dir':
                pass
            else:
                print("Unknown compound type %s in file %s" % (compoundType, name))
            
            if compound != None:
                compound.filename = filename
                self.__compounds[name] = compound 

    def __parseMissingCompound(self, line):
        '''
        Checks if the string matches an error indicating a missing compound. If it matches,
        information is saved to the srcFiles dictionary.
        
        @param line: The string to be checked.
        
        @return: True if string matches, False otherwise.
        
        '''
        
        retval = False
        test = re.compile('(?P<full_path>.+):\d+: warning: Compound\s+(?P<member_name>.+) is not documented', re.IGNORECASE)
        m = test.match(line)
        if m:
            srcfile = os.path.basename(str(m.group('full_path')))
            m_name = self.__removeParameters(m.group('member_name'))
            
            self.__addCompound(m.group('member_name'), 'class', srcfile)
            self.__compounds[m.group('member_name')].isMissing = True
            retval = True
        return retval

    def __parseMissingFileMember(self, line):
        '''
        Checks if the string matches an error indicating a missing file member. If it matches,
        information is saved to the srcFiles dictionary.
        
        @param line: The string to be checked.
        
        @return: True if string matches, False otherwise.
        
        '''
        retval = False
        test = re.compile('(?P<full_path>.+):\d+:\s+Warning:\s+Member\s+(?P<member_name>.+) \((?P<member_type>%s)\) of file\s+(?P<filename>.+)\s+is not documented' % (self.__MEMBER_TYPES), re.IGNORECASE)
        m = test.match(line)
        if m:
            # Remove parameters from function name
            m_name = self.__removeParameters(m.group('member_name'))
            srcFile = os.path.basename(m.group('filename'))
            self.__addCompound(srcFile, 'file', m.group('filename'))
            compound = self.__compounds[srcFile]
            compound.addMember(m_name, m.group('member_type'), True)
            retval = True
        
        return retval

    def __parseMissingClassMember(self, line):
        '''
        Checks if the string matches an error indicating a missing class member. If it matches,
        information is saved to the srcFiles dictionary.
        
        @param line: The string to be checked.
        
        @return: True if string matches, False otherwise.
        
        '''
        retval = False
        test = re.compile('(?P<full_path>.+):\d+:\s+warning:\s+Member\s+(?P<member_name>.+)\s+\((?P<member_type>%s)\) of (class|group|namespace)\s+(?P<class_name>.+)\s+is not documented' % (self.__MEMBER_TYPES), re.IGNORECASE)
        m = test.match(line)
        if m:
            srcfile = os.path.basename(str(m.group('full_path')))
            className = str(m.group('class_name'))
            m_name = self.__removeParameters(m.group('member_name'))
            memberType = m.group('member_type')
            
            self.__addCompound(className, 'class', srcfile)
            compound = self.__compounds[className]
            
            compound.addMember(m_name, memberType, True)
            
            retval = True
        return retval

    def __parseMissingParamList(self, line):
        ''' 
        Detect missing function parameters (they are handled in state 1).
        '''
        retval = False
        
        test = re.compile('(?P<filename>.+):\d+:\s+warning: The following parameters of (?P<member_name>[^:]+)(::(?P<function_name>.+))* are not documented:', re.IGNORECASE)
        m = test.match(line)
        if m:
            self.__state = 1
            self.__currFile = os.path.basename(str(m.group('filename')))
            if m.group('function_name') != None:
                # C++
                m_name = self.__removeParameters((m.group('function_name')))
                self.__currCompound = m.group('member_name')
                self.__currFunc = m_name
            else:
                # C
                m_name = self.__removeParameters(m.group('member_name'))
                self.__currCompound = self.__currFile
                self.__currFunc = m_name

            retval = True 
        
        return retval

    def __parseMissingParameter(self, line):
        '''
        Checks if the string matches an error indicating a missing parameter. If it matches,
        information is saved to the srcFiles dictionary.
        
        @param line: The string to be checked.
        
        @return: True if string matches, False otherwise.
        
        '''
        retval = False
        test = re.compile('(?P<full_path>.+):\d+:\s+warning:\s+parameters of member\s+(?P<member_name>[^:]+)(::(?P<function_name>\w+))*\s+are not \(all\) documented', re.IGNORECASE)
        m = test.match(line)
        
        if m:
            if m.group('full_path').startswith('<'):
                # There is no way to know where these structs belong to.
                return False
            
            found = False
            srcfile = os.path.basename(str(m.group('full_path')))
            if m.group('function_name') != None:
                # C++
                m_name = self.__removeParameters((m.group('function_name')))
                compound_type = 'class'
            else:
                # C
                m_name = self.__removeParameters(m.group('member_name'))
                compound_type = 'file'
                
            if m.group('member_name') in self.__compounds:
                compound = self.__compounds[m.group('member_name')]
                compound.addMember(m_name, 'function', False)
                compound.memberParameterMissing(m_name, 'Multiple')
                found = True
            else:
                for compound in self.__compounds.itervalues():
                    if compound.filename == srcfile:
                        compound.addMember(m_name, 'function', False)
                        compound.memberParameterMissing(m_name, 'Multiple')
                        found = True
            if found == False:
                self.__addCompound(m_name, compound_type, srcfile)
                compound = self.__compounds[m_name]
                compound.memberParameterMissing(m_name, 'Multiple')                

            retval = True
    
        return retval

    def __parseParamLine(self, line):
        '''
        Handle any lines that contain a parameter after a line indicating a list of missing 
        parameters. A matching line looks like
            parameter "param_name"
            
        '''
        test = re.compile('\s+parameter \'(?P<param_name>.+)\'\n', re.IGNORECASE)
        m = test.match(line)
        if m:
            found = False
            if self.__currCompound in self.__compounds:
                compound = self.__compounds[self.__currCompound]
                compound.addMember(self.__currFunc, 'function', False)
                compound.memberParameterMissing(self.__currFunc, m.group('param_name'))
                found = True
            else:
                for compound in self.__compounds.itervalues():
                    if compound.filename == self.__currFile:
                        compound.addMember(self.__currFunc, 'function', False)
                        compound.memberParameterMissing(self.__currFunc, m.group('param_name'))
                        found = True
            if found == False:
                self.__addCompound(self.__currCompound, 'file', self.__currFile)
                compound = self.__compounds[self.__currCompound]
                compound.addMember(self.__currFunc, 'function', False)
                compound.memberParameterMissing(self.__currFunc, m.group('param_name'))
        else:
            
            self.__state = 0
            self.__currFile = ''
            self.__currCompound = ''
            self.__currFunc = ''
        return

    def __parseMissingReturnValue(self, line):
        '''
        Checks if the string matches an error indicating a missing return value. If it matches,
        information is saved to the srcFiles dictionary.
        
        @param line: The string to be checked.
        
        @return: True if string matches, False otherwise.
        
        '''
        
        retval = False
        test = re.compile('(?P<full_path>.+):\d+: warning: return type of member (?P<member_name>.+) is not documented', re.IGNORECASE)
        m = test.match(line)
        if m:
            if m.group('full_path').startswith('<'):
                # There is no way to know where these structs belong to.
                test = re.compile('<(?P<member_name>[^>]+)>')
                m2 = test.match(m.group('full_path'))
                member_name = m2.group('member_name')
                for compound in self.__compounds.itervalues():
                    if member_name in compound.members:
                        compound.memberReturnValueMissing(member_name)
                        found = True
            else:
                srcfile = os.path.basename(str(m.group('full_path')))
                functionName = str(m.group('member_name'))
                
                found = False
                for compound in self.__compounds.itervalues():
                    if compound.filename == srcfile:
                        compound.memberReturnValueMissing(functionName)
                        found = True
                        
                if found == False:
                    self.__addCompound(srcfile, 'class', srcfile)
                    compound = self.__compounds[srcfile]
                    compound.memberReturnValueMissing(functionName)
                retval = True
            
        return retval

    def __removeParameters(self, s):
        ''' 
        Picks up the function or variable name by removing everything else 
        from the given string (function parameters etc).
        
        A name consists of alphanumerical characters and underscore. Anything 
        after a string containing those characters that are either inside 
        parentheses () or brackets [] are removed. Example:
        
        "my_func(int a, char c)" would become "my_func".  
        
        @param s:    Full function or variable declaration.
        
        @return:     Cleaned up function or variable name or None if no
                     matching name was found.

        '''

        retval = ''
        
        # Check that this isn't an override method for some operators
        test = re.compile('operator[=\[\+\-]+')
        
        m = test.match(str(s))
        if m:
            test = re.compile('(?P<member_name>(operator[=\-\+\*\[\]!&%]+))([\(\[].+[\)\]])*')
            m2 = test.match(str(s))
            try:
                retval = str(m2.group('member_name'))
            except AttributeError:
                retval = ''
        else:       
            test = re.compile('(?P<member_name>[a-zA-Z0-9_]+)([\(\[].+[\)\]])*')
            
            m2 = test.match(str(s))
            try:
                retval = str(m2.group('member_name'))
            except AttributeError:
                retval = ''
        
        return retval

    def __handleLine(self, line):
        '''
        This is the parser for the Doxygen output log. Handles a single line of 
        the log. 
        '''
        # Following is useful for debugging. If a line is not caught, copy the contents to the first line and 
        # put a breakpoint to the line with the pass command.
        if line.startswith("/home/poutima/albatross/LTE/LR2_beta/nomor/dev_3_ti/src/protocols/NOMOR_E_UTRA_S1-MME/protocol_data/rtconv.h:43: warning: return type of member rtBitStrToString is not documented"):
            pass
        
        # An ugly parser for different kinds of lines in the Doxygen output log
        
        # __state == 1 indicates the previous line said there are missing parameter(s) coming in the 
        # next lines in the format 
        #    parameter "param_name"
        # If the line doesn't match, __state is set back to 0 so that it is handled later.
        # We stay in this state until a line doesn't match since there can be several
        # parameters.
        if self.__state == 1:
            self.__parseParamLine(line)
        
        # __state == 0 indicates that this line can be handled normally.
        if self.__state == 0:
            
            #item = self.__lineTest(line)
            #if item != None:
            #    print ("Item: %s" % str(item))
            #    return
            
            # We check each possibility and handle the line inside the functions
            # if the line matches. 
            if self.__parseMissingFileMember(line) == True:
                return

            if self.__parseMissingClassMember(line) == True:
                return

            if self.__parseMissingCompound(line) == True:
                return
            
            if self.__parseMissingParameter(line) == True:
                return
            
            if self.__parseMissingReturnValue(line) == True:
                return
            
            if self.__parseMissingParamList(line) == True:
                return
            
            # Print everything not handled
            print line        
    
    def __init__(self,logObject, errorLog):
        '''
        Constructor
        '''
        self.__logger = logObject
        self.__compounds = {}
        
        for line in self.readFile(errorLog):
            self.__handleLine(line)
