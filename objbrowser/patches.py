""" Patches to add Qt5 methods to the classes.

    Forked from qtyp._patch.qheaderview.py (commit 722e745932281a64ef64ac8dd189329bec462f00),
    which has the MIT license.
"""
import logging

from qtpy.QtWidgets import QHeaderView
from qtpy import PYQT4, PYSIDE

logger = logging.getLogger(__name__)


def patch_qheaderview_if_needed():
    """ Checks that we are in PyQt4 or PySide and that QHeaderView hasn't been patched already.

        If so it will add the new Qt5 methods to the QHeaderView class.
    """
    # Only patch for Qt4 or Pyside
    if PYQT4 or PYSIDE:

        # See if it hasn't allready been patch (by qtpy 1.2.0 or higher)
        if not hasattr(QHeaderView, 'sectionsClickable'):
            logger.debug("Patching QHeaderView")
            introduce_renamed_methods_qheaderview(QHeaderView)



def introduce_renamed_methods_qheaderview(QHeaderView):
    """ Add the new Qt5 methods to the QHeaderView class.
    """
    def sectionsClickable(self):
        """
        QHeaderView.sectionsClickable() -> bool
        """
        return QHeaderView.isClickable(self)
    QHeaderView.sectionsClickable = sectionsClickable

    def sectionsMovable(self):
        """
        QHeaderView.sectionsMovable() -> bool
        """
        return QHeaderView.isMovable(self)
    QHeaderView.sectionsMovable = sectionsMovable

    def sectionResizeMode(self, logicalIndex):
        """
        QHeaderView.sectionResizeMode(int) -> QHeaderView.ResizeMode
        """
        return QHeaderView.resizeMode(self, logicalIndex)
    QHeaderView.sectionResizeMode = sectionResizeMode

    def setSectionsClickable(self, clickable):
        """
        QHeaderView.setSectionsClickable(bool)
        """
        return QHeaderView.setClickable(self, clickable)
    QHeaderView.setSectionsClickable = setSectionsClickable

    def setSectionsMovable(self, movable):
        """
        QHeaderView.setSectionsMovable(bool)
        """
        return QHeaderView.setMovable(self, movable)
    QHeaderView.setSectionsMovable = setSectionsMovable

    def setSectionResizeMode(self, *args):
        """
        QHeaderView.setSectionResizeMode(QHeaderView.ResizeMode)
        QHeaderView.setSectionResizeMode(int, QHeaderView.ResizeMode)
        """
        QHeaderView.setResizeMode(self, *args)
    QHeaderView.setSectionResizeMode = setSectionResizeMode



