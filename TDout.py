from access import *  #access - это название файла
from mainwin1 import *
from reg import *
from label import *
from auth import *
from help import *
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

b = TDDB()  # класс для доступа к БД
b.open_connect() 

class mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.table()
        
        self.ui.pushButton_7.clicked.connect(self.button_clicked) # добавить новую запись

        self.ui.pushButton_2.clicked.connect(self.button_clicked_2) # незавершенные

        self.ui.pushButton_3.clicked.connect(self.button_clicked_3)# завершенные

        self.ui.pushButton_4.clicked.connect(self.table) # все

        self.ui.pushButton_6.clicked.connect(self.button_clicked_6) # просроченные

        self.ui.pushButton_8.clicked.connect(self.button_clicked_8) # поиск по словам и по дате

        self.ui.pushButton_9.clicked.connect(self.button_clicked_9) # близжайшие

        self.ui.pushButton_5.clicked.connect(self.button_clicked_5) # важные
        
        self.ui.pushButton_exit.clicked.connect(self.button_clicked_exit) #выход
        self.ui.pushButton_help.clicked.connect(self.button_clicked_help) #помощь

        self.ui.label_time.setText(today()) #дата
        self.ui.label_name.setText("Добро пожаловать, "+b.user_name+"!") # фун-ия для выведения имени        
    
    def button_clicked(self):
        if self.ui.lineEdit.text() == "":
            self.att_win = attwindow("Введите текст!")
            self.att_win.show()
        else:
            text = self.ui.lineEdit.text()
            date = self.ui.lineEdit_2.text()
            ch_state = self.ui.checkBox_2.isChecked()
            if b.new_todo(text, date, ch_state):
                self.ui.lineEdit.clear()
                self.ui.lineEdit_2.clear()
                self.update_table() 
            else:
                self.att_win = attwindow("Неверный формат даты! Введите в формате '01/01/2023'.")
                self.att_win.show()
                self.ui.lineEdit.clear()
                self.ui.lineEdit_2.clear()

     
    def button_clicked_2(self): 
        records = b.select_not_done_all()  
        self.ui.tableWidget.setRowCount(0)
        self.fill_table(records)            

    def button_clicked_3(self):
        records = b.select_done_all()
        self.ui.tableWidget.setRowCount(0)
        self.fill_table(records)

    def button_clicked_5(self): 
        records = b.select_important_all()
        self.ui.tableWidget.setRowCount(0)
        self.fill_table(records)

    def button_clicked_6(self): 
        records = b.select_late_all() 
        self.ui.tableWidget.setRowCount(0)
        self.fill_table(records)   
    
    def button_clicked_8(self): 
        if self.ui.lineEdit.text() == "" and self.ui.lineEdit_2.text() == "":
            self.att_win = attwindow("Введите текст или дату для поиска!")
            self.att_win.show()
        else:
            text = self.ui.lineEdit.text()
            text2 = self.ui.lineEdit_2.text()            
            records = b.select_by_text_all(text, text2)
            if b.select_by_text_all(text, text2):
                self.ui.tableWidget.setRowCount(0)
                self.fill_table(records)
            else:
                self.att_win = attwindow("Неверный формат даты! Введите в формате '01/01/2023'.")
                self.att_win.show()
                self.ui.lineEdit_2.clear()



    def button_clicked_9(self): 
        records = b.select_deadline_all() 
        self.ui.tableWidget.setRowCount(0)
        self.fill_table(records)      
           
    def fill_table(self, records):
        self.ui.tableWidget.setColumnCount(6)
        self.ui.tableWidget.setColumnWidth(0, 50)  # ширина
        self.ui.tableWidget.setColumnWidth(1, 1050)
        self.ui.tableWidget.setColumnWidth(2, 50)
        self.ui.tableWidget.setColumnWidth(3, 230)
        self.ui.tableWidget.setColumnWidth(4, 30)
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(60)  # высота строк
        self.ui.tableWidget.verticalHeader().hide()  # скрыть заголовки
        self.ui.tableWidget.horizontalHeader().hide()
        self.ui.tableWidget.setRowCount(0)


        for row_index, row in enumerate(records):
            self.ui.tableWidget.insertRow(row_index)
            
            checkbox_item = QtWidgets.QTableWidgetItem()
            checkbox_item.setData(QtCore.Qt.CheckStateRole, QtCore.Qt.Checked if row[2] else QtCore.Qt.Unchecked)
            checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            delegate = CheckBoxDelegate(QtGui.QPixmap("icon/icons8-checked-checkbox-96.png"), QtGui.QPixmap("icon/icons8-checked-checkbox-96 (1).png"), QtGui.QPixmap("icon/icons8-fire-80 (3).png"), QtGui.QPixmap("icon/icons8-fire-80 (1).png"))
            self.ui.tableWidget.setItemDelegateForColumn(0, delegate)
            self.ui.tableWidget.setItemDelegateForColumn(2, delegate)

            checkbox_item2 = QtWidgets.QTableWidgetItem()
            checkbox_item2.setCheckState(QtCore.Qt.Checked if row[4] else QtCore.Qt.Unchecked)
            checkbox_item2.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            self.ui.tableWidget.setItem(row_index, 5, QtWidgets.QTableWidgetItem(str(row[0])))
            self.ui.tableWidget.horizontalHeader().setSectionHidden(5, True) # скрыть 
            self.ui.tableWidget.setItem(row_index, 0, checkbox_item)
            self.ui.tableWidget.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row[1]))
            self.ui.tableWidget.setItem(row_index, 2, checkbox_item2)
            self.ui.tableWidget.setItem(row_index, 3, QtWidgets.QTableWidgetItem(perform_date(row[3])))

            button = QtWidgets.QPushButton()
            self.ui.tableWidget.setCellWidget(row_index, 4, button)
            button.clicked.connect(lambda _, row_index=row_index: self.delete_row(row_index))
            button.setStyleSheet("QPushButton {image: url(icon/icons8-full-trash-100.png);background-color: rgba(255, 255, 255, 0);} QPushButton:hover {image: url(icon/icons8-full-trash-100 (1).png);background-color: rgba(255, 255, 255, 0);}")
           
           
            button.setFixedSize(40, 60)

    def delete_row(self, row_index): # удаление
        value = self.ui.tableWidget.item(row_index, 5).text()
        b.delete_todo_by_id(value)
        self.table()

    def table(self):
        records = b.select_all() 

        self.fill_table(records)        
        self.ui.tableWidget.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        column = item.column()
        if column == 0:
            if item.checkState() == QtCore.Qt.Checked:
                row = item.row()
                
                item_id_item = self.ui.tableWidget.item(row, 5) 
                if item_id_item is not None:
                    item_id = item_id_item.text()
                    b.update_done_by_id(item_id, True)
                else:
                    print(f"None{row}")
            if item.checkState() == QtCore.Qt.Unchecked:
                row = item.row()
                
                item_id_item = self.ui.tableWidget.item(row, 5) 
                if item_id_item is not None:
                    item_id = item_id_item.text()
                    b.update_done_by_id(item_id, False)
                else:
                    print(f"None{row}")
        
        elif column == 1:
            row_index = item.row()
            new_text = item.text()
            id_5 = self.ui.tableWidget.item(row_index, 5).text()

            b.update_text_by_id(id_5, new_text)
    
        elif column == 2:
            if item.checkState() == QtCore.Qt.Checked:
                row = item.row()
                
                item_id_item = self.ui.tableWidget.item(row, 5) 
                if item_id_item is not None:
                    item_id = item_id_item.text()
                    b.update_important_by_id(item_id, True)
                else:
                    print(f"None{row}")
            if item.checkState() == QtCore.Qt.Unchecked:
                row = item.row()
                
                item_id_item = self.ui.tableWidget.item(row, 5) 
                if item_id_item is not None:
                    item_id = item_id_item.text()
                    b.update_important_by_id(item_id, False)
                else:
                    print(f"None{row}")

        elif column == 3:
            row_index = item.row()
            n_text = item.text()
            id_5 = self.ui.tableWidget.item(row_index, 5).text()
            if n_text == "":
                b.update_deadline_by_id(id_5)
            elif  b.update_deadline_by_id(id_5, n_text):
                b.update_deadline_by_id(id_5, n_text)
            else:
                self.att_win = attwindow("Неверный формат даты! Введите в формате '01/01/2023'.")
                self.att_win.show()

            



    def update_table(self): 
        self.ui.tableWidget.setRowCount(0)
        self.table()
    
    def button_clicked_exit(self):
        self.auth_window = authwindow()
        self.auth_window.show()
        self.close()

    def button_clicked_help(self):
        self.help_window = helpwindow()
        self.help_window.show()

class regwindow(QtWidgets.QMainWindow): # регистрация
    def __init__(self):
        super(regwindow, self).__init__()
        self.ui = Ui_RegWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_reg.clicked.connect(self.reg)  
        self.ui.pushButton_auth.clicked.connect(self.open_auth_window) #вернуться к авторизации

    def open_auth_window(self):
        self.auth_window = authwindow()
        self.auth_window.show()
        self.close()
    
    def reg(self):
        if self.ui.lineEdit_name.text() == "" or self.ui.lineEdit_log.text() == "" or self.ui.lineEdit_passw.text() == "":
            self.att_win = attwindow("Заполните все поля!")
            self.att_win.show()
        else:
            name = self.ui.lineEdit_name.text().strip()
            login = self.ui.lineEdit_log.text().strip()
            passw = self.ui.lineEdit_passw.text().strip()
            if not b.user_exist(login):
                b.new_user(name, login, passw)
                self.auth_window = authwindow()
                self.auth_window.show()
                self.close()
            else: 
                self.att_win = attwindow("Пользователь с таким логином существует!")
                self.att_win.show()
                self.ui.lineEdit_name.clear()
                self.ui.lineEdit_log.clear()
                self.ui.lineEdit_passw.clear()                


class authwindow(QtWidgets.QMainWindow): #авторизация
    def __init__(self):
        super(authwindow, self).__init__()
        self.ui = Ui_AuthWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_reg.clicked.connect(self.open_reg_window) 
        self.ui.pushButton_signin.clicked.connect(self.open_main_window)

    def open_main_window(self):
        if self.ui.lineEdit_log.text() == "" or self.ui.lineEdit_passw.text() == "":
            self.att_win = attwindow("Заполните все поля!")
            self.att_win.show()
        else:
            login = self.ui.lineEdit_log.text()
            passw = self.ui.lineEdit_passw.text()
            b.auth_user(login, passw) # обновляет переменные юзер и айди
            if b.authorised_user:
                self.main_window = mainwindow()
                self.main_window.show()
                self.close()
            else:
                self.att_win = attwindow("Такого пользователя не существует!")
                self.att_win.show()


    def open_reg_window(self):
        self.reg_window = regwindow()
        self.reg_window.show()
        self.close()


class attwindow(QtWidgets.QMainWindow): #всплывающие окна
    def __init__(self, text):
        super(attwindow, self).__init__()
        self.ui = Ui_AttWindow()
        self.ui.setupUi(self)
        self.ui.label_text.setText(text)
        self.ui.pushButton_ok.clicked.connect(self.att_window) 
    def att_window(self):
        self.close()

class helpwindow(QtWidgets.QMainWindow): #помощь
    def __init__(self):
        super(helpwindow, self).__init__()
        self.ui = Ui_HelpWindow()
        self.ui.setupUi(self)

class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, ic11, ic12, ic21, ic22, parent=None):
        super(CheckBoxDelegate, self).__init__(parent)
        self.ic11 = ic11
        self.ic12 = ic12
        self.ic21 = ic21
        self.ic22 = ic22

    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.CheckStateRole)
        column = index.column()
        checkbox_rect = option.rect
        checkbox_rect.setLeft(checkbox_rect.left() + 3)
        checkbox_rect.setRight(checkbox_rect.right() - 23)
        checkbox_rect.setTop(checkbox_rect.top() + 15)
        checkbox_rect.setBottom(checkbox_rect.bottom() - 15)

        if value == QtCore.Qt.Checked:
            if column == 0:
                pixmap = self.ic11
            else:
                pixmap = self.ic21
        else:
            if column == 0:
                pixmap = self.ic12
            else:
                pixmap = self.ic22
        pixmap = pixmap.scaled(48, 48, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        painter.drawPixmap(option.rect, pixmap)

def creat_app():
    app = QtWidgets.QApplication(sys.argv)
    win = authwindow()
    win.show()
    sys.exit(app.exec_())

creat_app()

b.close_connection() 

