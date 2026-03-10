from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
import random, math, os

# Force Landscape for the Window
from kivy.config import Config
Config.set('graphics', 'orientation', 'landscape')

if not os.path.exists("SaveScoreFiles"):
    os.makedirs("SaveScoreFiles")

class Star:
    def __init__(self):
        self.s = random.uniform(5, 12)
        self.x = random.randint(0, int(Window.width))
        self.y = random.randint(0, int(Window.height))
        self.speed = self.s * 0.4

class HealthPack:
    def __init__(self, x, y, value):
        self.x, self.y, self.value = x, y, value
        self.size = (50, 50)
        self.speed = 4.0
        self.color = (0, 1, 0, 1) if value == 1 else (1, 0, 0, 1)

class Enemy:
    def __init__(self, etype):
        self.type, self.y, self.time, self.size, self.alpha, self.dived = etype, float(Window.height), 0.0, (80, 80), 1.0, False
        if etype == "scout": 
            self.hp=100; self.speed,self.color,self.src=10,(1.0, 0.4, 0.4, 1.0),"scout.png"
        elif etype == "tank": 
            self.hp=850; self.speed,self.size,self.color,self.src=2.5,(130,130),(0.4, 1.0, 0.4, 1.0),"tank.png"
        elif etype == "wasp": 
            self.hp=150; self.speed,self.color,self.src=7.5,(0.4, 0.7, 1.0, 1.0),"wasp.png"; self.center_x=random.randint(100,int(Window.width-100))
        elif etype == "teleporter": 
            self.hp=200; self.speed,self.color,self.src=6.5,(0.8, 0.2, 1.0, 1.0),"teleporter.png"
        elif etype == "diver": 
            self.hp=120; self.speed,self.color,self.src=4.0,(1.0, 0.7, 0.2, 1.0),"diver.png"
        elif etype == "ghost": 
            self.hp=100; self.speed,self.color,self.src=2.5,(1.0, 1.0, 1.0, 1.0),"ghost.png"
        
        self.max_hp = self.hp
        self.x = float(self.center_x) if etype == "wasp" else float(random.randint(0, int(Window.width-self.size[0])))

    def move(self, dt):
        self.time += dt; self.y -= self.speed
        if self.type == "wasp": self.x = self.center_x + math.sin(self.time * 5.5) * 160
        elif self.type == "teleporter" and int(self.time * 40) % 25 == 0: self.x = float(random.randint(50, int(Window.width-130)))
        elif self.type == "diver" and self.y < Window.height * 0.6 and not self.dived: self.speed, self.color, self.dived = 24.0, (1.0,0.1,0.1,1.0), True
        elif self.type == "ghost": self.alpha = 0.2 if (self.time % 4.0) < 3.0 else 1.0

class SpaceShipGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ship_x, self.ship_y = Window.width/2, 120.0
        self.bullets, self.enemies, self.packs = [], [], []
        self.stars = [Star() for _ in range(40)]
        self.score, self.highscore, self.health = 0, 0, 20
        self.weapon_type, self.beam_active, self.beam_timer, self.paused, self.flash = "bullet", False, 0.0, False, 0.0
        Clock.schedule_interval(self.update, 1.0/60.0)
        Clock.schedule_interval(self.spawn_enemy, 1.1)

    def spawn_enemy(self, dt):
        if not self.paused: self.enemies.append(Enemy(random.choice(["scout","tank","wasp","teleporter","diver","ghost"])))

    def update(self, dt):
        if self.paused: return
        self.canvas.clear()
        with self.canvas:
            for s in self.stars:
                s.y -= s.speed
                if s.y < 0: s.y = Window.height; s.x = random.randint(0, int(Window.width))
                Color(1,1,1,0.5); Rectangle(source="star.png", pos=(s.x, s.y), size=(s.s, s.s))
            if self.flash > 0: Color(1,0,0,self.flash); Rectangle(pos=(0,0), size=(Window.width, Window.height)); self.flash -= 0.05
            Color(1,1,1,1); Rectangle(source="ship.png", pos=(self.ship_x-45, self.ship_y), size=(90, 90))
            Color(1,1,1,max(0.2, self.health/20.0)); Rectangle(source="ship.png", pos=(Window.width-100, Window.height-60), size=(35, 35))
            if self.beam_active:
                self.beam_timer -= dt; Color(1,1,1,0.9); Rectangle(source="beam.png", pos=(self.ship_x-35, self.ship_y+90), size=(70, Window.height))
                if self.beam_timer <= 0: self.beam_active = False
            Color(1,1,0,1)
            for b in self.bullets[:]:
                b[1] += 20; Ellipse(pos=(b[0]-6, b[1]), size=(12, 24))
                if b[1] > Window.height: self.bullets.remove(b)
            for p in self.packs[:]:
                p.y -= p.speed; Color(p.color[0], p.color[1], p.color[2], p.color[3]); Rectangle(source="pack.png", pos=(p.x, p.y), size=p.size)
                if abs(p.x + 25 - self.ship_x) < 55 and abs(p.y - self.ship_y) < 55:
                    self.health = min(20, self.health + p.value); self.packs.remove(p)
                elif p.y < -50: self.packs.remove(p)
            for e in self.enemies[:]:
                e.move(dt); Color(e.color[0],e.color[1],e.color[2],e.alpha); Rectangle(source=e.src, pos=(e.x, e.y), size=e.size)
                if e.alpha > 0.5:
                    for b in self.bullets[:]:
                        if (e.x < b[0] < e.x+e.size[0]) and (e.y < b[1] < e.y+e.size[1]):
                            e.hp -= 120; self.bullets.remove(b)
                    if self.beam_active and abs(e.x + e.size[0]/2 - self.ship_x) < 40: e.hp -= 14
                if abs(e.x + e.size[0]/2 - self.ship_x) < 60 and abs(e.y - self.ship_y) < 60:
                    self.flash = 0.4; self.health -= 2 if e.type in ["tank", "diver"] else 1
                    self.enemies.remove(e)
                    if self.health <= 0: App.get_running_app().show_lose_screen()
                elif e.hp <= 0:
                    if e.type == "diver": self.packs.append(HealthPack(e.x, e.y, 1))
                    elif e.type == "tank": self.packs.append(HealthPack(e.x, e.y, 2))
                    self.score += 20; self.enemies.remove(e)
                elif e.y < -150: self.enemies.remove(e)

    def on_touch_down(self, touch):
        if self.paused or touch.y < 160: return False
        if self.weapon_type == "bullet": self.bullets.append([float(self.ship_x), float(self.ship_y+90)])
        elif not self.beam_active: self.beam_active, self.beam_timer = True, 2.3
        return True

    def on_touch_move(self, touch):
        if not self.paused and touch.y > 160: self.ship_x = float(touch.x)

class MyApp(App):
    def build(self):
        self.root = FloatLayout(); self.game = SpaceShipGame()
        self.score_label = Label(text="Score: 0", pos_hint={"center_x":0.5, "top":0.98}, size_hint=(0.4, 0.1), font_size="16sp")
        self.hp_label = Label(text="20", pos_hint={"x": 0.9, "top": 0.98}, size_hint=(0.1, 0.1), font_size="16sp", color=(1, 0.3, 0.3, 1))
        self.weapon_btn = Button(text="shoot.bullet", size_hint=(0.3, 0.12), pos=(20, 20), background_color=(0.1,0.1,0.1,1), color=(1,1,0,1))
        self.weapon_btn.bind(on_release=self.toggle_weapon)
        self.settings_btn = Button(text="Settings", size_hint=(0.25, 0.12), pos=(Window.width-Window.width*0.25-20, 20))
        self.settings_btn.bind(on_release=self.open_settings)
        self.root.add_widget(self.game); self.root.add_widget(self.score_label); self.root.add_widget(self.hp_label)
        self.root.add_widget(self.weapon_btn); self.root.add_widget(self.settings_btn)
        Clock.schedule_interval(self.update_ui, 0.1); return self.root

    def update_ui(self, dt):
        self.score_label.text = "Score: " + str(self.game.score) + " | High: " + str(self.game.highscore)
        self.hp_label.text = str(max(0, self.game.health))

    def show_lose_screen(self):
        self.game.paused = True; box = BoxLayout(orientation='vertical', padding=20, spacing=10)
        box.add_widget(Label(text="HULL DESTROYED", font_size='25sp', color=(1,0,0,1)))
        rb = Button(text="Retry"); sb = Button(text="Save Score")
        rb.bind(on_release=self.retry_game); sb.bind(on_release=lambda x: self.show_save_ui())
        box.add_widget(rb); box.add_widget(sb); self.lose_pop = Popup(title="Game Over", content=box, size_hint=(0.6, 0.6), auto_dismiss=False); self.lose_pop.open()

    def retry_game(self, instance):
        self.game.health, self.game.score, self.game.enemies, self.game.bullets, self.game.packs = 20, 0, [], [], []
        self.game.paused = False; self.lose_pop.dismiss()

    def toggle_weapon(self, instance):
        if self.game.weapon_type == "bullet": self.game.weapon_type, instance.text, instance.color = "beam", "beam", (0, 0.8, 1, 1)
        else: self.game.weapon_type, instance.text, instance.color = "bullet", "shoot.bullet", (1, 1, 0, 1)

    def open_settings(self, instance):
        self.game.paused = True; box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        for opt in ["Save Score", "Load Score", "Configure Files", "Help", "Resume"]:
            btn = Button(text=opt); btn.bind(on_release=self.handle_settings); box.add_widget(btn)
        self.pop = Popup(title="Settings", content=box, size_hint=(0.7, 0.8), auto_dismiss=False, pos_hint={'x': -1})
        self.pop.open(); Animation(pos_hint={'x': 0.15}, duration=0.4, t='out_back').start(self.pop)

    def handle_settings(self, instance):
        if instance.text == "Resume": self.pop.dismiss(); self.game.paused = False
        elif instance.text == "Save Score": self.show_save_ui()
        elif instance.text == "Load Score": self.show_file_ui("load")
        elif instance.text == "Configure Files": self.show_file_ui("config")
        elif instance.text == "Help": self.show_help_menu()

    def show_help_menu(self):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        for t in ["Tutorial", "Enemies", "Mechanics", "Back"]:
            btn = Button(text=t); btn.bind(on_release=self.help_logic); box.add_widget(btn)
        self.hp_pop = Popup(title="Help", content=box, size_hint=(0.8, 0.8)); self.hp_pop.open()

    def help_logic(self, instance):
        if instance.text == "Back": self.hp_pop.dismiss(); return
        info = "Dodge enemies. Collect health packs.\nTap to shoot bullets.\nToggle beam for piercing damage."
        Popup(title=instance.text, content=Label(text=info), size_hint=(0.7, 0.5)).open()

    def show_save_ui(self):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10); self.ni = TextInput(text="save1", multiline=False)
        confirm = Button(text="Save"); box.add_widget(self.ni); box.add_widget(confirm)
        p = Popup(title="Save", content=box, size_hint=(0.6, 0.4)); confirm.bind(on_release=lambda x: self.save_act(p)); p.open()

    def save_act(self, p):
        path = os.path.join("SaveScoreFiles", self.ni.text + ".txt")
        with open(path, "w") as f: f.write(str(self.game.score))
        p.dismiss()

    def show_file_ui(self, mode):
        sv = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None); box.bind(minimum_height=box.setter('height'))
        files = [f for f in os.listdir('SaveScoreFiles') if f.endswith('.txt')]
        for f in files:
            btn = Button(text=f, size_hint_y=None, height=70)
            if mode == "load": btn.bind(on_release=lambda x, fn=f: self.load_act(fn))
            else: btn.bind(on_release=lambda x, fn=f: self.config_act(fn))
            box.add_widget(btn)
        sv.add_widget(box); self.fp = Popup(title="Select File", content=sv, size_hint=(0.8, 0.8)); self.fp.open()

    def load_act(self, fn):
        with open(os.path.join("SaveScoreFiles", fn), "r") as f: self.game.highscore = int(f.read())
        self.fp.dismiss()

    def config_act(self, fn):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10); self.rn = TextInput(text=fn.replace(".txt",""), multiline=False)
        rb, db = Button(text="Rename"), Button(text="Delete", background_color=(1,0,0,1))
        box.add_widget(self.rn); box.add_widget(rb); box.add_widget(db)
        p = Popup(title="Manage File", content=box, size_hint=(0.7, 0.6)); p.open()
        db.bind(on_release=lambda x: [os.remove(os.path.join("SaveScoreFiles", fn)), p.dismiss(), self.fp.dismiss()])
        rb.bind(on_release=lambda x: [os.rename(os.path.join("SaveScoreFiles", fn), os.path.join("SaveScoreFiles", self.rn.text+".txt")), p.dismiss(), self.fp.dismiss()])

if __name__ == '__main__':
    MyApp().run()
     with open(path, "w") as f: f.write(str(self.game.score))
        p.dismiss()

    def show_file_ui(self, mode):
        sv = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None); box.bind(minimum_height=box.setter('height'))
        files = [f for f in os.listdir('SaveScoreFiles') if f.endswith('.txt')]
        for f in files:
            btn = Button(text=f, size_hint_y=None, height=80)
            if mode == "load": btn.bind(on_release=lambda x, fn=f: self.load_act(fn))
            else: btn.bind(on_release=lambda x, fn=f: self.config_act(fn))
            box.add_widget(btn)
        sv.add_widget(box); self.fp = Popup(title="Score Files", content=sv, size_hint=(0.9, 0.8)); self.fp.open()

    def load_act(self, fn):
        path = os.path.join("SaveScoreFiles", fn)
        with open(path, "r") as f: self.game.highscore = int(f.read())
        self.fp.dismiss()

    def config_act(self, fn):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10); self.rn = TextInput(text=fn.replace(".txt",""), multiline=False)
        rb, db = Button(text="Rename"), Button(text="Delete", background_color=(1,0,0,1))
        box.add_widget(self.rn); box.add_widget(rb); box.add_widget(db)
        p = Popup(title="Config: "+fn, content=box, size_hint=(0.7, 0.5)); p.open()
        db.bind(on_release=lambda x: self.del_file(fn, p))
        rb.bind(on_release=lambda x: self.ren_file(fn, p))

    def del_file(self, fn, p):
        os.remove(os.path.join("SaveScoreFiles", fn))
        p.dismiss(); self.fp.dismiss()

    def ren_file(self, fn, p):
        os.rename(os.path.join("SaveScoreFiles", fn), os.path.join("SaveScoreFiles", self.rn.text+".txt"))
        p.dismiss(); self.fp.dismiss()

if __name__ == '__main__':
    MyApp().run()
