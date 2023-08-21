from subprocess import Popen, PIPE
from tkinter import Tk, Label, Button, Checkbutton, IntVar, LabelFrame, Toplevel
from tkinter.ttk import Progressbar, Style
from tkinter.scrolledtext import ScrolledText
from os.path import join, dirname, exists
from os import makedirs
from datetime import datetime
from threading import Thread
from bs4 import BeautifulSoup
from xml.etree.ElementTree import ParseError
from time import time


def disableCheckboxes(checkBoxes):
    for checkbox in checkBoxes.keys():
        checkbox.config(state='disabled', cursor="arrow")


def enableCheckboxes(checkBoxesDict):
    for checkbox in checkBoxesDict.keys():
        checkbox.config(state='normal', cursor="hand2", bg='white')
        checkbox.deselect()


class processApp:
    if not exists('log'):
        makedirs('log')
    fileHandler = open(f"log/logs_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", 'a')
    process2Kill = 'conf/ProcessToKill.conf'
    equipXml = 'conf/EQPT.xml'
    credential = 'conf/credential.conf'
    iconFile = join(dirname(__file__), 'kill.ico')
    aboutIcon = join(dirname(__file__), 'info.ico')
    atLeastOneProcessKilledHostDict = {}
    allProcessKilledHostDict = {}
    unReachableHostDict = {}

    def __init__(self):
        self.equipDict = {}
        self.ipList = []
        self.varDictHost = {}
        self.checkBoxesHost = {}
        self.varDictProcess = {}
        self.checkBoxesProcess = {}
        self.processList = []
        self.processListSelected = []
        try:
            self.userName = open(self.credential, "r").readlines()[0].split('=')[1].strip()
            self.password = open(self.credential, "r").readlines()[1].split('=')[1].strip()
        except FileNotFoundError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] File [{self.credential}] '
                                   f'not found\n')
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] Something went wrong while opening'
                                   f' [{self.credential}][{e}]\n')
        self.window = Tk()
        self.window.config(bg='#F0F0F0')
        self.window.title('Kill - v1.1')
        self.window.geometry('300x455')
        self.window.iconbitmap(self.iconFile)
        self.window.resizable(False, False)
        self.selectHostLabel = Label(self.window, text='Select Host', font=('Arial', 9, 'bold'), fg='blue',
                                     bg='#F0F0F0').place(x=25, y=4)
        self.selectAllHostCheckboxVar = IntVar()
        self.selectAllHostCheckbox = Checkbutton(self.window, variable=self.selectAllHostCheckboxVar,
                                                 cursor='hand2', command=self.selectAllHost)
        self.selectAllHostCheckbox.place(x=1, y=4)
        self.checkBoxesScrolledTextHost = ScrolledText(self.window, width=14, height=12, bg='white', bd=4)
        self.checkBoxesScrolledTextHost.place(x=3, y=25)

        self.selectProcessLabel = Label(self.window, text='Select Process', font=(None, 9, 'bold'),
                                        fg='blue', bg='#F0F0F0').place(x=175, y=4)
        self.selectAllProcessCheckboxVar = IntVar()
        self.selectAllProcessCheckbox = Checkbutton(self.window, variable=self.selectAllProcessCheckboxVar,
                                                    cursor='arrow', command=self.selectAllProcess, state='disabled')
        self.selectAllProcessCheckbox.place(x=150, y=4)
        self.checkBoxesScrolledTextProcess = ScrolledText(self.window, width=14, height=12, bg='white', bd=4)
        self.checkBoxesScrolledTextProcess.place(x=150, y=25)

        self.submitBtn = Button(self.window, text='KILL', width=10, font=(None, 10, 'bold'),
                                command=self.killingProcess, bg='light grey', state='disabled')
        self.submitBtn.place(x=100, y=240)

        self.progressLabelFrame = LabelFrame(self.window, text='Progress', bd=3, labelanchor='n', relief='ridge',
                                             width=290, height=125)

        self.progressOverallLabel = Label(self.progressLabelFrame, text='Overall', font=(None, 9, 'bold'), bg='#F0F0F0')
        self.progressOverallLabel.place(x=1, y=5)
        self.progressOverall = Progressbar(self.progressLabelFrame, length=200, mode="determinate",
                                           style="Custom.Overall.Horizontal.TProgressbar")
        self.progressOverall.place(x=80, y=5)
        self.progressStyleOverall = Style()
        self.progressStyleOverall.theme_use('clam')
        self.progressStyleOverall.configure("Custom.Overall.Horizontal.TProgressbar", background="green", text='0/0')
        self.progressStyleOverall.layout('Custom.Overall.Horizontal.TProgressbar', [('Horizontal.Progressbar.trough',
                                                                                     {'children': [
                                                                                         ('Horizontal.Progressbar.pbar',
                                                                                          {'side': 'left',
                                                                                           'sticky': 'ns'})],
                                                                                         'sticky': 'nswe'}),
                                                                                    ('Horizontal.Progressbar.label',
                                                                                     {'sticky': ''})])

        self.progressPassLabel = Label(self.progressLabelFrame, text='All Killed', font=(None, 9, 'bold'), bg='#F0F0F0')
        self.progressPassLabel.place(x=1, y=30)
        self.progressPass = Progressbar(self.progressLabelFrame, length=200, mode="determinate",
                                        style="Custom.Pass.Horizontal.TProgressbar")
        self.progressPass.place(x=80, y=30)
        self.progressStylePass = Style()
        self.progressStylePass.theme_use('clam')
        self.progressStylePass.configure("Custom.Pass.Horizontal.TProgressbar", background="light green", text='0/0')
        self.progressStylePass.layout('Custom.Pass.Horizontal.TProgressbar', [('Horizontal.Progressbar.trough',
                                                                               {'children': [
                                                                                   ('Horizontal.Progressbar.pbar',
                                                                                    {'side': 'left',
                                                                                     'sticky': 'ns'})],
                                                                                   'sticky': 'nswe'}),
                                                                              ('Horizontal.Progressbar.label',
                                                                               {'sticky': ''})])

        self.progressPartialPassLabel = Label(self.progressLabelFrame, text='Partial-Killed', font=(None, 9, 'bold'),
                                              bg='#F0F0F0')
        self.progressPartialPassLabel.place(x=1, y=55)
        self.progressPartialPass = Progressbar(self.progressLabelFrame, length=200, mode="determinate",
                                               style="Custom.Partial.Horizontal.TProgressbar")
        self.progressPartialPass.place(x=80, y=55)
        self.progressStylePartialPass = Style()
        self.progressStylePartialPass.theme_use('clam')
        self.progressStylePartialPass.configure("Custom.Partial.Horizontal.TProgressbar", background="light green",
                                                text='0/0')
        self.progressStylePartialPass.layout('Custom.Partial.Horizontal.TProgressbar',
                                             [('Horizontal.Progressbar.trough',
                                               {'children': [
                                                   (
                                                       'Horizontal.Progressbar.pbar',
                                                       {'side': 'left',
                                                        'sticky': 'ns'})],
                                                   'sticky': 'nswe'}),
                                              ('Horizontal.Progressbar.label',
                                               {'sticky': ''})])

        self.progressUnreachableLabel = Label(self.progressLabelFrame, text='Unreachable', font=(None, 9, 'bold'),
                                              bg='#F0F0F0')
        self.progressUnreachableLabel.place(x=1, y=80)
        self.progressUnreachable = Progressbar(self.progressLabelFrame, length=200, mode="determinate",
                                               style="Custom.Unreachable.Horizontal.TProgressbar")
        self.progressUnreachable.place(x=80, y=80)
        self.progressStyleUnreachable = Style()
        self.progressStyleUnreachable.theme_use('clam')
        self.progressStyleUnreachable.configure("Custom.Unreachable.Horizontal.TProgressbar", background="red",
                                                text='0/0')
        self.progressStyleUnreachable.layout('Custom.Unreachable.Horizontal.TProgressbar',
                                             [('Horizontal.Progressbar.trough', {'children': [
                                                 ('Horizontal.Progressbar.pbar',
                                                  {'side': 'left',
                                                   'sticky': 'ns'})],
                                                 'sticky': 'nswe'}),
                                              ('Horizontal.Progressbar.label',
                                               {'sticky': ''})])

        self.progressLabelFrame.place(x=5, y=280)

        self.messageLabel = Label(self.window, font=('Arial', 9, 'bold'), bg='#F0F0F0')
        self.messageLabel.place(x=3, y=405)
        self.aboutBtn = Button(self.window, text='About', bg='brown', command=self.aboutWindow)
        self.aboutBtn.place(x=250, y=420)

    def populateEquipDict(self):
        self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Generating Host-IP pair from '
                               f'[{self.equipXml}]\n')
        try:
            for equip, ip in zip(BeautifulSoup(open(self.equipXml).read(), 'xml')('equipment'),
                                 BeautifulSoup(open(self.equipXml).read(), 'xml').findAll('ip')):
                self.equipDict[equip.get('Name')] = ip.text
                self.varDictHost[equip.get('Name')] = IntVar(value=0)
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Host-IP pair generated for '
                                   f'[{len(self.equipDict)}] hosts.\n{self.equipDict}\n')
        except FileNotFoundError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] file [{self.equipXml}] does '
                                   f'not exists. Checkbutton can not created\n')
        except IOError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] file [{self.equipXml}] unable'
                                   f' to read. Checkbutton can not created\n')
        except ParseError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] file [{self.equipXml}] is not'
                                   f' formatted as valid xml. Checkbutton can not created\n')
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] {e} \n')
        self.fileHandler.flush()

    def populateProcessDict(self):
        self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] extracting process from '
                               f'[{self.process2Kill}]\n')
        try:
            for eachProcess in open(self.process2Kill, "r").read().split('\n'):
                self.processList.append(eachProcess.strip())
                self.varDictProcess[eachProcess.strip()] = IntVar(value=0)
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] [{len(self.processList)}] Processes'
                                   f' extracted are \n{self.processList}\n')
        except FileNotFoundError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] File [{self.process2Kill}] '
                                   f'not found. Checkbutton can not created\n')
        except IOError:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] file [{self.process2Kill}] unable'
                                   f' to read. Checkbutton can not created\n')
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] Something went wrong while opening'
                                   f' [{self.process2Kill}][{e}]\n')
        self.fileHandler.flush()

    def checkboxCommandHost(self):
        self.messageLabel.config(text='')
        self.progressStyleOverall.configure("Custom.Overall.Horizontal.TProgressbar", text='0/0')
        self.progressStylePass.configure("Custom.Pass.Horizontal.TProgressbar", text='0/0')
        self.progressStyleUnreachable.configure("Custom.Unreachabl.Horizontal.TProgressbar", text='0/0')
        self.progressOverall['value'] = 0
        self.progressPass['value'] = 0
        self.progressUnreachable['value'] = 0
        self.ipList = [self.equipDict[key] for key in self.equipDict.keys() if self.varDictHost[key].get() == 1]
        for checkbox, checkboxText in self.checkBoxesHost.items():
            checkbox.config(bg='light green' if self.varDictHost[checkboxText].get() == 1 else 'white')
        self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Selected Hosts to proceed are '
                               f'{self.ipList} \n')
        if len(self.ipList) != len(self.checkBoxesHost):
            self.selectAllHostCheckbox.deselect()
        elif len(self.ipList) == len(self.checkBoxesHost):
            self.selectAllHostCheckbox.select()
        self.fileHandler.flush()

    def checkboxCommandProcess(self):
        self.processListSelected = [eachProcess for eachProcess in self.processList if
                                    self.varDictProcess[eachProcess].get() == 1]
        for checkbox, checkboxText in self.checkBoxesProcess.items():
            checkbox.config(bg='orange' if self.varDictProcess[checkboxText].get() == 1 else 'white')
        self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Selected processes to proceed are '
                               f'{self.processListSelected} \n')
        if len(self.processListSelected) != len(self.checkBoxesProcess):
            self.selectAllProcessCheckbox.deselect()
        elif len(self.processListSelected) == len(self.checkBoxesProcess):
            self.selectAllProcessCheckbox.select()
        self.fileHandler.flush()

    def enableProcessCheckBtnSubmitBtn(self, *args):
        hostCheckboxesState = [var.get() for var in self.varDictHost.values()]
        if any(hostCheckboxesState):
            self.selectAllProcessCheckbox.config(state='normal')
            self.selectAllProcessCheckbox.configure(cursor="hand2")
            for processCheckbox in self.checkBoxesProcess.keys():
                processCheckbox.config(state='normal')
                processCheckbox.configure(cursor="hand2")
        else:
            self.selectAllProcessCheckbox.deselect()
            self.selectAllProcessCheckbox.config(state='disabled')
            self.selectAllProcessCheckbox.configure(cursor="arrow")
            processVarList = list(self.varDictProcess.values())
            for index, processCheckbox in enumerate(self.checkBoxesProcess):
                if processVarList[index].get() == 1:
                    processCheckbox.deselect()
                processCheckbox.config(state='disabled', bg='white')
                processCheckbox.configure(cursor="arrow")
        processCheckboxesState = [var.get() for var in self.varDictProcess.values()]
        if any(processCheckboxesState):
            self.submitBtn.config(state='normal', bg='red')
        else:
            self.submitBtn.config(state='disabled', bg='light grey')

    def selectAllHost(self):
        selectAllHostCheckboxVarState = self.selectAllHostCheckboxVar.get()
        if selectAllHostCheckboxVarState:
            for checkbox in self.checkBoxesHost.keys():
                checkbox.select()
            self.checkboxCommandHost()
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] All Host selected by [ALL]\n')
        else:
            for checkbox in self.checkBoxesHost.keys():
                checkbox.deselect()
            self.checkboxCommandHost()
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] All Host deselected by [ALL]\n')
        self.fileHandler.flush()

    def selectAllProcess(self):
        selectAllProcessCheckboxVarState = self.selectAllProcessCheckboxVar.get()
        if selectAllProcessCheckboxVarState:
            for checkbox in self.checkBoxesProcess.keys():
                checkbox.select()
            self.checkboxCommandProcess()
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] All Processes selected by [ALL]\n')
        else:
            for checkbox in self.checkBoxesProcess.keys():
                checkbox.deselect()
            self.checkboxCommandProcess()
            self.fileHandler.write(
                f'{datetime.now().replace(microsecond=0)} [Info] All Processes deselected by [ALL]\n')
        self.fileHandler.flush()

    def killingProcess(self):
        def inner():
            startTime = time()
            self.submitBtn.config(state='disabled')
            disableCheckboxes(self.checkBoxesProcess)
            disableCheckboxes(self.checkBoxesHost)
            self.selectAllProcessCheckbox.config(state='disabled')
            self.selectAllHostCheckbox.config(state='disabled')
            self.messageLabel.config(text='Killing selected processes...')
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Killing selected processes...\n')
            self.progressStyleOverall.configure("Custom.Overall.Horizontal.TProgressbar", text=f'0/{len(self.ipList)}')
            self.progressStylePass.configure("Custom.Pass.Horizontal.TProgressbar", text=f'0/{len(self.ipList)}')
            self.progressStyleUnreachable.configure("Custom.Unreachable.Horizontal.TProgressbar",
                                                    text=f'0/{len(self.ipList)}')
            self.progressStyleUnreachable.configure("Custom.Partial.Horizontal.TProgressbar",
                                                    text=f'0/{len(self.ipList)}')
            for ip in self.ipList:
                hostName = {v: k for k, v in self.equipDict.items()}.get(ip)
                hostReachability = self.isHostReachable(ip, hostName)
                self.fileHandler.flush()
                if hostReachability:
                    self.processKill(ip, hostName)
                self.updateProgress(self.progressOverall, self.progressStyleOverall,
                                    len(self.atLeastOneProcessKilledHostDict) + len(self.unReachableHostDict) +
                                    len(self.allProcessKilledHostDict), len(self.ipList), 'Overall')
            endTime = time()
            self.messageLabel.config(text='Done, check logs!')
            enableCheckboxes(self.checkBoxesHost)
            self.selectAllHostCheckbox.deselect()
            self.selectAllProcessCheckbox.config(state='normal')
            self.selectAllHostCheckbox.config(state='normal')
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Done..\n')
            for successItem in self.allProcessKilledHostDict.items():
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Success] {successItem}\n')
            for partialItem in self.atLeastOneProcessKilledHostDict.items():
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Partial-Success] {partialItem}\n')
            for unReachableHost in self.unReachableHostDict.items():
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [FAIL] {unReachableHost}\n')
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] All processes KILLED for Total Host'
                                   f' - {len(self.allProcessKilledHostDict)}\n')
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Partial processes KILLED for Total '
                                   f'Host - {len(self.atLeastOneProcessKilledHostDict)}\n')
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] All processes FAILED to kill for '
                                   f'Total UnReachableHost - {len(self.unReachableHostDict)}\n')
            elapsedTime = endTime - startTime
            hours, remainder = divmod(elapsedTime, 3600)
            minutes, remainder = divmod(remainder, 60)
            seconds, milliseconds = divmod(remainder, 1)
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} ELAPSED TIME TO COMPLETE WHOLE PROCESS IS '
                                   f'{int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds '
                                   f'{int(milliseconds * 1000)} milliseconds')
            self.fileHandler.flush()

        threadKillProcess = Thread(target=inner)
        threadKillProcess.start()

    def isHostReachable(self, ip, hostName):
        try:
            commandConstruct = f"ping -n 2 {ip}"
            commandExecution = Popen(commandConstruct, stdout=PIPE, stderr=PIPE, shell=True)
            output = commandExecution.stdout.read().decode().strip()
            error = commandExecution.stderr.read().decode().strip()
            returnCode = commandExecution.wait()
            if returnCode == 0:
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Server [{hostName}_{ip}] is '
                                       f'CONNECTED\n')
                return True
            elif returnCode == 1:
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] Server [{hostName}_{ip}] is '
                                       f'not reachable, checking next host.\n')
                self.unReachableHostDict[hostName] = 'UnReachable'
                self.updateProgress(self.progressUnreachable, self.progressStyleUnreachable,
                                    len(self.unReachableHostDict), len(self.ipList), 'Unreachable')
                return False
            else:
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR_UnknownReturnCode1/3] Server '
                                       f'[{hostName}_{ip}] is not reachable\n')
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR_UnknownReturnCode2/3] Server '
                                       f'[{hostName}_{ip}] output >>> {output}\n')
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR_UnknownReturnCode3/3] Server '
                                       f'[{hostName}_{ip}] error >>> {error}\n')
                self.updateProgress(self.progressUnreachable, self.progressStyleUnreachable,
                                    len(self.unReachableHostDict), len(self.ipList), 'Unreachable')
                return False
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Exceptional_ERROR] Server '
                                   f'[{hostName}_{ip}] error >>> {e}\n')
            self.updateProgress(self.progressUnreachable, self.progressStyleUnreachable, len(self.unReachableHostDict),
                                len(self.ipList), 'Unreachable')
            return False

    def processKill(self, ip, hostName):
        killedProcessSuccessList = []
        killedProcessFailList = []
        processIterationTrack = len(self.processListSelected)
        for eachSelectedProcess in self.processListSelected:
            try:
                commandConstruct = f'Taskkill /S {ip} /U {self.userName} /P {self.password} /F /T /IM ' \
                                   f'{eachSelectedProcess}'

                commandExecution = Popen(commandConstruct, stdout=PIPE, stderr=PIPE, shell=True)
                output = commandExecution.stdout.read().decode().strip()
                error = commandExecution.stderr.read().decode().strip()
                returnCode = commandExecution.wait()
                if returnCode == 0:
                    self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [SUCCESS] Server '
                                           f'[{hostName}_{ip}] process [{eachSelectedProcess}] output >>> '
                                           f'{output}\n')
                    killedProcessSuccessList.append(eachSelectedProcess)
                elif returnCode == 128:
                    self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR128] Server '
                                           f'[{hostName}_{ip}] process [{eachSelectedProcess}] error >>> '
                                           f'{error}\n')
                    killedProcessFailList.append(eachSelectedProcess)
                elif returnCode == 1:
                    self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR1] Server '
                                           f'[{hostName}_{ip}] process [{eachSelectedProcess}] error >>> '
                                           f'{error}\n')
                    killedProcessFailList.append(eachSelectedProcess)
                else:
                    self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} '
                                           f'[ERROR_UnknownReturnCode] Server [{hostName}_{ip}] process '
                                           f'[{eachSelectedProcess}] error >>> {error}\n')
                    killedProcessFailList.append(eachSelectedProcess)
                processIterationTrack -= 1
                if processIterationTrack == 0:
                    if len(killedProcessSuccessList) == len(self.processListSelected):
                        self.allProcessKilledHostDict[hostName] = killedProcessSuccessList
                        self.updateProgress(self.progressPass, self.progressStylePass,
                                            len(self.allProcessKilledHostDict), len(self.ipList), 'Pass')
                    elif len(self.processListSelected) > len(killedProcessSuccessList) > 0:
                        self.atLeastOneProcessKilledHostDict[hostName] = killedProcessSuccessList
                        self.updateProgress(self.progressPartialPass, self.progressStylePartialPass,
                                            len(self.atLeastOneProcessKilledHostDict), len(self.ipList),
                                            'Partial')
            except Exception as e:
                self.fileHandler.write(
                    f'{datetime.now().replace(microsecond=0)} [ERROR] Server [{hostName}][{ip}] exceptional'
                    f' error >>> {e}\n')
        self.fileHandler.flush()

    def updateProgress(self, progressBar, progressStyle, newVal, totalVal, state):
        resultVal = f'{newVal}/{totalVal}'
        progressBar['value'] = round((newVal / totalVal) * 100, 2)
        progressStyle.configure(f"Custom.{state}.Horizontal.TProgressbar", text=resultVal)
        self.window.update()

    def aboutWindow(self):
        aboutWin = Toplevel(self.window)
        aboutWin.grab_set()
        aboutWin.geometry('285x90')
        aboutWin.resizable(False, False)
        aboutWin.title('About')
        aboutWin.iconbitmap(self.aboutIcon)
        aboutWinLabel = Label(aboutWin,
                              text=f'Version - 1.1\nDeveloped by Priyanshu\nFor any improvement please reach on '
                                   f'below email\nEmail : priyanshu.kumar@alstomgroup.com\nMobile : '
                                   f'+91-8285775109 '
                                   f'', font=('Helvetica', 9)).place(x=1, y=6)

    def runGUI(self):
        self.populateEquipDict()
        try:
            for equips in self.equipDict.keys():
                hostVar = IntVar()
                hostCheckButtons = Checkbutton(self.checkBoxesScrolledTextHost, text=equips, variable=hostVar,
                                               bg='white',
                                               cursor="hand2", command=self.checkboxCommandHost)
                self.varDictHost[equips] = hostVar
                self.checkBoxesHost[hostCheckButtons] = equips
                hostCheckButtons.pack()
                self.checkBoxesScrolledTextHost.window_create('end', window=hostCheckButtons)
                hostVar.trace_add('write', self.enableProcessCheckBtnSubmitBtn)
            if len(self.checkBoxesHost) > 0:
                self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [Info] Host Checkboxes created.. \n')
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] Host Checkboxes failed to create. '
                                   f'{e}\n')
        self.populateProcessDict()
        try:
            for eachProcess in self.processList:
                processVar = IntVar()
                processCheckButtons = Checkbutton(self.checkBoxesScrolledTextProcess, text=eachProcess,
                                                  variable=processVar,
                                                  bg='white', cursor="hand2", command=self.checkboxCommandProcess)
                self.varDictProcess[eachProcess] = processVar
                self.checkBoxesProcess[processCheckButtons] = eachProcess
                processCheckButtons.pack()
                self.checkBoxesScrolledTextProcess.window_create('end', window=processCheckButtons)
                processVar.trace_add('write', self.enableProcessCheckBtnSubmitBtn)
            if len(self.checkBoxesProcess) > 0:
                self.fileHandler.write(
                    f'{datetime.now().replace(microsecond=0)} [Info] Process Checkboxes created.. \n')
            disableCheckboxes(self.checkBoxesProcess)
        except Exception as e:
            self.fileHandler.write(f'{datetime.now().replace(microsecond=0)} [ERROR] Process Checkboxes failed to '
                                   f'create. {e}\n')
        self.fileHandler.flush()
        self.window.mainloop()


if __name__ == '__main__':
    killApp = processApp()
    killApp.runGUI()
