#!/usr/bin/python
'''
@date Oct 4, 2010

@author: mep
'''
import logging

from lxml import etree
from lxml.etree import LxmlSyntaxError

class XmlReader(object):
    '''
    This class implements a simple XML reader that can read an XML file and make sure
    it is valid XML and according to a schema (if defined)
    '''
    
    ## The full xml contents as a string.
    full_xml = ''
    
    def __init__(self):
        '''
        Constructor, nothing to see here.
        '''
            
    def readXML(self, xmlFile, schemaFile = None):
        """ 
        Attempts to read the XML file. File's integrity (=valid XML) is checked and
        it is also validated against the schema file, if one is found.
        
        If schemaFile is None, no validation against the schema is done. Also, if the schema
        file is not found, validation is skipped.
        
        Returns None if any errors were encountered.
        """
        logging.info('Reading XML file ' + xmlFile)
        
        try:
            f = open(xmlFile, 'r')
        except IOError:
            logging.error("Xml file " + xmlFile + " not found!")
            return None

        parser = etree.XMLParser()
            
        try:            
            tree = etree.parse(f, parser)
        except LxmlSyntaxError:
            logging.error('Invalid XML file ' + xmlFile + ' (unable to read!)')
            logging.error('Parser reports: ' + str(parser.error_log))
            return None
    
        self.full_xml = etree.tostring(tree)
        
        if schemaFile != None:
            valid = self.validate(tree, schemaFile)
            if valid == False:
                logging.error('XML file ' + xmlFile + ' does not match schema file.')
                return None
        
        return tree
    
    def _validate(self, xml, schema):
        """ 
        Attempts to validate the XML with a schema definition (xsd or dtd).
        
        The function first tries to find an .xsd file and if it doesn't find it, tries .dtd. 
        If that isn't found either, the XML is assumed to be correct.

        If a schema definition is found, it is used to verify the XML with etree.DTD.validate().
        """
        try: 
            f = open(schema)
        except IOError:
            logging.info('No schema found')
            return True

        dtd = etree.DTD(f)
        res = dtd.validate(xml)
        
        if res == False:
            logging.error('Schema validation failed')
        else:
            logging.info("XML validated ok")
        
        return res
    
    def toString(self):
        ''' Returns a stringified version of the XML tree. '''
        print self.full_xml
