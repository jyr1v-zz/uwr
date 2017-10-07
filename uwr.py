#!/usr/bin/env python
import wx
import serial
import serial.tools.list_ports
import threading
import time
import copy

# debugging
import pdb

SERIALRX = wx.NewEventType()

# bind to serial data receive events
EVT_SERIALRX = wx.PyEventBinder(SERIALRX, 0)

class SerialRxEvent(wx.PyCommandEvent):
    eventType = SERIALRX
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = copy.deepcopy(data)

    def Clone(self):
        self.__class__(self.GetId(), self.data)

class MyFrame(wx.Frame):

    def __init__(self, parent, id, title):
        self.blueGoals  = 257
        self.whiteGoals = 256

        wx.Frame.__init__(self, parent, id, title)

        self.__do_layout()

        self.Bind(EVT_SERIALRX, self.OnUpdate)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.serial = None
        self.thread = threading.Thread(target=self.RxThread)
        self.alive  = threading.Event()
        self.thread.setDaemon(1)
        self.alive.set()
        self.thread.start()

    def __do_layout(self):
        self.rootPanel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        self.rootPanel.SetBackgroundColour(wx.Colour(0, 255, 0))

        innerPanel = wx.Panel(self.rootPanel,-1, size=(900,650), style=wx.ALIGN_CENTER)
        innerPanel.SetBackgroundColour(wx.Colour(0, 255, 0))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.innerBox = wx.BoxSizer(wx.VERTICAL)

        self.stateTxt = wx.StaticText(innerPanel, id=-1, label="",style=wx.ALIGN_CENTER, name="")
        self.stateTxt.SetFont(wx.Font(28, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.stateTxt.SetForegroundColour((255,255,255))

        self.timerTxt = wx.StaticText(innerPanel, id=-1, label="TEXT HERE",style=wx.ALIGN_CENTER, name="")
        self.timerTxt.SetFont(wx.Font(48, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timerTxt.SetForegroundColour((255,255,255))

        self.goalTxt = wx.StaticText(innerPanel, id=-1, label="0-0",style=wx.ALIGN_CENTER, name="")
        self.goalTxt.SetFont(wx.Font(48, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.goalTxt.SetForegroundColour((255,255,255))

        self.connectionTxt = wx.StaticText(innerPanel, id=-1, label="Connected",style=wx.ALIGN_CENTER, name="")
        self.connectionTxt.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

        self.rawData = wx.StaticText(innerPanel, id=-1, label="no data",style=wx.ALIGN_CENTER, name="")
        self.rawData.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

        self.innerBox.AddSpacer((150,75))
        self.innerBox.Add(self.stateTxt, 0, wx.CENTER)
        self.innerBox.Add(self.timerTxt, 0, wx.CENTER)
        self.innerBox.Add(self.goalTxt, 0, wx.CENTER)
        self.innerBox.Add(self.connectionTxt, 0, wx.CENTER)
        self.innerBox.Add(self.rawData, 0, wx.CENTER)
        self.innerBox.AddSpacer((150,75))
        innerPanel.SetSizer(self.innerBox)

        hbox.Add(innerPanel, 0, wx.ALL|wx.ALIGN_CENTER)
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)

        self.rootPanel.SetSizer(vbox)
        vbox.Fit(self)
        self.Layout()
        self.SetSize((1000, 750))

    def OnUpdate(self, event):
        if len(event.data["raw"]) >= 49:
            self.state = " "
            if self.state != str(event.data["raw"][7:8]):
                self.state = str(event.data["raw"][7:8])

                if self.state == "T":
                    self.stateTxt.SetLabel("Timeout")
                elif self.state == "P":
                    self.stateTxt.SetLabel("Penalty")
                else:
                    self.stateTxt.SetLabel("")

            if self.timerTxt.GetLabel() != str(event.data["raw"][2:7]):
                self.timerTxt.SetLabel(str(event.data["raw"][2:7]))

            if self.blueGoals != int(event.data["raw"][8:10]) or self.whiteGoals != int(event.data["raw"][11:13]):
                self.blueGoals  = int(event.data["raw"][8:10])
                self.whiteGoals = int(event.data["raw"][11:13])
                self.goalTxt.SetLabel(str(self.whiteGoals) + "-" + str(self.blueGoals))

            if self.rawData.GetLabel() != str(event.data["raw"]):
                self.rawData.SetLabel(str(event.data["raw"]))
        else:
            self.stateTxt.SetLabel("")
            self.timerTxt.SetLabel("")
            self.goalTxt.SetLabel("")
            self.rawData.SetLabel("")

        if self.connectionTxt.GetLabel() != event.data["connState"]:
            self.connectionTxt.SetLabel(event.data["connState"])

        self.innerBox.Layout()

    def RxThread(self):
        data = {
            "connState": "Searching device...",
            "raw": "no data"
        }

        data["connState"] = "Searching..."
        data["raw"] = ""
        self.GetEventHandler().AddPendingEvent(SerialRxEvent(self.GetId(), data))

        ser = None
        rx = ""
        while self.alive.isSet():

            if "Searching..." in data["connState"]:
                ports = list(serial.tools.list_ports.comports())

                for p in ports:
                    if "ATEN USB" in p.description:
                        try:
                            data["connState"] = "Found..."
                            self.GetEventHandler().AddPendingEvent(SerialRxEvent(self.GetId(), data))
                            ser = serial.Serial(p.device, 9600, parity=serial.PARITY_NONE,
                                    bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=0.5)
                            data["connState"] = "Connected"
                            self.whiteGoals = 2580 # this is just so that goals will be drawed
                            self.GetEventHandler().AddPendingEvent(SerialRxEvent(self.GetId(), data))
                        except serial.serialutil.SerialException:
                            time.sleep(1) # try connecting again in 1 sec
                        break
            else:
                try:
                    rx = rx + ser.read(ser.inWaiting())

                    if not rx.startswith("DA"):
                        rx = ""

                    if len(rx) >= 49:
                        if data["raw"] != rx:
                            data["connState"] = "" # connected
                            data["raw"] = rx
                            self.GetEventHandler().AddPendingEvent(SerialRxEvent(self.GetId(), data))
                        rx = ""


                except serial.serialutil.SerialException:
                    data["connState"] = "Searching..."
                    data["raw"] = ""
                    self.GetEventHandler().AddPendingEvent(SerialRxEvent(self.GetId(), data))
                    ser.close()

                time.sleep(0.05)

        # make sure the port is closed before ending the rx thread
        if self.serial != None:
            self.serial.close()             #cleanup
            self.serial = None


    def OnClose(self, event):
        """Called on application shutdown."""
        """Stop the receiver thread, wait util it's finished."""
        if self.thread is not None:
            self.alive.clear()          #clear alive event for thread
            self.thread.join()          #wait until thread has finished
            self.thread = None

        if self.serial != None:
            self.serial.close()             #cleanup
            self.serial = None

        self.Destroy()                  #close windows, exit app

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'UWR')
        frame.Show(True)
        frame.Center()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
