from PySide6.QtCore import QObject, QRectF, QRect, Qt, Signal
from PySide6.QtGui import QPixmap
from threading import Thread
from random import randint
from enemy_bullet import Enemy, Bullet
import time

class Game(QObject):

    update_signal = Signal(QRect)
    gover_signal = Signal()

    def __init__(self, widget):
        super().__init__()
        self.parent = widget
        self.rect = QRectF(widget.rect())

        # 배경, 아군, 적군 이미지
        self.bk_img = QPixmap('./images/background.png')
        self.my_img = QPixmap('./images/my.png')
        self.en_img = QPixmap('./images/enemy_normal.png')
        self.eb_img = QPixmap('./images/enemy_boss.png')
        self.bu_img = QPixmap('./images/bullet.png')
        self.de_img = QPixmap('./images/destroy.png')

        # 화면중앙에 아군 사각형
        x = self.rect.width()/4
        y = self.rect.height()/2
        w = self.my_img.rect().width()
        h = self.my_img.rect().height()
        self.my = QRectF(x, y, w, h)
        self.bullets = []

        # 방향키
        self.L = False
        self.R = False
        self.U = False
        self.D = False

        # 적군들
        self.enemies = [] 

        # 각종 신호들
        self.update_signal.connect(widget.update)
        self.gover_signal.connect(widget.gameOver)


        # 게임 진행쓰레드
        self.t = Thread(target=self.threadFunc)
        self.run = True
        self.t.start()

    def draw(self, qp):
        # 배경그리기
        qp.drawPixmap(self.rect, self.bk_img, self.bk_img.rect())

        # 주인공그리기
        #qp.drawRect(self.my)
        qp.drawPixmap(self.my, self.my_img, self.my_img.rect())


        # 총알 그리기
        for b in self.bullets:
            qp.drawPixmap(b.rect, b.img, b.img.rect())

        # 적군그리기
        for e in self.enemies:
            #qp.drawRect(e.rect)
            qp.drawPixmap(e.rect, e.img, e.img.rect())

    def keyPress(self, key, isPress):
        if key==Qt.Key.Key_A:
            self.L = isPress
        if key==Qt.Key.Key_D:
            self.R = isPress
        if key==Qt.Key.Key_W:
            self.U = isPress
        if key==Qt.Key.Key_S:
            self.D = isPress

        if key==Qt.Key.Key_Space and isPress:
            self.createBullet()

    def createBullet(self):
        x = self.my.center().x()
        y = self.my.center().y()
        w = self.bu_img.rect().width()
        h = self.bu_img.rect().height()
        rect = QRectF(x, y, w, h)
        b = Bullet(rect, self.bu_img)
        self.bullets.append(b)

    def createEnemy(self):
        k = 1000
        n = randint(1, k)
        # k의 1/100보다 작으면 랜덤으로 적생성
        if n<k//100:            
            if n==1:
                isBoss = True
                img = self.eb_img
            else:
                isBoss = False
                img = self.en_img

            w = img.width()
            h = img.height()
            x = self.rect.width()
            y = randint(0, int(self.rect.height()))-h
            rect = QRectF(x, y, w, h)

            e = Enemy(rect, img, isBoss)
            self.enemies.append(e)
        

    def moveMy(self):
        old_my = QRectF(self.my)
        sp = 3
        if self.L:
            self.my.translate(-sp, 0)
        if self.R:
            self.my.translate(sp, 0)
        if self.U:
            self.my.translate(0, -sp)
        if self.D:
            self.my.translate(0, sp)  
        
        self.rePaint(old_my, self.my)

    def moveEnemy(self):
        for e in self.enemies:
            old_e = QRectF(e.rect)
            x = 1
            y = 0.5

            if self.my.center().y() < e.rect.center().y():
                y = 0-y

            e.rect.translate(-x, y)

            # 화면을 벗어난 적
            if e.rect.right()<0:
                e.isDead = True

            # 나와 충돌한 적
            if self.my.intersects(e.rect):
                return False

            self.rePaint(old_e, e.rect)   
        return True

    def moveBullet(self):
        sp = 5
        for b in self.bullets:
            old_b = QRectF(b.rect)

            b.rect.translate(sp, 0)

            # 화면을 벗어난 총알
            if b.rect.left()>self.rect.width():
                b.isDead = True

            # 적과 부딪힌 총알
            for e in self.enemies:
                if e.rect.intersects(b.rect):
                    e.hp -= 1
                    if e.hp<=0:
                        e.isDead = True
                    b.isDead = True
                    break        
            
            self.rePaint(old_b, b.rect)

    def rePaint(self, old_rect, rect):
        # 이전 영역과 새로운 영역을 합친 영역만 새로그림(효율성)
        new_rect = old_rect.united(rect)
        self.update_signal.emit(new_rect.toAlignedRect())

    def closeGame(self):
        self.run = False

    def threadFunc(self):
        while self.run:
            self.createEnemy()
            self.moveMy()    
            self.moveBullet()

            if self.moveEnemy()==False:
                self.run = False
                self.my_img = QPixmap(self.de_img)
                self.rePaint(self.my, self.my)
                self.gover_signal.emit()                

            # 죽은 적군 리스트에서 제거
            self.enemies = [e for e in self.enemies if e.isDead==False]
            # 죽은 총알 리스트에서 제거
            self.bullets = [b for b in self.bullets if b.isDead==False]
            time.sleep(0.01)

            print('number of bullets:', len(self.bullets))
            print('number of enemies:', len(self.enemies))