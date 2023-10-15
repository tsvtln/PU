#!/usr/bin/env python
#tsvtln
from socket import * 

if __name__ == '__main__':

    import sys

    if ( len(sys.argv) != 2 ):
        print "Usage: " + sys.argv[0] + " you must enter IP or FQDN as argument"
        sys.exit(1)
	
    targetIP = gethostbyname(sys.argv[1])

    for i in range(20, 65535):
       	s = socket(AF_INET, SOCK_STREAM)
	result = s.connect_ex((targetIP, i))
       	if(result == 0) :
            print '%d' % (i)
	    s.close()
