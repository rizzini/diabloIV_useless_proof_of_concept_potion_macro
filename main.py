import multiprocessing
import cv2
import time
import numpy
from multiprocessing import Process, Lock
import os
import mss.tools
from PyQt5.QtCore import QTimer
from pynput.keyboard import Key, Controller
from pynput import keyboard
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton, QLabel, QApplication, QWidget
from ctypes import c_wchar_p

fechar = multiprocessing.Value('i', 0)
pausa = multiprocessing.Value('i', 1)
usando_pocao = multiprocessing.Value('i', 0)
status = multiprocessing.Value(c_wchar_p, 0)
lock = Lock()


class janela(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(100, 100, 140, 235)
        self.botao_recarregar()
        self.botao_pausar_resumir()
        self.botao_fechar()
        self.status_label = QLabel(self)
        self.status_label.setFixedWidth(140)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.move(0, 193)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.status)
        self.timer.start(500)

    def status(self):
        if pausa.value == 0:
            self.status_label.setText('Rodando')
            self.status_label.setStyleSheet("QLabel {background-color: green;}")
        else:
            self.status_label.setText('Pausado..')
            self.status_label.setStyleSheet("QLabel {background-color: red;}")

    def botao_pausar_resumir(self):
        botao_pausar_resumir = QPushButton('Pausar/Resumir', self)
        botao_pausar_resumir.clicked.connect(self.pausar_resumir)
        botao_pausar_resumir.setGeometry(5, 5, 130, 50)
        botao_pausar_resumir.show()

    def botao_recarregar(self):
        botao_recarregar = QPushButton('Recarregar', self)
        botao_recarregar.clicked.connect(self.recarregar)
        botao_recarregar.setGeometry(5, 65, 130, 50)
        botao_recarregar.show()

    def botao_fechar(self):
        botao_fechar = QPushButton('Fechar', self)
        botao_fechar.clicked.connect(self.fechar)
        botao_fechar.setGeometry(5, 125, 130, 50)
        botao_fechar.show()

    def fechar(self):
        fechar.value = 1
        self.close()
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()

    def recarregar(self):
        fechar.value = 1
        self.close()
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()
        os.execv(sys.executable, ['python'] + sys.argv)

    def pausar_resumir(self):
        if str(pausa.value) == '1':
            pausa.value = 0
        else:
            pausa.value = 1


def on_release(key):
    if key == Key.end:
        fechar.value = 1
        janela.fechar()
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()
        return False
    elif key == Key.f1:
        if str(pausa.value) == '1':
            pausa.value = 0
        else:
            pausa.value = 1
    elif key == Key.f5:
        fechar.value = 1
        janela.fechar()
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()
        os.execv(sys.executable, ['python'] + sys.argv)


def deteccao():
    keyboard_input = Controller()
    while str(fechar.value) == '0':
        if str(pausa.value) == '0':
            with mss.mss() as sct:
                monitor = {"top": 1000, "left": 616, "width": 1, "height": 15}
                # im = sct.grab(monitor) # troubleshoot
                # mss.tools.to_png(im.rgb, im.size, output="/tmp/screenshot.png") # troubleshoot
                img = numpy.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            lower_vermelho = numpy.array([0, 89, 0])
            upper_vermelho = numpy.array([179, 255, 255])
            mask_vermelho = cv2.inRange(hsv, lower_vermelho, upper_vermelho)
            porcentagem = numpy.count_nonzero(mask_vermelho) / numpy.size(mask_vermelho) * 100
            if porcentagem < 50 and str(usando_pocao.value) == '0':
                with lock:
                    usando_pocao.value = 1
                    # disp = Xlib.display.Display()
                    # janela_em_foco = disp.get_input_focus().focus
                    # if str(janela_em_foco.get_wm_name()) == 'Diablo IV' and str(janela_em_foco.get_geometry().width) == '1920' and str(janela_em_foco.get_geometry().height) == '1080':
                    print('usar opção', porcentagem, usando_pocao.value)
                    keyboard_input.press('q')
                    keyboard_input.release('q')
                    time.sleep(1)
                    usando_pocao.value = 0
                    # else:
                    #     print('va para janela do jogo..')
            else:
                print('nao usar poção', porcentagem, usando_pocao.value)

            time.sleep(150 / 1000)
            with lock:
                fechar.value = fechar.value
        else:
            print('pausado..')
            time.sleep(1)


p1 = Process(target=deteccao)
p2 = Process(target=deteccao)
p3 = Process(target=deteccao)
p4 = Process(target=deteccao)
p5 = Process(target=deteccao)
if __name__ == '__main__':
    print('Iniciando...')
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    listener = keyboard.Listener(on_release=on_release)
    listener.start()
    app = QApplication(sys.argv)
    janela = janela()
    janela.show()
    app.exec_()
