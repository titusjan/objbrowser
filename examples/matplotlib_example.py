""" 
    Example that demonstrates inspecting a MatPlotLib Figure.
"""
from __future__ import print_function

import sys, logging
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.ioff()

from objbrowser import browse, logging_basic_config

logger = logging.getLogger(__name__)

def make_fig(title1):
    """ Creates a test Figure.
    """
    x = np.linspace(10.0, 40.0, 100)
    y1 = x + 1.23456789e7

    fig1 = plt.figure(title1)
    fig1.clear()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.plot(x, y1, 'b-', picker = 5)
    ax1.grid(True)
    y_formatter = mpl.ticker.ScalarFormatter(useMathText=True)
    y_formatter.set_useOffset(False)
    ax1.yaxis.set_major_formatter(y_formatter)

    return fig1
    
        
def main():
    """ Main program to test stand alone 
    """
    logging_basic_config('DEBUG')
    logger.info('Started example')

    fig1 = make_fig('figure1')
    exit_code = browse(fig1, obj_name='fig1', show_special_methods=False)

    logging.info('Done example')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
