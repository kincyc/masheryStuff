#!/usr/bin/python

import sys
sys.path.append('/opt/vmware/share/htdocs/service/mashery/cgi/')

import MySQLdb as mdb
import Mashery

def purge_tokens():
    print "Purging tokens from instance...\n"
    conn = None
    
    try:
        creds = Mashery.get_mysql_credentials('local')
        if (creds != None):
            conn = mdb.connect("localhost", creds['user'], creds['password'], "onprem");
            cursor = conn.cursor()
            cursor.execute("TRUNCATE table oauth2_access_tokens;")
            # conn.commit()
            
            return True
        
        return False
    
    except mdb.Error, e:
        print e
        if conn != None:
            conn.rollback()
            conn.close()
        return False
    
    except:
        return False
    
systype = Mashery.get_system_type()
if (systype == "master"):
    if (purge_tokens()):
        print "Sucessfully purged all tokens\n"
    else:
        print "Failed purging tokens\n"
else:
    print "Command must be run on Master instance"
