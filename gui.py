import wx
import datetime
import logging
import os
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # Force separate plot window

import matplotlib.pyplot as plt

from tasks.task1 import run_strategy as run_task1
from tasks.task2 import run_strategy as run_task2

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/gui.log", level=logging.INFO)

class TradingGUI(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Strategy Runner", size=(400, 500))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.script_choice = wx.Choice(panel, choices=["task1", "task2"])
        self.entry_time = wx.TextCtrl(panel)
        self.exit_time = wx.TextCtrl(panel)
        self.sl_ratio = wx.TextCtrl(panel)
        self.log_tf = wx.TextCtrl(panel)

        run_btn = wx.Button(panel, label="Run Strategy")

        self.date_picker = wx.TextCtrl(panel)
        self.task_choice_load = wx.Choice(panel, choices=["task1", "task2"])
        load_btn = wx.Button(panel, label="Load Waveform")

        for label, ctrl in [
            ("Select Script", self.script_choice),
            ("Entry Time", self.entry_time),
            ("Exit Time", self.exit_time),
            ("SL Ratio", self.sl_ratio),
            ("Log Time Frame", self.log_tf),
        ]:
            vbox.Add(wx.StaticText(panel, label=label))
            vbox.Add(ctrl, flag=wx.EXPAND | wx.ALL, border=5)

        vbox.Add(run_btn, flag=wx.ALL | wx.CENTER, border=10)
        vbox.Add(wx.StaticLine(panel))

        vbox.Add(wx.StaticText(panel, label="Date (YYYY-MM-DD)"))
        vbox.Add(self.date_picker, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(wx.StaticText(panel, label="Task"))
        vbox.Add(self.task_choice_load, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(load_btn, flag=wx.ALL | wx.CENTER, border=10)

        panel.SetSizer(vbox)

        run_btn.Bind(wx.EVT_BUTTON, self.on_run)
        load_btn.Bind(wx.EVT_BUTTON, self.on_load)

    def on_run(self, event):
        script = self.script_choice.GetStringSelection()
        entry = self.entry_time.GetValue()
        exit = self.exit_time.GetValue()
        sl = self.sl_ratio.GetValue()
        log_tf = self.log_tf.GetValue()
        date = datetime.date.today().strftime("%Y-%m-%d")

        logging.info(f"Running {script} with {entry}, {exit}, SL={sl}, TF={log_tf}")

        if script == "task1":
            output = run_task1(entry, exit, sl, log_tf, date)
        else:
            output = run_task2(entry, exit, sl, log_tf, date)

        wx.MessageBox(f"Output saved at:\n{output}", "Success")

    def on_load(self, event):
        date = self.date_picker.GetValue()
        task = self.task_choice_load.GetStringSelection()

        if not date or not task:
            wx.MessageBox("Please enter date and select task", "Error")
            return

        file_path = f"output/{task}/{date}_{task}.xlsx"

        if not os.path.exists(file_path):
            wx.MessageBox("File not found!", "Error")
            return

        df = pd.read_excel(file_path)
        print("Loaded file:", file_path)
        print(df.head())


        if "Time" not in df.columns or "Price" not in df.columns:
            wx.MessageBox("Excel missing Time or Price columns!", "Error")
        return

        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 4))
        plt.plot(df["Time"], df["Price"], marker='o')
        plt.title(f"{task.upper()} Price Waveform - {date}")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.grid(True)
        plt.tight_layout()
        plt.show(block=True)





app = wx.App()
frame = TradingGUI()
frame.Show()
app.MainLoop()
