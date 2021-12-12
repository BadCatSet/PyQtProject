import sqlite3
import sys
import time

from PIL import Image, ImageGrab
from PyQt5 import uic
from PyQt5.QtCore import QEvent, QLine, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QComboBox, QLabel, QLineEdit, \
    QMainWindow, QPlainTextEdit, QPushButton, QSpinBox, QStackedWidget, QStyledItemDelegate, \
    QTabWidget, QTableWidget, QTableWidgetItem, QWidget

import Psql


class MyImage(QLabel):
    def __init__(self, parent, image):
        super().__init__(parent)
        self.image_name = image
        self.setStyleSheet("""QLabel{border-image: url(?);}""".replace('?', image))


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return


class AdministratorLoginSignal(Exception):
    pass


class Item(QWidget):
    def __init__(self, par, dat):
        super().__init__(par)
        uic.loadUi('_item.ui', self)
        _vars = Psql.get_vars(con, item_id=dat[0])
        price = min([i[2] for i in _vars])
        self.picture.setStyleSheet(
            """QLabel{border-image: url(item_pic/?.png);}""".replace('?', str(_vars[0][0])))
        self.name.setText(dat[1])
        self.price.setText(str(price)+' руб.')
        self.dat = dat

    def mouseDoubleClickEvent(self, event):
        w_main.go_item(self.dat[0])


class WSignIn(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('_signin.ui', self)
        self.pb_signin.clicked.connect(self.run)
        w_main.w_login.setEnabled(False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def run(self):
        global USER_DATA
        if not Psql.get_user_by_username(con, self.le_username.text()):
            Psql.add_user(con, self.le_username.text(), self.le_password.text(),
                          self.le_name.text(),
                          self.le_surname.text(), self.le_phone.text(), self.le_adress.text())
            USER_DATA = Psql.get_user_by_data(con, self.le_username.text(), self.le_password.text())
            w_main.m_login.setText(cut_text(USER_DATA[1]))
            save_login_data(USER_DATA[1])
            w_main.i_buy.setEnabled(True)
            w_main.m_cart.setEnabled(True)
            self.close()
            w_main.w_login.close()
        else:
            self.statusBar().showMessage('эта почта уже занята!')

    def closeEvent(self, event):
        w_main.w_login.setEnabled(True)


class WLogIn(QMainWindow):
    w_sign_in: WSignIn

    le_username: QLineEdit
    le_password: QLineEdit
    pb_login: QPushButton
    pb_signin: QPushButton

    def __init__(self):
        super().__init__()
        uic.loadUi('_login.ui', self)
        self.pb_login.clicked.connect(self.run)
        self.pb_signin.clicked.connect(self.open_signin)
        self.le_username.setText(load_login_data())
        w_main.setEnabled(False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.le_password.setFocus()
        self.le_password.returnPressed.connect(self.run)

    def open_signin(self):
        self.w_sign_in = WSignIn()
        self.w_sign_in.show()

    def run(self):
        global USER_DATA
        res = Psql.get_user_by_data(con, self.le_username.text(), self.le_password.text())
        if res:
            save_login_data(res[1])
            if res[0] == 1:
                raise AdministratorLoginSignal
            USER_DATA = res
            w_main.m_login.setText(cut_text(USER_DATA[1]))
            w_main.i_buy.setEnabled(True)
            w_main.m_cart.setEnabled(True)
            self.close()
        else:
            self.statusBar().showMessage('что-то пошло не так!!')

    def closeEvent(self, event):
        w_main.setEnabled(True)


class WMain(QMainWindow):
    stackedWidget: QStackedWidget
    search_data: list
    search_pages_count: int
    w_login: WLogIn

    m_cart: QPushButton
    m_children: QPushButton
    m_current_page: QLabel
    m_first: QPushButton
    m_gender: QLine
    m_header: QLabel
    m_info: QLabel
    m_last: QPushButton
    m_login: QPushButton
    m_men: QPushButton
    m_next: QPushButton
    m_previous: QPushButton
    m_search_le: QLineEdit
    m_search_pb: QPushButton
    m_women: QPushButton

    c_address: QLineEdit
    c_comment: QPlainTextEdit
    c_home: QPushButton
    c_order: QPushButton
    c_tw: QTableWidget

    i_buy: QPushButton
    i_cart: QPushButton
    i_color: QComboBox
    i_description: QLabel
    i_home: QPushButton
    i_name: QLabel
    i_picture: QLabel
    i_price: QLabel
    i_size: QComboBox

    def __init__(self):
        super().__init__()
        uic.loadUi('_main_page.ui', self)
        self.setWindowIcon(QIcon('icon.gif'))

        self.search_wd = []
        self.other_vars = []
        self.current_var = ()
        self.blocker = False
        self.selected_gender = 'men'

        self.m_login.clicked.connect(self.open_login)
        self.m_search_pb.clicked.connect(self.update_search)

        self.m_men.clicked.connect(self.select_men)
        self.m_women.clicked.connect(self.select_women)
        self.m_children.clicked.connect(self.select_children)

        self.i_home.clicked.connect(self.go_home)
        self.c_home.clicked.connect(self.go_home)
        self.m_cart.clicked.connect(self.go_cart)
        self.i_cart.clicked.connect(self.go_cart)

        self.i_buy.clicked.connect(self.buy)
        self.c_order.clicked.connect(self.run_order)

        self.i_color.currentIndexChanged.connect(self.modify_color)
        self.i_size.currentIndexChanged.connect(self.modify_size)
        self.c_tw.itemChanged.connect(self.cart_amount_changed)

        self.m_cart.setIcon(QIcon('cart.png'))
        self.m_login.setIcon(QIcon('account.png'))
        self.m_login.setIconSize(QSize(20, 20))

        self.stackedWidget.setCurrentIndex(0)

        self.update_search()

    def update_search(self):
        self.search_data = \
            Psql.get_items(con, name=self.m_search_le.text(), gender=self.selected_gender)
        self.search_pages_count = int(len(self.search_data) / 4 + 0.999999)

        self.clear_widgets()
        for i, v in enumerate(self.search_data):
            res = Item(self, v)
            res.move(80 + 155 * (i % 4), 200 + 240 * (i // 4))
            res.show()
            self.search_wd.append(res)

    def go_item(self, item_id):
        w_main.blocker = True
        self.other_vars = Psql.get_vars(con, item_id=item_id)
        self.current_var = self.other_vars[0]
        self.clear_widgets()
        self.stackedWidget.setCurrentIndex(2)
        self.set_item_page()
        self.blocker = False

    def buy(self):
        if USER_DATA:
            item_id = self.current_var[0]
            order_id = Psql.get_cart_id(con, USER_DATA[0])
            Psql.add_order_item(con, order_id, item_id)
        else:
            self.statusBar().showMessage('необходимо войти!')

    def modify_color(self):
        if not self.blocker:
            self.blocker = True
            self.current_var = [x for x in self.other_vars if x[4] == self.i_color.currentText()][0]
            self.set_item_page()
            self.blocker = False

    def modify_size(self):
        if not self.blocker:
            self.blocker = True
            self.current_var = [x for x in self.other_vars if x[4] == self.current_var[4] and
                                str(x[3]) == self.i_size.currentText()][0]

            self.set_item_page()
            self.blocker = False

    def set_item_page(self):
        var = self.current_var
        item = Psql.get_items(con, item_id=var[1])[0]
        colors = {i[4] for i in self.other_vars}
        sizes = {str(i[3]) for i in self.other_vars if i[4] == var[4]}

        self.i_color.clear()
        self.i_color.addItems(list(colors))
        self.i_color.setCurrentText(var[4])

        self.i_size.clear()
        self.i_size.addItems(list(sizes))
        self.i_size.setCurrentText(str(var[3]))

        self.i_name.setText(str(item[1]))
        self.i_price.setText(str(var[2]) + ' руб.')
        self.i_description.setText(item[4])
        self.i_picture.setStyleSheet(
            """QLabel{border-image: url(item_pic/?.png);}""".replace('?', str(var[0])))

    def go_home(self):
        self.stackedWidget.setCurrentIndex(0)
        self.update_search()

    def go_cart(self):
        self.blocker = True
        self.clear_widgets()
        self.stackedWidget.setCurrentIndex(1)
        items = Psql.get_order_items(con, Psql.get_cart_id(con, USER_DATA[0]))

        self.c_tw.setColumnCount(5)
        self.c_tw.setRowCount(len(items))

        self.c_tw.setHorizontalHeaderLabels(
            ['картинка', 'название', 'размер', 'цвет', 'количество'])
        self.c_tw.verticalHeader().hide()

        for n, sou in enumerate(items):
            v = Psql.get_vars(con, var_id=sou[1])[0]
            i = Psql.get_items(con, item_id=v[1])[0]
            self.c_tw.setRowHeight(n, 100)

            self.c_tw.setCellWidget(n, 0, MyImage(self, f'item_pic/{v[0]}.png'))

            self.c_tw.setItem(n, 1, QTableWidgetItem(i[1]))
            self.c_tw.item(n, 1).setFlags(Qt.ItemIsSelectable)

            self.c_tw.setItem(n, 2, QTableWidgetItem(str(v[3])))
            self.c_tw.item(n, 2).setFlags(Qt.ItemIsSelectable)

            self.c_tw.setItem(n, 3, QTableWidgetItem(str(v[4])))
            self.c_tw.item(n, 3).setFlags(Qt.ItemIsSelectable)

            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, sou[2])
            self.c_tw.setItem(n, 4, item)

        self.blocker = False

    def cart_amount_changed(self):
        if not self.blocker:
            items = Psql.get_order_items(con, Psql.get_cart_id(con, USER_DATA[0]))
            for i in range(self.c_tw.rowCount()):
                now, last = int(self.c_tw.item(i, 4).text()), items[i][2]
                if now == 0:
                    Psql.delete_order_item_by_data(con, items[i][0], items[i][1])
                    self.go_cart()
                elif now < 1:
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, last)
                    self.c_tw.setItem(i, 4, item)
                elif now != last:
                    Psql.set_order_item_count(con, items[i][0], items[i][1], now)
                else:
                    continue
                break

    def run_order(self):
        order_id = Psql.get_cart_id(con, USER_DATA[0])
        comm = self.c_comment.document().toPlainText()
        address = self.c_address.text()

        Psql.set_order_status(con, order_id, 'paid')
        Psql.set_order_comm(con, order_id, comm)
        Psql.set_order_address(con, order_id, address)
        Psql.set_order_datetime(con, order_id)

        Psql.add_order(con, USER_DATA[0])
        self.go_home()

    def clear_widgets(self):
        for i in self.search_wd:
            i.setParent(None)
        self.search_wd.clear()

    def open_login(self):
        self.w_login = WLogIn()
        self.w_login.show()

    def select_men(self):
        self.selected_gender = 'men'
        self.update_search()
        self.select_to(475)

    def select_women(self):
        self.selected_gender = 'women'
        self.update_search()
        self.select_to(585)

    def select_children(self):
        self.selected_gender = 'children'
        self.update_search()
        self.select_to(690)

    def select_to(self, to):
        for i in range(self.m_gender.x(), to, (10 if self.m_gender.x() < to else -10)):
            self.m_gender.move(i, 100)
            self.repaint()
            time.sleep(0.01)
        self.m_gender.move(to, 100)


class WNewVar(QMainWindow):
    m_color: QComboBox
    m_label1: QLabel
    m_label2: QLabel
    m_label3: QLabel
    m_ok: QPushButton
    m_price: QSpinBox
    m_size: QSpinBox

    def __init__(self, item_id):
        super().__init__()
        uic.loadUi('_new_var.ui', self)
        self.item_id = item_id

        self.m_color.addItems([i for _, i in Psql.get_colors_dict(con).items()])
        self.m_ok.clicked.connect(self.ok)

    def ok(self):
        color = self.m_color.currentText()
        size = self.m_size.text()
        price = self.m_price.text()
        if not Psql.get_vars(con, item_id=self.item_id, color=color, size=size):
            Psql.add_var(con, self.item_id, color, size, price)
            var_id = Psql.get_vars(con, item_id=self.item_id, color=color, size=size)[0][0]
            Image.new('RGB', (10, 10)).save(f'item_pic/{var_id}.png')
            self.hide()


class WAdminItem(QMainWindow):
    w_new_var: WNewVar

    m_add: QPushButton
    m_paste: QPushButton
    m_tw: QTableWidget

    def __init__(self, item_id):
        super().__init__()
        uic.loadUi('_admin_item.ui', self)

        item = Psql.get_items(con, item_id=item_id)[0]
        self.item_id = item_id

        self.setWindowTitle('Changing item with name:   ' + item[1])

        delegate = ReadOnlyDelegate(self.m_tw)
        self.m_tw.setColumnCount(6)
        self.m_tw.setHorizontalHeaderLabels(['var_id', 'picture', 'color', 'size', 'price', 'del'])
        self.m_tw.setItemDelegateForColumn(0, delegate)
        self.m_tw.verticalHeader().hide()
        self.m_tw.setColumnWidth(0, 50)

        self.load_vars()

        self.m_paste.clicked.connect(self.paste_picture)
        self.m_add.clicked.connect(self.new_var)

    def load_vars(self):
        _vars = Psql.get_vars(con, item_id=self.item_id)
        colors = [i for _, i in Psql.get_colors_dict(con).items()]
        self.m_tw.setRowCount(len(_vars))
        for n, v in enumerate(_vars):
            self.m_tw.setRowHeight(n, 100)

            color = QComboBox(self)
            color.var_id = v[0]
            color.addItems(colors)
            color.setCurrentText(v[4])
            color.currentTextChanged.connect(self.change_color)

            size = QSpinBox(self)
            size.var_id = v[0]
            size.setRange(24, 45)
            size.setValue(v[3])
            size.valueChanged.connect(self.change_size)

            price = QSpinBox(self)
            price.var_id = v[0]
            price.setRange(500, 100000)
            price.setValue(v[2])
            price.valueChanged.connect(self.change_price)

            del_button = QPushButton(self)
            del_button.var_id = v[0]
            del_button.setIcon(QIcon('delete.png'))
            del_button.clicked.connect(self.delete_var)

            self.m_tw.setItem(n, 0, QTableWidgetItem(str(v[0])))
            self.m_tw.setCellWidget(n, 1, MyImage(self, f'item_pic/{v[0]}.png'))
            self.m_tw.setCellWidget(n, 2, color)
            self.m_tw.setCellWidget(n, 3, size)
            self.m_tw.setCellWidget(n, 4, price)
            self.m_tw.setCellWidget(n, 5, del_button)

    def delete_var(self):
        if self.m_tw.rowCount() > 1:
            Psql.delete_var_and_connected(con, self.sender().var_id)
            self.load_vars()
        else:
            self.statusBar().showMessage('you could not delete last var!')

    def change_color(self):
        Psql.set_var_color(con, self.sender().var_id, self.sender().currentText())

    def change_size(self):
        Psql.set_var_size(con, self.sender().var_id, self.sender().value())

    def change_price(self):
        Psql.set_var_price(con, self.sender().var_id, self.sender().value())

    def new_var(self):
        self.w_new_var = WNewVar(self.item_id)
        self.w_new_var.show()

    def paste_picture(self):
        var_id = self.m_tw.item(self.m_tw.currentRow(), 0).text()
        save_clipboard_picture(f'item_pic/{var_id}.png')
        self.load_vars()


class WAdmin(QMainWindow):
    tabWidget: QTabWidget
    w_admin_item: WAdminItem

    o_apply: QPushButton
    o_set_stat: QComboBox
    o_tw: QTableWidget

    i_brand: QComboBox
    i_gender: QComboBox
    i_refresh: QPushButton
    i_search: QLineEdit
    i_tw: QTableWidget

    u_refresh: QPushButton
    u_search: QLineEdit
    u_tw: QTableWidget

    def __init__(self):
        super().__init__()
        uic.loadUi('_admin.ui', self)

        self.poss_st = Psql.get_statuses_dict(con)
        self.o_set_stat.addItems(self.poss_st.values())

        self.o_tw.setColumnCount(4)
        self.o_tw.setHorizontalHeaderLabels(['order_id', 'username', 'datetime', 'status'])
        self.o_tw.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.i_tw.setColumnCount(8)
        self.i_tw.setHorizontalHeaderLabels(
            ['item_id(edit)', 'picture', 'name', 'brand', 'gender', 'description', 'delete', 'ok'])
        delegate = ReadOnlyDelegate(self.i_tw)
        self.i_tw.setItemDelegateForColumn(0, delegate)
        self.i_tw.viewport().installEventFilter(self)
        self.i_tw.verticalHeader().hide()

        self.u_tw.setColumnCount(7)
        self.u_tw.setHorizontalHeaderLabels(
            ['user_id', 'username', 'password', 'name', 'surname', 'phone', 'address'])
        self.u_tw.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.i_brand.addItems(['unset'] + [i for _, i in Psql.get_brands_dict(con).items()])
        self.i_gender.addItems(['unset'] + [i for _, i in Psql.get_genders_dict(con).items()])

        self.load_orders()
        self.load_items()
        self.load_users()

        self.o_apply.clicked.connect(self.apply_st)

        self.i_refresh.clicked.connect(self.load_items)
        self.u_refresh.clicked.connect(self.load_users)

        self.i_refresh.setIcon(QIcon('refresh.png'))
        self.u_refresh.setIcon(QIcon('refresh.png'))

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonDblClick and source is self.i_tw.viewport():
            if self.i_tw.itemAt(event.pos()).column() == 0:
                row = self.i_tw.itemAt(event.pos()).row()
                self.w_admin_item = WAdminItem(self.i_tw.item(row, 0).text())
                self.w_admin_item.show()
        return super(WAdmin, self).eventFilter(source, event)

    def apply_st(self):
        status_id = self.o_set_stat.currentText()
        selected = self.o_tw.selectedItems()
        for curr_it in selected:
            order_id = self.o_tw.item(curr_it.row(), 0).text()
            Psql.set_order_status(con, order_id, status_id)
        if selected:
            self.load_orders()

    def load_orders(self):
        res = Psql.get_orders(con)
        self.o_tw.setRowCount(len(res))
        for n, v in enumerate(res):
            self.o_tw.setItem(n, 0, QTableWidgetItem(str(v[0])))
            self.o_tw.setItem(n, 1, QTableWidgetItem(str(Psql.get_user_by_id(con, v[1])[1])))
            self.o_tw.setItem(n, 2, QTableWidgetItem(str(v[2])))
            self.o_tw.setItem(n, 3, QTableWidgetItem(str(v[3])))

    def load_items(self):
        res = Psql.get_items(con, self.i_search.text(),
                             self.i_brand.currentText(), self.i_gender.currentText())
        brands = [i for _, i in Psql.get_brands_dict(con).items()]
        genders = [i for _, i in Psql.get_genders_dict(con).items()]
        self.i_tw.setRowCount(len(res))
        for n, v in enumerate(res):
            self.i_tw.setRowHeight(n, 100)

            pic = f'item_pic/{Psql.get_vars(con, item_id=v[0])[0][0]}.png'

            name = QLineEdit(self)
            name.row = n
            name.setText(v[1])
            name.textChanged.connect(self.set_edited)

            brand = QComboBox(self)
            brand.row = n
            brand.addItems(brands)
            brand.setCurrentText(v[2])
            brand.currentTextChanged.connect(self.set_edited)

            gender = QComboBox(self)
            gender.row = n
            gender.addItems(genders)
            gender.setCurrentText(v[3])
            gender.currentTextChanged.connect(self.set_edited)

            desc = QPlainTextEdit(self)
            desc.row = n
            desc.document().setPlainText(v[4])
            desc.textChanged.connect(self.set_edited)

            del_button = QPushButton(self)
            del_button.row = n
            del_button.setIcon(QIcon('delete.png'))
            del_button.clicked.connect(self.delete_item)

            ok_button = QPushButton(self)
            ok_button.item_id = v[0]
            ok_button.row = n
            ok_button.setIcon(QIcon('ok.png'))
            ok_button.clicked.connect(self.ok_item)

            self.i_tw.setItem(n, 0, QTableWidgetItem(str(v[0])))
            self.i_tw.setCellWidget(n, 1, MyImage(self, pic))
            self.i_tw.setCellWidget(n, 2, name)
            self.i_tw.setCellWidget(n, 3, brand)
            self.i_tw.setCellWidget(n, 4, gender)
            self.i_tw.setCellWidget(n, 5, desc)
            self.i_tw.setCellWidget(n, 6, del_button)
            self.i_tw.setCellWidget(n, 7, ok_button)

    def set_edited(self):
        row = self.sender().row
        self.i_tw.cellWidget(row, 7).setIcon(QIcon('edited.png'))

    def delete_item(self):
        item_id = self.sender().item_id
        print(item_id)

    def ok_item(self):
        n = self.sender().row
        item_id = self.sender().item_id
        name = self.i_tw.cellWidget(n, 2).text()
        brand = self.i_tw.cellWidget(n, 3).currentText()
        gender = self.i_tw.cellWidget(n, 4).currentText()
        desc = self.i_tw.cellWidget(n, 5).document().toPlainText()

        Psql.set_item_name(con, item_id, name)
        Psql.set_item_brand(con, item_id, brand)
        Psql.set_item_gender(con, item_id, gender)
        Psql.set_item_desc(con, item_id, desc)
        self.i_tw.cellWidget(n, 7).setIcon(QIcon('ok.png'))

    def load_users(self):
        res = Psql.get_users(con, name=self.u_search.text())
        self.u_tw.setRowCount(len(res))
        for n, v in enumerate(res):
            for i in range(7):
                self.u_tw.setItem(n, i, QTableWidgetItem(str(v[i])))


def save_login_data(data):
    with open('login_data.txt', mode='wt', encoding='utf-8') as file:
        file.write(data)


def load_login_data():
    with open('login_data.txt', encoding='utf-8') as file:
        res = file.read()
    return res


def get_key_fr_value(d: dict, value):
    if value in d.values():
        return list(d.keys())[list(d.values()).index(value)]


def cut_text(t, le=8):
    if len(t) > le:
        return t[:le - 2] + '..'
    return t


def save_clipboard_picture(path):
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        print('saved!')
        im.save(path)


def excepthook(exc_type, value, traceback):
    global do_admin
    if exc_type is AdministratorLoginSignal:
        do_admin = True
        w_main.w_login.hide()
        w_main.hide()
        app.exit()
    else:
        print(exc_type, value, traceback)
        raise Exception


if __name__ == '__main__':
    con = sqlite3.connect('shop_db.db')
    sys.excepthook = excepthook
    do_admin = False

    USER_DATA = ()

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    w_main = WMain()
    w_main.show()
    app.exec()
    if do_admin:
        w_admin = WAdmin()
        w_admin.show()
        app.exec()
    con.close()
