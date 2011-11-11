'''
Created on 30 Sep 2011

@author: poutima
'''

from lxml import etree
from XmlReader import XmlReader
import logging

class Reporter(object):
    '''
    Matches errors in the log to the members in the XML index file and creates the resulting XML.
    '''            

    def addIssuesToXml(self):
        '''
        Adds attributes for member type elements in the XML that were found
        in the error log.
        '''
        for comp in self.__xmlroot.iter('compound'):
            del comp.attrib['refid']
            comp_name = comp.find('name').text
            comp_type = comp.attrib['kind']

            try:
                error_comp = self.__doxyLog[comp_name]
            except KeyError:
                error_comp = None
                
            if error_comp != None:
                if error_comp.isMissing == True:
                    comp.attrib['isMissing'] = "1"
                    
                for member in comp.iter('member'):
                    del member.attrib['refid']
                    member_name = member.find('name').text
                    member_kind = member.attrib['kind']
                    if member_name in error_comp.members:
                        error_member = error_comp.members[member_name]
                        if error_member.memberType == 'function':
                            if len(error_member.parameters) > 0:
                                member.attrib['missingparameters'] = ','.join(error_member.parameters)
                            if error_member.returnValueMissing == True:
                                member.attrib['missingreturnvalue'] = "1"
                            if error_member.isMissing == True:
                                member.attrib['ismissing'] = "1"                            
                        else:
                            member.attrib['ismissing'] = "1"
            else:
                # Remove refid attributes
                for member in comp.iter('member'):
                    del member.attrib['refid']

    def writeXml(self, outfile):
        '''
        Writes the modified XML tree to a file.
        
        @param outfile    File to write the XML to.
        '''
        
        xml_out = etree.tostring(self.__xmlroot, pretty_print=True)
        
        logging.info('Writing XML file ' + outfile)
        
        try:
            f = open(outfile, 'w')
        except IOError:
            logging.error("Xml file " + outfile + " not found!")
        
        f.write(xml_out)
    
        f.close()
          
    def __init__(self, xmlDir, logProblems):
        '''
        Constructor
        
        @param xmlDir : Directory where the Doxygen XML files are. 
        @param logProblems : Collection of SrcFile objects in a dictionary.
        @param danglingProblems: List of issues that could not be mapped to a file.
        @param memberTypes: List of member types found.
        
        '''
        self.__fileCount = 0
        xmlReader = XmlReader()
        self.__xmlDir = xmlDir
        doxyXML = xmlReader.readXML(self.__xmlDir + '/index.xml', None)
        self.__xmlroot = doxyXML.getroot()
        self.__doxyLog = logProblems
                