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
    radius = 4 # 半径 (実際に表示される半径は1つ大きい)
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

    def lootTaken(self, loot):
        if (pow(self.y - loot.y, 2) + pow(self.x - loot.x, 2) <=
            pow(self.radius + loot.radius, 2)):
            return True
        else:
            return False


# カーソルのライト
class Light:
    radius = 36 # 半径
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
    blinkDuration = 20 # 点滅する時間
    laserDuration = 15 # レーザーが出る時間
    width = 5 # 太さ
    
    def __init__(self):
        self.set()

    # レーザーを出現させる
    def set(self):
        self.x = pyxel.rndi(5,195)
        self.y = pyxel.rndi(5,195)
        self.isBlinking = True # これから点滅するよってやつ
        self.isShooting = False # まだ撃ってないよってやつ
        self.blinkTime = 0 # どれくらいのフレーム点滅してるかってやつ

    # レーザーを点滅させるタイマー的な役割
    def blink(self):
        if self.blinkTime < self.blinkDuration:
            self.blinkTime += 1
        else:
            self.isBlinking = False # 点滅終了
            self.isShooting = True # これから撃つよってやつ
            self.shootTime = 0 # どれくらいのフレーム撃ってるかってやつ

    # レーザーを放つタイマー的な
    def shoot(self):
        if self.shootTime < self.laserDuration:
            self.shootTime += 1
        else:
            self.isShooting = False # 発砲終了


# 得点や残機をくれる謎のボール
class Loot:
    blinkDuration = 21
    radius = 4

    def __init__(self):
        self.x = pyxel.rndi(5,195)
        self.y = pyxel.rndi(5,195)
        self.isLife = False

    def set(self, life):
        self.x = pyxel.rndi(5,195)
        self.y = pyxel.rndi(5,195)
        self.isLife = False
        # 残機が減っていた場合、3分の1の確率で効果が残機回復になる
        if life < 3 and pyxel.rndi(1,3) == 1:
                self.isLife = True


class App:
    player = Player()
    light = Light()
    bullets = [Bullet()]
    laser = Laser()
    loot = Loot()
    points = -1 # 得点
    life = 3 # 残機

    def __init__(self):
        self.bullets = [Bullet() for _ in range(7)]
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

        # プレイヤーが得点ボールを拾った際の処理
        if self.player.lootTaken(self.loot):
            # ライフボールの場合、残機が増える
            if self.loot.isLife:
                self.life += 1
            else:
                self.points += pyxel.rndi(12,18)
            # ボールのリセット
            self.loot.set(self.life)
                

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
            self.laser.set() # レーザーの位置設定＆点滅開始させる

        # 点滅のタイマー
        if self.laser.isBlinking:
            self.laser.blink()

        # レーザーが放たれてる間、プレイヤーが当たると残機が減るという処理
        if self.laser.isShooting:
            self.laser.shoot()
            if self.player.laserHit(self.laser):
                self.life -= 1
            
        
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
        pyxel.circ(self.player.x, self.player.y, self.player.radius+1, self.player.color)
        pyxel.circ(self.player.x, self.player.y, self.player.radius, self.player.color2)

        # 弾幕の描画
        for b in self.bullets:
            pyxel.circ(b.x, b.y, b.radius, 0)

        # 点滅中のレーザーの描画
        if self.laser.isBlinking and self.laser.blinkTime % 2 == 0:
            pyxel.line(self.laser.x, 0, self.laser.x, 200, 0)
            pyxel.line(0, self.laser.y, 200, self.laser.y, 0)

        # 放たれてるレーザーの描画
        if self.laser.isShooting:
            pyxel.rect(self.laser.x -1, 0, self.laser.width, 200, 0)
            pyxel.rect(0, self.laser.y -1, 200, self.laser.width, 0)

        # 謎ボールの描画
        pyxel.circb(self.loot.x, self.loot.y, self.loot.radius, 0)

        # スコア等
        pyxel.text(5, 5, "score: " + str(self.points), 5)
        pyxel.text(5, 11, "lives: " + str(self.life), 5)


App()



