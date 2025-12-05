import pyxel
import math
pyxel.init(200,200)
pyxel.sounds[0].set(notes='A2C3', tones='TT', volumes='33', effects='NN', speed=10)
pyxel.sounds[1].set(notes='A2A1', tones='NN', volumes='33', effects='NN', speed=10)


# プレイヤー
class Player:
    normSpeed = 3 # プレイヤーの通常移動速度
    dashSpeed = 25 # ダッシュ中の移動速度
    shiftSpeed = 1 # シフト中の移動速度
    radius = 5 # 半径
    color = 11 # 外側の色
    color2 = 0 # 内側の色
    
    def __init__(self):
        self.x = 100
        self.y = 100
        self.speed = Player.normSpeed

    def moveUp(self):
        self.y -= self.speed

    def moveLeft(self):
        self.x -= self.speed

    def moveDown(self):
        self.y += self.speed

    def moveRight(self):
        self.x += self.speed

    # 弾幕にあたったかどうかの処理
    def hit(self, bullet):
        if (pow(self.y - bullet.y, 2) + pow(self.x - bullet.x, 2) <=
            pow(self.radius + bullet.radius, 2)):
            return True
        else:
            return False

    # レーザーにあたったかどうかの処理
    def laserHit(self, laser):
        halfWidth = math.floor(laser.width/2)
        if self.x - self.radius - halfWidth <= laser.x <= self.x + self.radius + halfWidth:
            return True
        if self.y - self.radius - halfWidth <= laser.y <= self.y + self.radius + halfWidth:
            return True
        return False


# カーソルのライト
class Light:
    radius = 35 # 半径
    color = 7 # 色（白）

    def __init__(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y

    def update(self):
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y


# 弾幕
class Bullet:
    speed = 2 # 速度
    radius = 4 # 半径

    def __init__(self):
        self.restart()

    def move(self):
        self.x += self.vx * Bullet.speed
        self.y += self.vy * Bullet.speed
        # 跳ね返りの処理
        if self.x >= 200 or self.x <= 0:
            self.vx = self.vx * -1

    # 画面上側に弾が戻る
    def restart(self):
        self.x = pyxel.rndi(0,199)
        self.y = 0
        angle = pyxel.rndi(30,150)
        self.vx = pyxel.cos(angle)
        self.vy = pyxel.sin(angle)
    

# レーザー
class Laser:
    blinkDuration = 21 # 点滅する時間。奇数でなければならない
    laserDuration = 15 # レーザーが出る時間
    width = 5 # 太さ
    
    def __init__(self):
        self.set()

    # レーザーの出現場所をランダムに設定する
    def set(self):
        self.x = pyxel.rndi(5,195)
        self.y = pyxel.rndi(5,195)


class App:
    player = Player()
    light = Light()
    bullets = [Bullet()]
    laserBlink = False # 点滅中の間　レーザーを描画するかどうか
    laserShoot = False # レーザーが放たれてるかどうか
    laser = Laser()
    blinkFrame = Laser.blinkDuration # レーザー点滅の残りフレーム数
    points = -1 # 得点
    life = 3 # 残機

    def __init__(self):
        self.bullets = [Bullet() for _ in range(5)]
        pyxel.run(self.update, self.draw)

    def update(self):
        # 3回以上当たったら終了
        if self.life <= 0:
            return
        
        # プレイヤーの移動の処理
        if pyxel.btn(pyxel.KEY_SHIFT):
            self.player.speed = Player.shiftSpeed
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.player.speed = Player.dashSpeed
        if pyxel.btn(pyxel.KEY_W):
            self.player.moveUp()
        if pyxel.btn(pyxel.KEY_A):
            self.player.moveLeft()
        if pyxel.btn(pyxel.KEY_S):
            self.player.moveDown()
        if pyxel.btn(pyxel.KEY_D):
            self.player.moveRight()
        self.player.speed = Player.normSpeed

        # カーソルのライトをアップデート
        self.light.update()

        # 弾幕の処理
        for b in self.bullets:
            b.move()
            # 当たったときの処理
            if self.player.hit(b):
                b.restart()
                self.life -= 1
            # 画面下側に行ったときの処理
            elif b.y >= 200:
                b.restart()

        # 得点の処理。30フレーム毎に+1
        if pyxel.frame_count % 30 == 0:
            self.points += 1

        # レーザーの処理。300フレーム毎に出現
        if pyxel.frame_count % 300 == 0:
            self.bullets.append(Bullet()) # ついでに弾幕の数を上げる
            self.bullets.append(Bullet())
            self.laser.set() # ランダムな位置に設定
            self.laserBlink = True # レーザーを描画するよ
            self.blinkFrame = Laser.blinkDuration

        # 点滅中の処理
        if self.blinkFrame > 0:
            self.laserBlink = not self.laserBlink
            self.blinkFrame -= 1

        # 点滅し終わったよっていう処理
        if (pyxel.frame_count - Laser.blinkDuration) % 300 == 0:
            self.laserShoot = True

        # レーザーを撃ってる間、プレイヤーが当たった際の処理
        if self.laserShoot:
            if self.player.laserHit(self.laser):
                self.life -= 1
        
        # 撃ち終わったよっていう処理
        if (pyxel.frame_count - (Laser.blinkDuration + Laser.laserDuration)) % 300 == 0:
            self.laserShoot = False
            
        
    # 描画
    def draw(self):
        # ゲームオーバーの表示
        if self.life <= 0:
            pyxel.text(85, 100, "Game Over", 8)
            return
        
        pyxel.cls(0) #黒くする
        
        # カーソルのライトの描画
        pyxel.circ(self.light.x, self.light.y, self.light.radius, self.light.color)

        # プレイヤーの描画
        pyxel.circ(self.player.x, self.player.y, 20, 7) # プレイヤー周辺のライト
        pyxel.circ(self.player.x, self.player.y, self.player.radius, self.player.color)
        pyxel.circ(self.player.x, self.player.y, self.player.radius-1, self.player.color2)

        # 弾幕の描画
        for b in self.bullets:
            pyxel.circ(b.x, b.y, b.radius, 0)

        # 点滅中のレーザーの描画
        if self.laserBlink:
            pyxel.line(self.laser.x, 0, self.laser.x, 200, 0)
            pyxel.line(0, self.laser.y, 200, self.laser.y, 0)

        # 放たれてるレーザーの描画
        if self.laserShoot:
            pyxel.rect(self.laser.x -1, 0, self.laser.width, 200, 0)
            pyxel.rect(0, self.laser.y -1, 200, self.laser.width, 0)

        # スコア等
        pyxel.text(5, 5, "score: " + str(self.points), 5)
        pyxel.text(5, 11, "lives: " + str(self.life), 5)


App()

