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
        self.top_manual = tk.Label(root, text = 'Time:')
        self.top_manual.grid(column=1, row=6)
        self.top_manual_text = tk.StringVar()
        self.top_manual_entry = tk.Entry(root, width=10, bd=5, textvariable=self.top_manual_text)
        self.top_manual_entry.bind('<Control-s>', lambda x: self.execute(self.toggle_top))
        self.top_manual_entry.grid(column=2, columnspan=2, row=6)
        self.top_time = tk.Label(root, text='05:00')
        self.top_time.grid(column=4, columnspan=2, row=6)
        self.top_button = tk.Button(root, text='Start', command=self.toggle_top)
        self.top_button.grid(column=1, columnspan=5, row=7)

        self.blank = tk.Label(root, text='')
        self.blank.grid(column=1, columnspan=5, row=8)
        self.jg = tk.Label(root, text = 'Jungle')
        self.jg.grid(column=1, columnspan=5, row=9)
        self.jg_manual = tk.Label(root, text = 'Time:')
        self.jg_manual.grid(column=1, row=10)
        self.jg_manual_text = tk.StringVar()
        self.jg_manual_entry = tk.Entry(root, width=10, bd=5, textvariable=self.jg_manual_text)
        self.jg_manual_entry.grid(column=2, columnspan=2, row=10)
        self.jg_manual_entry.bind('<Control-s>', lambda x: self.execute(self.toggle_jg))
        self.jg_time = tk.Label(root, text='05:00')
        self.jg_time.grid(column=4, columnspan=2, row=10)
        self.jg_button = tk.Button(root, text='Start', command=self.toggle_jg)
        self.jg_button.grid(column=1, columnspan=5, row=11)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=12)
        self.mid = tk.Label(root, text = 'Mid')
        self.mid.grid(column=1, columnspan=5, row=13)
        self.mid_manual = tk.Label(root, text = 'Time:')
        self.mid_manual.grid(column=1, row=14)
        self.mid_manual_text = tk.StringVar()
        self.mid_manual_entry = tk.Entry(root, width=10, bd=5, textvariable=self.mid_manual_text)
        self.mid_manual_entry.grid(column=2, columnspan=2, row=14)
        self.mid_manual_entry.bind('<Control-s>', lambda x: self.execute(self.toggle_mid))
        self.mid_time = tk.Label(root, text='05:00')
        self.mid_time.grid(column=4, columnspan=2, row=14)
        self.mid_button = tk.Button(root, text='Start', command=self.toggle_mid)
        self.mid_button.grid(column=1, columnspan=5, row=15)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=16)
        self.ad = tk.Label(root, text = 'AD Carry')
        self.ad.grid(column=1, columnspan=5, row=17)
        self.ad_manual = tk.Label(root, text = 'Time:')
        self.ad_manual.grid(column=1, row=18)
        self.ad_manual_text = tk.StringVar()
        self.ad_manual_entry = tk.Entry(root, width=10, bd=5, textvariable=self.ad_manual_text)
        self.ad_manual_entry.grid(column=2, columnspan=2, row=18)
        self.ad_manual_entry.bind('<Control-s>', lambda x: self.execute(self.toggle_ad))
        self.ad_time = tk.Label(root, text='05:00')
        self.ad_time.grid(column=4, columnspan=2, row=18)
        self.ad_button = tk.Button(root, text='Start', command=self.toggle_ad)
        self.ad_button.grid(column=1, columnspan=5, row=19)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=20)
        self.sup = tk.Label(root, text = 'Support')
        self.sup.grid(column=1, columnspan=5, row=21)
        self.sup_manual = tk.Label(root, text = 'Time:')
        self.sup_manual.grid(column=1, row=22)
        self.sup_manual_text = tk.StringVar()
        self.sup_manual_entry = tk.Entry(root, width=10, bd=5, textvariable=self.sup_manual_text)
        self.sup_manual_entry.grid(column=2, columnspan=2, row=22)
        self.sup_manual_entry.bind('<Control-s>', lambda x: self.execute(self.toggle_sup))
        self.sup_time = tk.Label(root, text='05:00')
        self.sup_time.grid(column=4, columnspan=2, row=22)
        self.sup_button = tk.Button(root, text='Start', command=self.toggle_sup)
        self.sup_button.grid(column=1, columnspan=5, row=23)
        
        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=24)
        self.all = tk.Entry(root, bd=5)
        self.all.bind('<Control-s>', lambda x: self.execute(self.input_info))
        self.all.grid(column=1, columnspan=5, row=25)

        self.blank = tk.Label(root, text = '')
        self.blank.grid(column=1, columnspan=5, row=26)
        self.reset = tk.Button(root, text='Reset All', command=self.reset_all)
        self.reset.grid(column=1, columnspan=5, row=27)

        def destroyer():
            root.quit()
            root.destroy()
            sys.exit()

        self.quit = tk.Button(root, text = 'Exit', command=destroyer)
        self.quit.grid(column=1, columnspan=5, row=28)

        self.top_paused = True
        self.jg_paused = True
        self.mid_paused = True
        self.ad_paused = True
        self.sup_paused = True

        self.gameTimer_paused = True
        self.top_cooldown_paused = False

        root.mainloop()

    def input_info(self):
        times = self.all.get().split(sep=' ')
        for time in times:
            if 'top' in time:
                self.top_manual_entry.delete(0, tk.END)
                self.top_manual_entry.insert(0, time.replace('top', ''))
                self.toggle_top()
            elif 'jg' in time:
                self.jg_manual_entry.delete(0, tk.END)
                self.jg_manual_entry.insert(0, time.replace('jg', ''))
                self.toggle_jg()
            elif 'mid' in time:
                self.mid_manual_entry.delete(0, tk.END)
                self.mid_manual_entry.insert(0, time.replace('mid', ''))
                self.toggle_mid()
            elif 'ad' in time:
                self.ad_manual_entry.delete(0, tk.END)
                self.ad_manual_entry.insert(0, time.replace('ad', ''))
                self.toggle_ad()
            elif 'sup' in time:
                self.sup_manual_entry.delete(0, tk.END)
                self.sup_manual_entry.insert(0, time.replace('sup', ''))
                self.toggle_sup()
    
    def execute(self, event):
        event()

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
        self.top_manual_entry.delete(0, tk.END)
        self.jg_manual_entry.delete(0, tk.END)
        self.mid_manual_entry.delete(0, tk.END)
        self.ad_manual_entry.delete(0, tk.END)
        self.sup_manual_entry.delete(0, tk.END)

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

    def toggle_top(self):
        self.top_paused = False
        self.top_oldtime = self.gametime
        self.top_delta = 0
        if len(self.top_manual_entry.get()) != 4: 
            timestr = '{:02}{:02}'.format(*divmod(self.gametime + 300, 60))
            self.top_manual_entry.delete(0, tk.END)
            self.top_manual_entry.insert(0, timestr)
        self.run_timer_top()

    def run_timer_top(self):
        if self.top_paused:
            return
        if len(self.top_manual_entry.get()) == 4:
            time = int(self.top_manual_entry.get()[:2])*60 + int(self.top_manual_entry.get()[2:])
        else:
            time = self.top_oldtime + 300
        timestr = '{:02}:{:02}'.format(*divmod(time - self.gametime, 60))
        self.top_time.config(text=timestr)
        self.top_time.after(1000, self.run_timer_top)
        if time - self.gametime == 0:
            self.top_paused = True
            self.top_button.config(text='Start')
            self.top_time.config(text='05:00') 

    def toggle_jg(self):
        self.jg_paused = False
        self.jg_oldtime = self.gametime
        self.jg_delta = 0
        if len(self.jg_manual_entry.get()) != 4: 
            timestr = '{:02}{:02}'.format(*divmod(self.gametime + 300, 60))
            self.jg_manual_entry.delete(0, tk.END)
            self.jg_manual_entry.insert(0, timestr)
        self.run_timer_jg()

    def run_timer_jg(self):
        if self.jg_paused:
            return
        if len(self.jg_manual_entry.get()) == 4:
            time = int(self.jg_manual_entry.get()[:2])*60 + int(self.jg_manual_entry.get()[2:])
        else:
            time = self.jg_oldtime + 300
        timestr = '{:02}:{:02}'.format(*divmod(time - self.gametime, 60))
        self.jg_time.config(text=timestr)
        self.jg_time.after(1000, self.run_timer_jg)
        if time - self.gametime == 0:
            self.jg_paused = True
            self.jg_button.config(text='Start')
            self.jg_time.config(text='05:00')

    def toggle_mid(self):
        self.mid_paused = False
        self.mid_oldtime = self.gametime
        self.mid_delta = 0
        if len(self.mid_manual_entry.get()) != 4: 
            timestr = '{:02}{:02}'.format(*divmod(self.gametime + 300, 60))
            self.mid_manual_entry.delete(0, tk.END)
            self.mid_manual_entry.insert(0, timestr)
        self.run_timer_mid()

    def run_timer_mid(self):
        if self.mid_paused:
            return
        if len(self.mid_manual_entry.get()) == 4:
            time = int(self.mid_manual_entry.get()[:2])*60 + int(self.mid_manual_entry.get()[2:])
        else:
            time = self.mid_oldtime + 300
        timestr = '{:02}:{:02}'.format(*divmod(time - self.gametime, 60))
        self.mid_time.config(text=timestr)
        self.mid_time.after(1000, self.run_timer_mid)
        if time - self.gametime == 0:
            self.mid_paused = True
            self.mid_button.config(text='Start')
            self.mid_time.config(text='05:00')

    def toggle_ad(self):
        self.ad_paused = False
        self.ad_oldtime = self.gametime
        self.ad_delta = 0
        if len(self.ad_manual_entry.get()) != 4: 
            timestr = '{:02}{:02}'.format(*divmod(self.gametime + 300, 60))
            self.ad_manual_entry.delete(0, tk.END)
            self.ad_manual_entry.insert(0, timestr)
        self.run_timer_ad()

    def run_timer_ad(self):
        if self.ad_paused:
            return
        if len(self.ad_manual_entry.get()) == 4:
            time = int(self.ad_manual_entry.get()[:2])*60 + int(self.ad_manual_entry.get()[2:])
        else:
            time = self.ad_oldtime + 300
        timestr = '{:02}:{:02}'.format(*divmod(time - self.gametime, 60))
        self.ad_time.config(text=timestr)
        self.ad_time.after(1000, self.run_timer_ad)
        if time - self.gametime == 0:
            self.ad_paused = True
            self.ad_button.config(text='Start')
            self.ad_time.config(text='05:00')

    def toggle_sup(self):
        self.sup_paused = False
        self.sup_oldtime = self.gametime
        self.sup_delta = 0
        if len(self.sup_manual_entry.get()) != 4: 
            timestr = '{:02}{:02}'.format(*divmod(self.gametime + 300, 60))
            self.sup_manual_entry.delete(0, tk.END)
            self.sup_manual_entry.insert(0, timestr)
        self.run_timer_sup()

    def run_timer_sup(self):
        if self.sup_paused:
            return
        if len(self.sup_manual_entry.get()) == 4:
            time = int(self.sup_manual_entry.get()[:2])*60 + int(self.sup_manual_entry.get()[2:])
        else:
            time = self.sup_oldtime + 300
        timestr = '{:02}:{:02}'.format(*divmod(time - self.gametime, 60))
        self.sup_time.config(text=timestr)
        self.sup_time.after(1000, self.run_timer_sup)
        if time - self.gametime == 0:
            self.sup_paused = True
            self.sup_button.config(text='Start')
            self.sup_time.config(text='05:00')

SpellChecker()