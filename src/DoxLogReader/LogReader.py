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
        test = re.compile('''
                          (?P<full_path>                  # Start capturing a group called full_path
                            .+                            #   It consists of one or more characters of any kind
                          )                               # End group
                          :                               # A literal colon
                          \d+                             # One or more numbers
                          :                               # A literal colon
                          \swarning:\sCompound\s+         # An almost static string
                          (?P<member_name>                # Start capturing a group called member_name
                            .+                            #   It consists of one or more characters of any kind
                          )                               # End group
                          \sis\snot\sdocumented''',       # And an almost static string to end the line
                          re.IGNORECASE|re.VERBOSE)       # Let's not worry about case, because it seems to differ between Doxygen versions
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
        test = re.compile('''
                          (?P<full_path>                        # Start capture group full_path
                          .+                                    #   It consists of characters of any kind
                          )                                     # 
                          :                                     # A literal colon
                          \d+                                   # One more or numbers
                          :                                     # A literal colon
                          \s+Warning:\s+Member\s+               # A static string
                          (?P<member_name>                      # Capture group member_name
                            .+                                  #   It consists of characters of any kind
                          )                                     #
                          \s\(                                  # Space and open parentheses
                          (?P<member_type>                      # Capture group member_type
                            %s                                  #   Defined in self.__MEMBER_TYPES
                          )                                     #
                          \)                                    # Literal closing parentheses
                          \sof\sfile\s+                         # Static string
                          (?P<filename>                         # Capture group filename
                            .+                                  #   It consists of characters of any kind
                          )                                     #
                          \s+is\snot\sdocumented''' % (self.__MEMBER_TYPES), # And a static string to end the line
                          re.IGNORECASE|re.VERBOSE)                          # Let's not worry about case, because it seems to differ between Doxygen versions
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
        test = re.compile('''
                          (?P<full_path>                     # Start capturing a group called full_path
                            .+                               #   It consists of one or more characters of any kind
                          )                                  # Group ends
                          :                                  # A literal colon
                          \d+                                # One or more numbers
                          :                                  # A literal colon
                          \s+warning:\s+Member\s+            # An almost static string
                          (?P<member_name>                   # Start capturing a group called member_name
                            .+                               #   It consists of one or more characters of any kind
                          )                                  # End group
                          \s+                                # One or more whitespaces
                          \(                                 # A literal (
                          (?P<member_type>                   # Start capturing a group called member_type
                            %s                               #   Possible values are listed in self.__MEMBER_TYPES
                          )                                  # End group
                          \)                                 # A literal )
                          \sof\s(class|group|namespace|file) # An almost static string
                          \s+                                # One or more whitespaces
                          (?P<class_name>                    # Start capturing a group called class_name
                            .+                               #   It consists of one or more characters of any kind
                          )                                  # End of group
                          \s+is\snot\sdocumented             # And a static string to end the line
                          ''' 
                          % (self.__MEMBER_TYPES),  
                          re.IGNORECASE|re.VERBOSE)                            # Let's not worry about case, because it seems to differ between Doxygen versions
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
        
        test = re.compile('''
                          (?P<filename>                                 # Capture a group called file_name
                            .+                                          #   It consists of one more characters of any type
                          )                                             # Line starts with full path and file name
                          :                                             # A literal colon
                          \d+                                           # One or more numbers (line number)
                          :                                             # A literal colon
                          \s+warning:\sThe\sfollowing\sparameters\sof\s # An almost static string
                          (?P<member_name>                              # Capture a group called member_name
                            [                                           #         
                              ^:                                        #   Match anything but a colon (so finding a colon ends group)
                            ]+                                          #   Match one or more characters
                          )                                             # Group ends
                          (                                             # In C++'s case:
                            ::                                          #   Two colons
                            (?P<function_name>                          #   Start another group called function_name
                              .+                                        #     It consists on one or more alphanumeric characters
                            )                                           #   End group
                          )*                                            # But this is optional and does not apply to C
                          \sare\snot\sdocumented:'''                           # String ends with static string
                          , re.IGNORECASE|re.VERBOSE|re.DEBUG)                                  # Let's not worry about case, because it seems to differ between Doxygen versions
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
        test = re.compile('''
                           (?P<full_path>                                  # Capture a group called full_path
                             .+                                            #   It consists of one more characters of any type
                           )                                               # Group ends                      
                           :                                               # A literal colon
                           \d+                                             # One or more numbers (line number)
                           :                                               # A literal colon
                           \s+warning:\s+parameters\sof\smember\s+         # An almost static string
                           (?P<member_name>                                # Capture a group called member_name
                             [                                             #   
                               ^:                                          #   Match anything but a colon (so finding a colon ends group)
                             ]+                                            #   Match one or more characters
                           )                                               # Group ends
                           (                                               # Start an unnamed group 
                             ::                                            #   Two literal colons
                             (?P<function_name>                            #   Start another group called function_name
                               \w+                                         #     It consists on one or more alphanumeric characters
                             )                                             #   End group
                           )*                                              # This group is entirely optional and does not apply to C
                           \s+are\snot\s\(all\)\sdocumented''',            # And line ends with an almost static string
                           re.IGNORECASE|re.VERBOSE)                                 # Let's not worry about case, because it seems to differ between Doxygen versions
                          
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
        test = re.compile(('''\s+parameter '            # Static string
                           '(?P<param_name>             # Start capture group param_name
                             .+)                        #   Consisting of one of more characters of any type
                           '\'\n'''),                   # It ends with a hyphen and EOL character
                           re.IGNORECASE|re.VERBOSE)
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
        test = re.compile('''
                          (?P<full_path>                              # Start capturing a group called full_path
                            .+                                        #   It consists of one more characters of any type
                          )                                           # Group ends
                          :                                           # A literal colon
                          \d+                                         # One or more numbers
                          :                                           # A literal colon
                          \swarning:\sreturn\stype\sof\smember\s      # Almost static line
                          (?P<member_name>                            # Start capturing a group called member_name 
                            .+                                        #   It consists of one or more characters of any type
                          )                                           # Group end
                          \sis\snot\sdocumented''',                   # Almost static string to end the line 
                          re.IGNORECASE|re.VERBOSE)                   # Let's not worry about case, because it seems to differ between Doxygen versions
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

    #def __parseInvalidParamCommand(self, line):
    #    test = re.compile(('''(?P<full_path>.+):\d+: warning: argument \'(?P<param_name>.+)\' of command @param is not found in the argument list of (?P<member_name>[^:]+)(::(?P<function_name>\w+))*', re.IGNORECASE)
    #    m = test.match(line)
    #    if m:
    #        pass
        
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
            test = re.compile('''
                                (?P<member_name>                   # Begin capturing a group called member_name
                                  (                                #   Capture the operator name
                                    operator                       #     Static string
                                    [                              #
                                      =\-\+\*\[\]!&%               #     Match operators =, -, +, *, [, ], !, & and %
                                    ]                              #
                                    +                              #   One or more times (i.e. will also capture !=, [], etc)
                                  )                                #
                                )                                  #
                                (                                  # Capture the possible parameters
                                  [                                #
                                    \(\[                           #   Literal ( or [
                                  ]                                #
                                  .+                               #   Any character one or more times
                                  [                                #
                                    \)\]                           #   Literal ) or ]
                                  ]                                #
                                )*                                 # Zero or more times
                              ''', re.IGNORECASE|re.VERBOSE)       # Let's not worry about case, because it seems to differ between Doxygen versions
            m2 = test.match(str(s))
            try:
                retval = str(m2.group('member_name'))
            except AttributeError:
                retval = ''
        else:       
            test = re.compile('''
                              (?P<member_name>    # Capture a group called member_name
                                \w+               #   It consists of one or more alphanumerical characters
                              )                   # 
                              (                   # Capture possible parameters
                                [                 # 
                                  \(\[            #   A literal ( or [
                                ]                 # 
                                .+                #   One or more characters of any type
                                [                 # 
                                  \)\]            #   A literal ) or ]
                                ]                 # 
                              )*                  # Zero or more times
                          ''')
            
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
        if line.startswith("/home/foo"):
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
