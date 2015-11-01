""" 
    Simple usage of the object browser; shows local variables
"""
import logging
fmt = '%(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
logging.basicConfig(level='DEBUG', format=fmt)

from datetime import datetime
from objbrowser import browse
    

def main():
    
    utc_now = datetime.utcnow()
    lst = [5, 6, 7]
    browse(locals())


if __name__ == '__main__':
    main()
    