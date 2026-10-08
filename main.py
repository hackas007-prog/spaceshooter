import random
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Triangle, Ellipse
from kivy.uix.label import Label
from kivy.uix.widget import Widget

DP = 2.0  # player depth


class Game(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.label = Label(font_size="22sp", halign="center", valign="top",
                           size_hint=(None, None))
        self.add_widget(self.label)
        self.reset()

    def reset(self):
        self.px = 0.0
        self.stars = [[random.uniform(-14, 14), random.uniform(-14, 14),
                       random.uniform(1, 30)] for _ in range(90)]
        self.enemies, self.bullets, self.booms = [], [], []
        self.score, self.lives, self.over = 0, 3, False
        self.t_fire = self.t_spawn = 0.0

    def on_touch_down(self, touch):
        if self.over:
            self.reset()
        self.move_to(touch.x)
        return True

    def on_touch_move(self, touch):
        self.move_to(touch.x)
        return True

    def move_to(self, tx):
        f = self.width * 0.5
        self.px = max(-1.8, min(1.8, (tx - self.width / 2) / f * DP))

    def update(self, dt):
        dt = min(dt, 0.05)
        w, h = self.size
        if w <= 1:
            return
        f, cx, cy = w * 0.5, w / 2, h * 0.62
        py = (h * 0.18 - cy) / f * DP

        for s in self.stars:
            s[2] -= dt * 8
            if s[2] < 0.5:
                s[:] = [random.uniform(-14, 14), random.uniform(-14, 14), 30]

        if not self.over:
            self.t_fire += dt
            if self.t_fire >= 0.2:
                self.t_fire = 0
                self.bullets.append([self.px, py, DP])
            self.t_spawn += dt
            if self.t_spawn >= max(0.35, 1.0 - self.score * 0.004):
                self.t_spawn = 0
                self.enemies.append([random.uniform(-1.8, 1.8),
                                     py + random.uniform(0, 0.5), 30.0])
            spd = min(14, 6 + self.score * 0.02)
            for b in self.bullets:
                b[2] += dt * 25
            self.bullets = [b for b in self.bullets if b[2] < 30]
            for e in self.enemies:
                e[2] -= dt * spd
            for b in self.bullets[:]:
                for e in self.enemies[:]:
                    if (abs(b[0] - e[0]) < 0.5 and abs(b[1] - e[1]) < 0.7
                            and abs(b[2] - e[2]) < 1.0):
                        self.bullets.remove(b)
                        self.enemies.remove(e)
                        self.booms.append([e[0], e[1], e[2], 1.0])
                        self.score += 10
                        break
            for e in self.enemies[:]:
                if e[2] <= DP + 0.3 and abs(e[0] - self.px) < 0.6:
                    self.enemies.remove(e)
                    self.booms.append([e[0], e[1], e[2], 1.0])
                    self.lives -= 1
                elif e[2] < 0.7:
                    self.enemies.remove(e)
            if self.lives <= 0:
                self.over = True
        for x in self.booms:
            x[3] -= dt * 2
        self.booms = [x for x in self.booms if x[3] > 0]

        # ---------- drawing ----------
        c = self.canvas.before
        c.clear()
        with c:
            Color(0.02, 0.02, 0.08)
            Rectangle(pos=self.pos, size=self.size)
            for X, Y, d in self.stars:
                if d > 0.5:
                    Color(1, 1, 1, max(0.1, 1 - d / 30))
                    sz = max(1.5, 6 / d)
                    Rectangle(pos=(cx + X / d * f, cy + Y / d * f), size=(sz, sz))
            for X, Y, d in sorted(self.enemies, key=lambda e: -e[2]):
                sx, sy, s = cx + X / d * f, cy + Y / d * f, 0.7 / d * f
                Color(0.6, 0.05, 0.05)
                Triangle(points=(sx, sy - s * .5, sx - s * .55, sy + s * .4, sx, sy + s * .2))
                Color(1, 0.2, 0.2)
                Triangle(points=(sx, sy - s * .5, sx + s * .55, sy + s * .4, sx, sy + s * .2))
                Color(1, 0.8, 0.2)
                Ellipse(pos=(sx - s * .1, sy - s * .1), size=(s * .2, s * .2))
            for X, Y, d in self.bullets:
                Color(1, 1, 0.3)
                bw, bl = 0.12 / d * f, 0.6 / d * f
                Rectangle(pos=(cx + X / d * f - bw / 2, cy + Y / d * f), size=(bw, bl))
            for X, Y, d, life in self.booms:
                sx, sy = cx + X / d * f, cy + Y / d * f
                r = (1.5 - life) * 1.2 / d * f
                Color(1, 0.6, 0.1, life)
                Ellipse(pos=(sx - r / 2, sy - r / 2), size=(r, r))
            if self.lives > 0:
                sx, sy, s = cx + self.px / DP * f, h * 0.18, 0.8 / DP * f
                Color(1, 0.5, 0.1)
                Ellipse(pos=(sx - s * .12, sy - s * .55), size=(s * .24, s * .3))
                Color(0.1, 0.4, 0.8)
                Triangle(points=(sx, sy + s * .6, sx - s * .5, sy - s * .4, sx, sy - s * .15))
                Color(0.4, 0.8, 1)
                Triangle(points=(sx, sy + s * .6, sx + s * .5, sy - s * .4, sx, sy - s * .15))

        self.label.size = (w, 110)
        self.label.text_size = (w, 110)
        self.label.pos = (0, h - 120)
        t = "Score: %d    Lives: %d" % (self.score, max(0, self.lives))
        if self.over:
            t += "\nGAME OVER - tap karke restart karo"
        self.label.text = t


class SpaceApp(App):
    def build(self):
        g = Game()
        Clock.schedule_interval(g.update, 1 / 60.0)
        return g


if __name__ == "__main__":
    SpaceApp().run()
