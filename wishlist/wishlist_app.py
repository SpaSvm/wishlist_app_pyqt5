from PyQt5 import QtCore, QtGui, QtWidgets
import MySQLdb as mdb
import ast
import os

# Данные о базе из переменных окружения
localhost = os.environ.get('wishlist_db_host')
user = os.environ.get('wishlist_db_user')
password = os.environ.get('wishlist_db_password')
db_name = os.environ.get('wishlist_db_name')

# Соединение с базой данных
def get_db():
    db = mdb.connect(localhost, user, password, db_name)
    cur = db.cursor()
    cur.execute(
            """
            CREATE TABLE IF NOT EXISTS wishlist (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(20),
            price INT,
            link VARCHAR(80),
            note VARCHAR(60)
            );
            """
    )
    db.commit()
    return db

# Конвертирование данных из базы в подходящий тип для приложения
def converter(mydata):
    def cvt(data):
        try:
            return ast.literal_eval(data)
        except Exception:
            return str(data)
    return tuple(map(cvt, mydata))

# Класс описывающий приложение
class Ui_MainWindow(object):
    # Основная функция приложения
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(641, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Serif")
        font.setPointSize(12)
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Title', 'Price', 'Link', 'Note'])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.verticalLayout.addWidget(self.tableWidget)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.create)
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.update)
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.delete)
        self.verticalLayout.addWidget(self.pushButton_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.loadData()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Create"))
        self.pushButton_3.setText(_translate("MainWindow", "Update"))
        self.pushButton_2.setText(_translate("MainWindow", "Delete"))

    # Загрузка данных из базы данных
    def loadData(self):
        db = get_db()
        cur = db.cursor()
        rows = cur.execute("SELECT * FROM wishlist")
        data = cur.fetchall()

        for row in data:
            self.addTable(converter(row))

        cur.close()

    # Распределение по ячейкам таблицы приложения
    def addTable(self, columns):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        for i, column in enumerate(columns):
            self.tableWidget.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(str(column)))

    # Диалоговое окно для создания новой записи
    def create(self):
        title, ok1 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Title',
            'Enter wish title:')
        price, ok2 = QtWidgets.QInputDialog.getInt(self.setupUi(MainWindow), 'Price',
            'Enter wish price:')
        link, ok3 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Link',
            'Link to the wish:')
        note, ok4 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Note',
            'Your note:')

        # Проверка подтверждения ввода, добавление новой записи в БД
        # и добавление записи в таблицу приложения
        if ok1 and ok2 and ok3 and ok4:
            db = get_db()
            cur = db.cursor()
            cur.execute(
                'INSERT INTO wishlist (title, price, link, note)'
                'VALUES ("{}", {}, "{}", "{}")'.format(title, price, link, note)
            )
            db.commit()
            sql = 'SELECT * FROM wishlist WHERE title = %s'
            record = (title,)
            cur.execute(sql, record)
            data = cur.fetchone()
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            for i, column in enumerate(converter(data)):
                self.tableWidget.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(str(column)))

    # Диалоговое окно выбора записи для удаления
    def delete(self):
        id, ok = QtWidgets.QInputDialog.getInt(self.setupUi(MainWindow), 'Wish id',
            'Enter wish id here:')
        # При подтверждении ввода - удаление выбранной записи из БД
        # и обновление таблицы приложения
        if ok:
            db = get_db()
            cur = db.cursor()
            sql = 'DELETE FROM wishlist WHERE id = %s'
            record = (id,)
            cur.execute(sql, record)
            db.commit()

            self.tableWidget.clear()
            for i in reversed(range(self.tableWidget.rowCount())):
                self.tableWidget.removeRow(i)

            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setHorizontalHeaderLabels(['ID', 'Title', 'Price', 'Link', 'Note'])
            self.loadData()

    # Диалоговое окно выбора записи для изменение
    def update(self):
        id, ok = QtWidgets.QInputDialog.getInt(self.setupUi(MainWindow), 'Wish id',
            'Enter wish id here:')
        # Диалоговые окна изменения пунктов записи
        if ok:
            title, ok1 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Title',
                'Enter new title:')
            price, ok2 = QtWidgets.QInputDialog.getInt(self.setupUi(MainWindow), 'Price',
                'Enter new price:')
            link, ok3 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Link',
                'New link to the wish:')
            note, ok4 = QtWidgets.QInputDialog.getText(self.setupUi(MainWindow), 'Note',
                'New note:')
            # При подтверждении ввода - изменение данных записи в БД
            # и обновление таблицы приложения
            if ok1 and ok2 and ok3 and ok4:
                db = get_db()
                cur = db.cursor()
                sql = 'UPDATE wishlist SET title = %s, price = %s, link = %s, note = %s WHERE id = %s'
                record = (title, price, link, note, id)
                cur.execute(sql, record)
                db.commit()

                self.tableWidget.clear()
                for i in reversed(range(self.tableWidget.rowCount())):
                    self.tableWidget.removeRow(i)

                header = self.tableWidget.horizontalHeader()
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
                header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
                self.tableWidget.setColumnCount(5)
                self.tableWidget.setRowCount(0)
                self.tableWidget.setHorizontalHeaderLabels(['ID', 'Title', 'Price', 'Link', 'Note'])
                self.loadData()

# При самостоятельном запуске файла запускается приложение
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
