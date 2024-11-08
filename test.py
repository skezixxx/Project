import sys
import requests
import os
import time

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
        self.post_image = self.pre_image.scaled(self.size(), Qt.KeepAspectRatioByExpanding, transformMode = Qt.SmoothTransformation)
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
                queue = sorted(list(set(map(lambda x: x.strip().strip('!'), filter(lambda x: x.strip().startswith('!'), git_version.split('\n')[2:]))) - set(os.listdir(os.path.dirname(os.path.abspath(__file__))))))
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

    def throwDialogue(self, title, icon=None, text=None, informative_text=None, detailed_text=None, buttons='QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No'):
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
        self.nextWindow('Workspace', 'workspace.ui', 'workspace.png')


class Workspace(WindowMaker):
    def __init__(self, ui, background_image):
        super().__init__(ui, background_image)
        self.pushButton.setStyleSheet('background: #FA9800; color: white; padding: 10px 30px; border: 1px solid #FA9800; border-radius: 25px')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Greet('greet.ui', 'greet.png')
    ex.show()
    sys.exit(app.exec())
