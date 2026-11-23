class Enemy:

    def __init__(self, rect, img, isBoss = False):
        self.rect = rect
        self.img = img
        self.isBoss = isBoss        
        self.isDead = False
        
        if isBoss:
            self.hp = 10
        else:
            self.hp = 1

class Bullet:

    def __init__(self, rect, img):
        self.rect = rect
        self.img = img        
        self.isDead = False