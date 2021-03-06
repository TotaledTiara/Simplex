from PyQt5.QtWidgets import (QMainWindow, QDialog, QWidget, QAction, QApplication, QLabel, QDialogButtonBox,
                             QGridLayout, QPushButton, QComboBox, QLineEdit, QFileDialog, QStyle, QFrame)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtCore

from fractions import Fraction
import copy
import sys


class Simplex(QDialog):
    def __init__(self, matrix):
        super().__init__()
        self.title = 'Вычисление'
        self.matrix = matrix
        self.history_matrix = []
        self.history_col_x = []
        self.history_row_x = []
        self.history_simplex_state = []

        self.simplex_flag = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.prew_button = QPushButton("Назад")
        self.prew_button.setEnabled(False)
        self.prew_button.clicked.connect(self.prew)

        self.next_button = QPushButton("Далее")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.calculation_in_main_line)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.prew_button, 0, 0)
        self.grid.addWidget(self.next_button, 0, 1)

        self.main_line = self.matrix.pop(0)  # Главная строка
        self.main_cells = []
        self.main_cell = []

        self.row_x = [x+1 for x in range(len(self.matrix[0])-1)]  # Список иксов по горизонтали
        self.col_x = [x+len(self.row_x)+1 for x in range(len(self.matrix))]  # Список иксов по вертикали

        self.starting_grid()
        self.rendering_designations()
        self.searching_of_main()
        self.rendering_grid()

    def rendering_designations(self):
        for i, value in enumerate(self.row_x):  # Заполнение x-сами по горизонтали
            self.label = QLabel('x' + str(value))
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            self.grid.addWidget(self.label, 1, i+1)
        for i, value in enumerate(self.col_x):  # Заполнение x-сами по вертикали
            self.label = QLabel('x' + str(value))
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            self.grid.addWidget(self.label, i+2, 0)

    def starting_grid(self):
        last_line = [Fraction(0) for _ in range(len(self.matrix[0]))]
        for i in self.matrix:  # Сложение строк матрицы
            last_line = [last_line[j] + i[j] for j in range(len(i))]
        for i in range(len(last_line)):  # Смена знака строки
            last_line[i] *= -1
        self.matrix.append(last_line)  # Добавление последней строки в конец

    def searching_of_main(self):
        j_i = []
        negative = False
        for i, val in enumerate(self.matrix[-1][:-1]):
            if val < 0:
                j_i.append(i)
            if val <= 0:
                negative = True

        if negative:
            for j in j_i:
                minimum = 100000
                min_index = []
                for i in range(len(self.matrix)-1):
                    try:
                        if minimum > (self.matrix[i][-1] / self.matrix[i][j]) and self.matrix[i][j] > 0:
                            minimum = self.matrix[i][-1] / self.matrix[i][j]
                            min_index = [i,j]
                    except:
                        continue
                self.main_cells.append(min_index)
            y_i = []
        else:
            if not self.simplex_flag:
                print('Нерешаемо!')

    def rendering_grid(self):
        for i, line in enumerate(self.matrix):
            for j, value in enumerate(line):
                self.btn = QPushButton('{}'.format(value))
                if [i,j] in self.main_cells:
                    self.btn.setStyleSheet('background-color: #00FFFF')
                    self.btn.clicked.connect(lambda checked, i=i, j=j: self.next(i,j))
                self.grid.addWidget(self.btn, i+2, j+1)
        self.main_cells = []

    def calculate(self):
        new_matrix = []
        st = []
        for i in self.matrix:  # TODO: Сделать нормальное копирование списка
            for j in i:
                st.append(j)
            new_matrix.append(st)
            st = []
        i, j = self.main_cell
        new_matrix[i][j] = 1 / self.matrix[i][j]  # Изменение опорного элемента

        for index, _ in enumerate(self.matrix[i]):  # Изменение значений в опорной строке
            if index != j:
                new_matrix[i][index] *= new_matrix[i][j]

        for index_i, string in enumerate(self.matrix):  # Изменение значений в опорном столбце
            if index_i != i:
                for index_j, _ in enumerate(string):
                    if index_j == j:
                        new_matrix[index_i][index_j] *= (new_matrix[i][j] * -1)

        for index_i, string in enumerate(self.matrix):  # Изменения оставшихся значений матрицы
            if index_i != i:
                for index_j, _ in enumerate(string):
                    if index_j != j:
                        new_matrix[index_i][index_j] = self.matrix[index_i][index_j] - (new_matrix[i][index_j] * self.matrix[index_i][j])
        self.matrix = new_matrix

    def delete_column(self):  # Удаление опорного столбца
        self.col_x[self.main_cell[0]] = self.row_x[self.main_cell[1]]
        del self.row_x[self.main_cell[1]]
        for string in self.matrix:
            del string[self.main_cell[1]]

    def clear_grid(self):
        for i in reversed(range(self.grid.count())):  # Чистим сетку
            if i != 0 and i != 1:
                self.grid.itemAt(i).widget().setParent(None)

    def prew(self):
        self.next_button.setEnabled(False)
        self.matrix = copy.deepcopy(self.history_matrix[-1])
        self.row_x = copy.deepcopy(self.history_row_x[-1])
        self.col_x = copy.deepcopy(self.history_col_x[-1])
        self.simplex_flag = copy.deepcopy(self.history_simplex_state[-1])

        del self.history_matrix[-1]
        del self.history_row_x[-1]
        del self.history_col_x[-1]
        del self.history_simplex_state[-1]

        if len(self.history_matrix) > 0:
            self.prew_button.setEnabled(True)
        else:
            self.prew_button.setEnabled(False)

        self.clear_grid()
        self.rendering_designations()
        self.searching_of_main()
        self.rendering_grid()

    def next(self, i='placeholder', j='placeholder'):
        self.add_history()
        self.main_cell = [i, j]

        flag = False
        for i in self.matrix[-1][:-1]:
            if i < 0:
                flag = True
                break
        if flag == True:
            self.clear_grid()
            self.calculate()
            if self.col_x[self.main_cell[0]] not in [i+1 for i in range(len(self.main_line) - 1)]:
                self.delete_column()
            else:
                self.col_x[self.main_cell[0]], self.row_x[self.main_cell[1]] = self.row_x[self.main_cell[1]], self.col_x[self.main_cell[0]]
            self.rendering_designations()
            self.searching_of_main()
            self.rendering_grid()
            if len(self.history_matrix) > 0:
                self.prew_button.setEnabled(True)
            else:
                self.prew_button.setEnabled(False)

        if not self.simplex_flag:
            flag = True
            for i in self.matrix[-1][:-1]:
                if i != 0:
                    flag = False
                    break
            if flag:
                self.next_button.setEnabled(True)
        else:
            flag = True
            for i in self.matrix[-1][:-1]:
                if i < 0:
                    flag = False
                    break
            if flag:
                self.next_button.setEnabled(True)


    def add_history(self):
        self.history_matrix.append(copy.deepcopy(self.matrix))
        self.history_row_x.append(copy.deepcopy(self.row_x))
        self.history_col_x.append(copy.deepcopy(self.col_x))
        self.history_simplex_state.append(copy.deepcopy(self.simplex_flag))


    def calculation_in_main_line(self):
        self.simplex_flag = True
        self.clear_grid()
        ln = len(self.main_line)-1
        xn = {}
        for i, value in enumerate(self.col_x):
            x = [0 for _ in range(ln)]
            for j, val in enumerate(self.matrix[i][:-1]):
                x[self.row_x[j]-1] = val * -1
            x.append(self.matrix[i][-1])
            xn.update({value : x})
        final_string = [0 for _ in range(len(self.main_line))]  # Все х и свободный член

        for index, value in enumerate(self.main_line):
            if index+1 in xn:
                for i, val in enumerate(xn[index+1]):
                    final_string[i] += value * val
            else:
                final_string[index] += value

        fl = False
        for i in final_string:
            if i > 0:
                fl = True

        if fl == False:
            self.rendering_designations()
            self.rendering_grid()
            self.output(final_string, xn)
        else:
            self.next_button.setEnabled(False)
            for i, x in enumerate(self.row_x):
                self.matrix[-1][i] = final_string[x-1] * -1
            self.matrix[-1][-1] = final_string[-1]
            self.rendering_designations()
            self.searching_of_main()
            self.rendering_grid()

            flag = False

            for i in self.matrix[-1][:-1]:
                if i < 0:
                    flag = True
                    self.simplex_flag = True
                    break
            if flag == False:
                self.output(final_string, xn)

    def output(self, final_string, xn):
        x = [0 for _ in range(len(final_string)-1)]
        for key, value in xn.items():
            x[key-1] = value[-1]
        x_string = ''
        for i, val in enumerate(x):
            if i == len(x)-1:
                x_string += str(val)
            else:    
                x_string += (str(val)) + ', '

        self.label_f = QLabel(f'F* = {final_string[-1]}')
        self.label_x = QLabel(f'x* = ({x_string})')
        self.grid.addWidget(self.label_f)
        self.grid.addWidget(self.label_x)
        self.next_button.setEnabled(False)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Симплекс-метод'
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.statusBar().showMessage('')

        self.widget = QWidget()
        self.grid = QGridLayout()
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)

        self.comboBox_var = QComboBox()
        self.comboBox_var.addItems(["3", "4", "5", "6", "7"])
        self.comboBox_var.activated.connect(self.combo_input)
        self.grid.addWidget(self.comboBox_var, 0, 0)

        self.comboBox_str = QComboBox()
        self.comboBox_str.addItems(["2", "3", "4", "5", "6"])
        self.comboBox_str.activated.connect(self.combo_input)
        self.grid.addWidget(self.comboBox_str, 0, 1)

        self.btn = QPushButton("OK")
        self.btn.clicked.connect(self.read_line)
        self.grid.addWidget(self.btn, 0, 2)

        self.advice_btn = QPushButton("Справка")
        self.advice_btn.clicked.connect(self.advice)
        self.grid.addWidget(self.advice_btn, 0, 3)

        for i in range(3):
            self.label = QLabel('x'+ '{}'.format(i+1))
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            self.grid.addWidget(self.label, 1, i)

        for i in range(3):
            for j in range(4):
                self.inp = QLineEdit()
                if i == 0:
                    self.inp.setStyleSheet('background-color: #98FB98')
                self.inp.setAlignment(QtCore.Qt.AlignCenter)
                self.grid.addWidget(self.inp, i+2, j)

    def combo_input(self):
        if (int(self.comboBox_var.currentText()) - int(self.comboBox_str.currentText())) >= 1:
            self.statusBar().showMessage('')
            for i in reversed(range(self.grid.count())):  # Чистим сетку
                if i != 0 and i != 1 and i != 2 and i != 3:
                    self.grid.itemAt(i).widget().setParent(None)

            for i in range(int(self.comboBox_var.currentText())):  # Добавляем иксы 
                self.label = QLabel('x'+ '{}'.format(i+1))
                self.label.setAlignment(QtCore.Qt.AlignCenter)
                self.grid.addWidget(self.label, 1, i)

            for j in range(int(self.comboBox_str.currentText())+1):  # Строим сетку
                for i in range(int(self.comboBox_var.currentText())+1):
                    self.inp = QLineEdit()
                    if j == 0:
                        self.inp.setStyleSheet('background-color: #98FB98')
                    self.grid.addWidget(self.inp, j+2, i)
        else:
            self.statusBar().showMessage('Нельзя!')

    def read_line(self):  # Чтение из строк и запись значений в матрицу
        def isdigit(string):
            if string.isdigit():
               return True
            else:
                try:
                    float(string)
                    return True
                except ValueError:
                    return False

        n = [x for x in range(0, int(self.comboBox_var.currentText())+4)]  # Кол-во элементов не из матрицы
        matrix = []
        string = []
        for i in range(self.grid.count()):
            if i not in n:
                if self.grid.itemAt(i).widget().text().find('/') > -1:
                    string.append(Fraction(self.grid.itemAt(i).widget().text()))
                elif self.grid.itemAt(i).widget().text().find('.') > -1:
                    string.append(Fraction(self.grid.itemAt(i).widget().text()))
                elif isdigit(self.grid.itemAt(i).widget().text()):
                    string.append(Fraction(int(self.grid.itemAt(i).widget().text())))
                else:
                    self.statusBar().showMessage('Недопустимые символы!')
                    return
            if len(string) == int(self.comboBox_var.currentText()) + 1:
                matrix.append(string)
                string = []
        self.statusBar().showMessage('')
        self.calculate(matrix)

    def calculate(self, matrix):  # Вычисление
        dialog = Simplex(matrix)
        dialog.exec_()

    def advice(self):
        spravka = Advice()
        spravka.exec_()


class Advice(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Справка'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.one_s= 'Справочная информация\n'
        self.two_s = 'Лабораторная работа использует метод искусственного базиса для решения уравнения(решается задача на максимум).'
        self.three_s = 'Зелёным цетом выделена целеваю функция. Остальные строки предназначены для заполнения их коэффициентами ограничений.'
        self.four_s = 'Предполагается, что свободнй член уже находится в правой части уравнения!'

        self.one = QLabel(self.one_s)
        self.two = QLabel(self.two_s)
        self.three = QLabel(self.three_s)
        self.four = QLabel(self.four_s)

        self.grid.addWidget(self.one, 0, 2, 1,1)
        self.grid.addWidget(self.two, 1, 0, 1,5)
        self.grid.addWidget(self.three, 2, 0, 1,5)
        self.grid.addWidget(self.four, 3, 0, 1,5)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
