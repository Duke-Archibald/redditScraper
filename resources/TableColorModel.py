from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtSql import QSqlTableModel, QSqlRelationalTableModel


class TableColorModel(QSqlRelationalTableModel):
    def __init__(self, db):
        super(TableColorModel, self).__init__(db=db)

    def data(self, index, role=Qt.DisplayRole):
        color = "#000000"
        if role == Qt.DisplayRole:
            return super(TableColorModel, self).data(index, role)
        if role == Qt.EditRole:
            return super(TableColorModel, self).data(index, role)
        if role == Qt.ForegroundRole:
            if self.tableName() == "lines":
                color = QtGui.QColor(super(TableColorModel, self).data(super(TableColorModel, self)
                                                                       .index(index.row(), 11), Qt.DisplayRole))
            elif self.tableName() == "voices":

                color = QtGui.QColor(super(TableColorModel, self).data(super(TableColorModel, self)
                                                                       .index(index.row(), 6), Qt.DisplayRole))

            elif self.tableName() == "submissions":
                status = super(TableColorModel, self).data(super(TableColorModel, self)
                                                           .index(index.row(), 3), Qt.DisplayRole)
                if status == "wip":
                    color = QColor("#979c08")
                elif status == "to-do":
                    color = QColor("#919189")
                elif status == "complete":
                    color = QColor("#00800d")

            elif self.tableName() == "entries":
                status = super(TableColorModel, self).data(super(TableColorModel, self)
                                                           .index(index.row(), 3), Qt.DisplayRole)
                if status == "wip":
                    color = QColor("#979c08")
                elif status == "to-do":
                    color = QColor("#919189")
                elif status == "complete":
                    color = QColor("#00800d")

            return color
