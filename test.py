import sys
import requests
import os
import textwrap

from itertools import product
from random import choice, randint
from copy import deepcopy

from PIL import Image
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon
from PyQt5.QtCore import QSize, Qt


class WindowMaker(QMainWindow):
    def __init__(self, ui, background_image):
        super().__init__()
        try:
            exist_check = open(background_image, 'rb')
            exist_check.close()
            exist_check = open('icon.png', 'rb')
            exist_check.close()
            exist_check = open(ui, 'rb')
            exist_check.close()
        #Здесь действия на случай, если чего-то не хватает для запуска
        except:
            response = self.lookForUpdates(1)
            if response == [2]:
                sys.exit()
                return None
        uic.loadUi(ui, self)
        self.pre_image = QImage(background_image)
        self.background = QPalette()
        self.setPalette(self.background)
        self.setWindowIcon(QIcon('icon.png'))
        with Image.open(background_image) as img:
            width, height = img.size
        self.aspect_ratio = width / height

    def resizeEvent(self, event):
        self.post_image = self.pre_image.scaled(self.size(),
                                                Qt.KeepAspectRatioByExpanding,
                                                transformMode = Qt.SmoothTransformation)
        self.background.setBrush(QPalette.Window, QBrush(self.post_image))
        self.setPalette(self.background)
        self.setFixedHeight(int(self.width() / self.aspect_ratio))
        
    #Обработчик мышки
    def mousePressEvent(self, event):
        self.nextWindow()

    #Обработчик клавиатуры
    def keyPressEvent(self, event):
        #При нажатии на клавишу enter переход на домашнюю страницу
        if event.key() == Qt.Key_Return:
            self.confirm()
        #При нажатии на клавишу esc выход из приложения
        elif event.key() == Qt.Key_Escape:
            self.back()

    #Проверка обновлений
    def lookForUpdates(self, download=0):
        #Отслеживаем возникновение ошибок
        response = []
        
        #Пытаемся получить актуальную версию с гитхаба и скачать все недостающие обязательные компоненты
        try:
            git_version = requests.get('https://raw.githubusercontent.com/skezixxx/Project/refs/heads/main/version.txt').text
            #Скачиваем недостающие элементы
            if download:
                queue = sorted(list(set(map(lambda x: x.strip().strip('!'),
                                            filter(lambda x: x.strip().startswith('!'),
                                                   git_version.split('\n')[2:]))) - set(os.listdir(os.path.dirname(os.path.abspath(__file__))))))
                for i in queue:
                    i = i.strip()
                    try:
                        with open(i, 'wb') as file:
                            file.write(requests.get(f'https://raw.githubusercontent.com/skezixxx/Project/refs/heads/main/{i}').content)
                    except:
                        print(f'Something went wrong with {i}')
                        download = 2
                if download != 2:
                    download = 0
        #Здесь диалог на случай, если не удалось её получить
        except:
            if self.throwDialogue('Не удалось обновить приложение',
                                       icon='warning',
                                       text='Не удалось обновить приложение. Проверьте подключение к интернету',
                                       informative_text='Повторить попытку?',
                                       detailed_text='Ваша версия приложения устарела или были утеряны важные файлы. Проблема исправится автоматически при повторном подключении к интернету') == QMessageBox.StandardButton.Yes:
                self.lookForUpdates(download)
                return [1]
            else:
                self.close()
                return [2]

        #Пытаемся узнать нашу версию с компа
        try:
            self.version = open('version.txt', 'r').read()
        #Здесь действия на случай, если версию узнать не удалось
        except:
            response.append('''version.txt doesn't exist''')

        #Сравниваем версии, если смогли их получить
        if not response and git_version.split('\n')[0].strip() != self.version.split('\n')[0].strip():
            response.append('''programme version is outdated''')
        elif not response and git_version.split('\n')[0].strip() == self.version.split('\n')[0].strip() and download:
            response.append('''some files are broken''')

        #Возвращаем список ответов наших попыток
        return response

    def throwDialogue(self, title, icon=None,
                      text=None, informative_text=None,
                      detailed_text=None,
                      buttons='QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No'):
        dialogue = QMessageBox(self)
        dialogue.setWindowTitle(title)
        dialogue.setText(text)
        dialogue.setInformativeText(informative_text)
        dialogue.setDetailedText(detailed_text)
        exec(f'dialogue.setStandardButtons({buttons})')
        exec(f'dialogue.setIcon(QMessageBox.Icon.{icon.capitalize()})')
        choice = dialogue.exec()
        return choice

    # Запуск второго окна
    def nextWindow(self, classname=None, ui=None, background_image=None):
        if classname and ui and background_image:
            exec(f'self.next_window = {classname}(ui, background_image)')
            self.next_window.show()
        self.close()

    #Если нажали esc
    def back(self):
        print(1)
        self.close()

    #Если нажали enter
    def confirm(self):
        self.nextWindow()


class Greet(WindowMaker):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        value = self.width() // 100 + 8
        self.label.setStyleSheet(f'font-size: {value * 2}px; color: white; padding-left: {int(value ** 1.5) * 7}px')

    def mousePressEvent(self, event):
        self.confirm()
        
    def confirm(self):
        self.nextWindow('Main', 'main.ui', 'main.png')


class Main(WindowMaker):
    def __init__(self, ui, background_image):
        super().__init__(ui, background_image)
        self.comboBox.setStyleSheet('background: #1D3633; color: white; border: 1px #1D3633 solid')
        self.pushButton.setStyleSheet('background: #B4E6B6; color: #1D3633; padding: 10px 30px; border: 1px #B4E6B6 solid; border-radius: 15px')
        self.pushButton.clicked.connect(self.confirm)
        for filename in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks')):
            if filename.endswith('.txt'):
                self.comboBox.addItem(filename.rstrip('.txt'))

    def confirm(self):
        self.next_window = Workspace('workspace.ui',
                                     'workspace.png',
                                     f'{self.comboBox.currentText()}.txt')
        self.close()

    def back(self):
        self.nextWindow('Greet', 'greet.ui', 'greet.png')

    def mousePressEvent(self, event):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        value = self.width() // 100 + 4
        self.pushButton.setStyleSheet(f'background: #B4E6B6; color: #1D3633; padding: 10px 30px; border: 1px #B4E6B6 solid; border-radius: 15px; font-size: {value * 2}px;')


class Workspace(WindowMaker):
    def con(self):
        self.next_window = Condition('condition.ui', 'condition.png',
                                     self.condition)
        self.next_window.show()
    
    def __init__(self, ui, background_image, task):
        super().__init__(ui, background_image)
        self.pushButton.setStyleSheet('background: #FA9800; color: white; padding: 10px 30px; border: 1px solid #FA9800; border-radius: 15px;')
        self.textEdit.setHtml('''<!DOCTYPE html>
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; text-decoration: bold}
</style></head><body style="font-family: 'Courier New'; font-size: 12pt; font-weight: 600; font-style: normal">
<code><p style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-block-indent: 0; text-indent: 0px"><span style="font-family: 'Courier New'; font-size: 12pt"></span></p></code></body></html>''')
        self.textEdit.setStyleSheet('background: #4472C4; color: white; border: 2px white solid')
        self.label.setStyleSheet('color: white')
        self.pushButton_3.clicked.connect(self.con)
        self.pushButton_4.clicked.connect(self.back)
        self.testlist = None
        self.pushButton.clicked.connect(self.confirm)
        self.textEdit.textChanged.connect(self.labelClear)
        try:
            file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks', task), 'r', encoding='utf-8')
            self.task = file.readlines()
            self.task[-1] += '\n'
            file.close()
            for test_part in ['condition', 'answer', 'example', 'tests']:
                first_value = self.task.index('`\n')
                self.task.pop(first_value)
                second_value = self.task.index('`\n')
                self.task.pop(second_value)
                task_part = []
                for line in range(first_value + 1, second_value):
                    task_part.append(self.task[line])
                task_part[-1] = task_part[-1].rstrip()
                exec(f"""self.{test_part} = '''{"".join(task_part)}'''""")
        except Exception as e:
            print('Файл с задачей повреждён или был удалён или переименован незадолго до открытия окна. Пожалуйста, перезапустите приложение. Задачу придётся скачать заново')
            sys.exit()
            return None
        #Теперь существуют self.condition, self.answer, self.example и self.tests
        self.show()
        
    def confirm(self):
        self.label.setText('Тестируем...')
        if self.testlist == None:
            exec(self.tests)
            self.answer = self.answer.replace('print(', 'self.testprint(temp_file, ').replace('input(', 'self.testinput(self.testlist_2[test_variables], temp_file, ').replace(', )', ')')
        self.code = self.textEdit.toPlainText()
        self.printTestSystem()

    def labelClear(self):
        self.label.setText('Результат')

    #Крайне примитивная система проверки задач, результатом которых является печать. Возвращает ответ тестов
    def printTestSystem(self):
        self.lenght = len(self.testlist)
        self.testlist_1 = deepcopy(self.testlist)
        self.testlist_2 = deepcopy(self.testlist)
        self.code = f'''try:
{textwrap.indent(self.code, '    ')}
    self.result = 'OK'
except Exception as e:
    self.result = (str(e))'''.replace('print(', 'self.testprint(temp_file, ').replace('input(', 'self.testinput(self.testlist_1[test_variables], temp_file, ').replace(', )', ')')
        with open('temp.txt', 'w', encoding='utf-8') as temp_file:
            for test_variables in range(len(self.testlist)):
                exec(self.code)
            temp_file.write('\n')
            for test_variables in range(len(self.testlist)):
                exec(self.answer)
        with open('temp.txt', 'r', encoding='utf-8') as temp_file:
            lines = temp_file.readlines()
        if len(list(filter(lambda x: x.strip(), lines))) < self.lenght * 2:
            self.label.setText('Не все выводы выполнены')
        elif len(list(filter(lambda x: x.strip(), lines))) > self.lenght * 2:
            self.label.setText('Выводов слишком много')
        else:
            for i in range(self.lenght):
                if lines[i] != lines[i + 1 + self.lenght]:
                    self.label.setText('Некоторые тесты некорректны')
                    break
            else:
                self.label.setText('OK')
                
    def mousePressEvent(self, event):
        pass

    def testprint(self, *args, sep=' ', end='\n', file=None, flush=False):
       try:
           args = list(args)
           file = args.pop(0)
           file.write(sep.join(list(map(str, args))) + end)
           return None
        except:
            pass

    def testinput(self, li, temp_file, prompt=''):
        if prompt:
            self.testprint(temp_file, prompt)
        if li:
            return li.pop(0)
        raise InputException

    def back(self):
        self.nextWindow('Main', 'main.ui', 'main.png')
        

class InputException(Exception):
    def __init__(self):
        pass
    
    def __str__(self):
        return 'too many inputs'


class Condition(WindowMaker):
    def __init__(self, ui, background_image, condition):
        super().__init__(ui, background_image)
        self.condition = condition
        self.textEdit.setStyleSheet('background: #4472C4; color: white; border: 2px white solid')
        self.textEdit.setText(self.condition.strip())

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Greet('greet.ui', 'greet.png')
    ex.show()
    sys.exit(app.exec())
