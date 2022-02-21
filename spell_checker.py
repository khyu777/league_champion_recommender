import tkinter as tk
import sys

class SpellChecker:
    def __init__(self):
        root = tk.Tk()
        root.title('Spell Check')

        self.gameTimer_label = tk.Label(root, text='Game Time')
        self.gameTimer_label.grid(column=1, columnspan=5, row=1)
        self.gameTimer = tk.Label(root, text='00:00')
        self.gameTimer.grid(column=1, columnspan=5, row=2)
        self.gameTimer_button = tk.Button(root, text = 'Start', command=self.startgame)
        self.gameTimer_button.grid(column=1, row=3)
        self.gameTimer_addmin = tk.Button(root, text = '+min', command=self.add_min)
        self.gameTimer_addmin.grid(column=2, row=3)
        self.gameTimer_subtmin = tk.Button(root, text = '-min', command=self.subt_min)
        self.gameTimer_subtmin.grid(column=3, row=3)
        self.gameTimer_addsec = tk.Button(root, text = '+sec', command=self.add_sec)
        self.gameTimer_addsec.grid(column=4, row=3)
        self.gameTimer_subtsec = tk.Button(root, text = '-sec', command=self.subt_sec)
        self.gameTimer_subtsec.grid(column=5, row=3)

        self.blank = tk.Label(root, text='')
        self.blank.grid(column=1, columnspan=5, row=4)
        self.top = tk.Label(root, text = 'Top')
        self.top.grid(column=1, columnspan=5, row=5)
        self.top_cooldown = tk.Label(root, text='00:00')
        self.top_cooldown.grid(column=1, columnspan=3, row=6)
        self.top_time = tk.Label(root, text='05:00')
        self.top_time.grid(column=4, row=6)
        self.top_button = tk.Button(root, text='Start', command=self.toggle_top)
        self.top_button.grid(column=1, columnspan=5, row=7)

        self.blank = tk.Label(root, text='')
        self.blank.grid(column=1, columnspan=5, row=8)
        self.jg = tk.Label(root, text = 'Jungle')
        self.jg.grid(column=1, columnspan=5, row=9)
        self.jg_cooldown = tk.Label(root, text='00:00')
        self.jg_cooldown.grid(column=1, columnspan=3, row=10)
        self.jg_time = tk.Label(root, text='05:00')
        self.jg_time.grid(column=4, row=10)
        self.jg_button = tk.Button(root, text='Start', command=self.toggle_jg)
        self.jg_button.grid(column=1, columnspan=5, row=11)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=12)
        self.mid = tk.Label(root, text = 'Mid')
        self.mid.grid(column=1, columnspan=5, row=13)
        self.mid_cooldown = tk.Label(root, text='00:00')
        self.mid_cooldown.grid(column=1, columnspan=3, row=14)
        self.mid_time = tk.Label(root, text='05:00')
        self.mid_time.grid(column=4, row=14)
        self.mid_button = tk.Button(root, text='Start', command=self.toggle_mid)
        self.mid_button.grid(column=1, columnspan=5, row=15)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=16)
        self.ad = tk.Label(root, text = 'AD Carry')
        self.ad.grid(column=1, columnspan=5, row=17)
        self.ad_cooldown = tk.Label(root, text='00:00')
        self.ad_cooldown.grid(column=1, columnspan=3, row=18)
        self.ad_time = tk.Label(root, text='05:00')
        self.ad_time.grid(column=4, row=18)
        self.ad_button = tk.Button(root, text='Start', command=self.toggle_ad)
        self.ad_button.grid(column=1, columnspan=5, row=19)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=20)
        self.sup = tk.Label(root, text = 'Support')
        self.sup.grid(column=1, columnspan=5, row=21)
        self.sup_cooldown = tk.Label(root, text='00:00')
        self.sup_cooldown.grid(column=1, columnspan=3, row=22)
        self.sup_time = tk.Label(root, text='05:00')
        self.sup_time.grid(column=4, row=22)
        self.sup_button = tk.Button(root, text='Start', command=self.toggle_sup)
        self.sup_button.grid(column=1, columnspan=5, row=23)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=24)
        self.reset = tk.Button(root, text='Reset All', command=self.reset_all)
        self.reset.grid(column=1, columnspan=5, row=25)

        def destroyer():
            root.quit()
            root.destroy()
            sys.exit()

        #self.quit = tk.Button(root, text = 'Exit', command=destroyer)
        #self.quit.pack()

        self.top_paused = True
        self.jg_paused = True
        self.mid_paused = True
        self.ad_paused = True
        self.sup_paused = True

        self.gameTimer_paused = True
        self.top_cooldown_paused = False

        root.mainloop()

    def startgame(self):
        if self.gameTimer_paused:
            self.gameTimer_paused = False
            self.gameTimer_button.config(text='Stop')
            self.gameTimer_oldtime = 0
            self.gameTimer_delta = 0
            self.run_gameTimer()
        else:
            self.gameTimer_paused = True
            self.gameTimer_oldtime = 0
            self.gameTimer_button.config(text='Start')
            self.gameTimer.config(text='00:00')

    def run_gameTimer(self):
        if self.gameTimer_paused:
            return self.gameTimer_paused
        self.gametime = self.gameTimer_oldtime + self.gameTimer_delta
        self.gameTimer_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(self.gametime, 60))
        self.gameTimer.config(text=timestr)
        self.gameTimer.after(1000, self.run_gameTimer) 

    def add_min(self):
        self.gameTimer_delta += 60

    def subt_min(self):
        self.gameTimer_delta -= 60

    def add_sec(self):
        self.gameTimer_delta += 1

    def subt_sec(self):
        self.gameTimer_delta -= 1

    def reset_all(self):
        self.top_paused = True
        self.jg_paused = True
        self.mid_paused = True
        self.ad_paused = True
        self.sup_paused = True
        self.gameTimer_paused = True
        self.top_cooldown_paused = False
        self.top_time.config(text='05:00')
        self.jg_time.config(text='05:00')
        self.mid_time.config(text='05:00')
        self.ad_time.config(text='05:00')
        self.sup_time.config(text='05:00')
        self.top_button.config(text='Start')
        self.jg_button.config(text='Start')
        self.mid_button.config(text='Start')
        self.ad_button.config(text='Start')
        self.sup_button.config(text='Start')
        self.gameTimer_button.config(text='Start')
        self.gameTimer.config(text='00:00')
        self.top_cooldown.config(text='00:00')
        self.jg_cooldown.config(text='00:00')
        self.mid_cooldown.config(text='00:00')
        self.ad_cooldown.config(text='00:00')
        self.sup_cooldown.config(text='00:00')

    def toggle_top(self):
        if self.top_paused:
            self.top_paused = False
            self.top_button.config(text='Stop')
            self.top_oldtime = 300
            self.top_delta = 0
            self.top_cooldown.config(text='{:02}:{:02}'.format(*divmod(self.gametime + 300, 60)))
            self.run_timer_top()
        else:
            self.top_paused = True
            self.top_oldtime = 0
            self.top_button.config(text='Start')

    def run_timer_top(self):
        if self.top_paused:
            return
        time = self.top_oldtime - self.top_delta
        self.top_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(time, 60))
        self.top_time.config(text=timestr)
        self.top_time.after(1000, self.run_timer_top)
        if time == 0:
            self.top_paused = True
            self.top_button.config(text='Start')
            self.top_time.config(text='05:00')        

    def toggle_jg(self):
        if self.jg_paused:
            self.jg_paused = False
            self.jg_button.config(text='Stop')
            self.jg_oldtime = 300
            self.jg_delta = 0
            self.jg_cooldown.config(text='{:02}:{:02}'.format(*divmod(self.gametime + 300, 60)))
            self.run_timer_jg()
        else:
            self.jg_paused = True
            self.jg_oldtime = 0
            self.jg_button.config(text='Start')

    def run_timer_jg(self):
        if self.jg_paused:
            return
        time = self.jg_oldtime - self.jg_delta
        self.jg_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(time, 60))
        self.jg_time.config(text=timestr)
        self.jg_time.after(1000, self.run_timer_jg)
        if time == 0:
            self.jg_paused = True
            self.jg_button.config(text='Start')
            self.jg_time.config(text='05:00')

    def toggle_mid(self):
        if self.mid_paused:
            self.mid_paused = False
            self.mid_button.config(text='Stop')
            self.mid_oldtime = 300
            self.mid_delta = 0
            self.mid_cooldown.config(text='{:02}:{:02}'.format(*divmod(self.gametime + 300, 60)))   
            self.run_timer_mid()
        else:
            self.mid_paused = True
            self.mid_oldtime = 0
            self.mid_button.config(text='Start')

    def run_timer_mid(self):
        if self.mid_paused:
            return
        time = self.mid_oldtime - self.mid_delta
        self.mid_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(time, 60))
        self.mid_time.config(text=timestr)
        self.mid_time.after(1000, self.run_timer_mid)
        if time == 0:
            self.mid_paused = True
            self.mid_button.config(text='Start')
            self.mid_time.config(text='05:00')

    def toggle_ad(self):
        if self.ad_paused:
            self.ad_paused = False
            self.ad_button.config(text='Stop')
            self.ad_oldtime = 300
            self.ad_delta = 0
            self.ad_cooldown.config(text='{:02}:{:02}'.format(*divmod(self.gametime + 300, 60)))
            self.run_timer_ad()
        else:
            self.ad_paused = True
            self.ad_oldtime = 0
            self.ad_button.config(text='Start')

    def run_timer_ad(self):
        if self.ad_paused:
            return
        time = self.ad_oldtime - self.ad_delta
        self.ad_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(time, 60))
        self.ad_time.config(text=timestr)
        self.ad_time.after(1000, self.run_timer_ad)
        if time == 0:
            self.ad_paused = True
            self.ad_button.config(text='Start')
            self.ad_time.config(text='05:00')

    def toggle_sup(self):
        if self.sup_paused:
            self.sup_paused = False
            self.sup_button.config(text='Stop')
            self.sup_oldtime = 300
            self.sup_delta = 0
            self.sup_cooldown.config(text='{:02}:{:02}'.format(*divmod(self.gametime + 300, 60)))
            self.run_timer_sup()
        else:
            self.sup_paused = True
            self.sup_oldtime = 0
            self.sup_button.config(text='Start')

    def run_timer_sup(self):
        if self.sup_paused:
            return
        time = self.sup_oldtime - self.sup_delta
        self.sup_delta += 1
        timestr = '{:02}:{:02}'.format(*divmod(time, 60))
        self.sup_time.config(text=timestr)
        self.sup_time.after(1000, self.run_timer_sup)
        if time == 0:
            self.sup_paused = True
            self.sup_button.config(text='Start')
            self.sup_time.config(text='05:00')

SpellChecker()