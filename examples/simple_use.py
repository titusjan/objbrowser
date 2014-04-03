""" 
    Simple usage of the object browser; shows local variables
"""
from objbrowser import browse
from datetime import datetime

def main():
    utc_now = datetime.utcnow()
    lst = [5, 6, 7]
    browse(locals())


if __name__ == '__main__':
    main()
    