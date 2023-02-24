from subprocess import Popen, PIPE  # To run the windows commands
from tkinter import Tk, Label, Button, Checkbutton, IntVar, Frame  # To create GUI
from tkinter.scrolledtext import ScrolledText  # To create dynamic checkboxes
from os.path import join, dirname, exists  # TO manage the files and path
from os import makedirs  # To create folder
from datetime import datetime  # Required timestamp to write in log file
from threading import Thread  # To run processes in different threads
from bs4 import BeautifulSoup  # TO parse the xml

Icon_File = join(dirname(__file__), 'kill.ico')
Process_to_Kill = 'conf/ProcessToKill.conf'
Eqpt_XML = 'conf/EQPT.xml'
Credential = 'conf/Credential.conf'

User_Name = open(Credential, "r").readlines()[0].split('=')[1].strip()
Password = open(Credential, "r").readlines()[1].split('=')[1].strip()

window = Tk()
window.config(bg='grey')
window.title('Kill - Developed by PK')
window.minsize(width=300, height=360)
window.maxsize(width=300, height=360)
window.iconbitmap(Icon_File)
window.resizable(False, False)

if not exists('log'):
    makedirs('log')
file_handler = open(f"log/logs_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", 'a')

def Command_Construction_Execution(ip, username, password, process, host_name):
    try:
        Command_Construct = f'Taskkill /S {ip} /U {username} /P {password} /F /T /IM {process}'
        Command_execution = Popen(Command_Construct, stdout=PIPE, stderr=PIPE, shell=True)
        output1 = Command_execution.stdout.read().decode().strip()
        error1 = Command_execution.stderr.read().decode().strip()
        file_handler.write(
                f'{datetime.now().replace(microsecond=0)} Server [{host_name}][{ip}] process [{process}] output >>> {output1}\n')
        file_handler.write(
                f'{datetime.now().replace(microsecond=0)} Server [{host_name}][{ip}] process [{process}] error >>> {error1}\n')
    except Exception as e:
        file_handler.write(
            f'{datetime.now().replace(microsecond=0)} Server [{host_name}][{ip}] exceptional error >>> {e}\n')

def threading_checkbutton3():
    thread_checkbutton3 = Thread(target=checkbutton3_func)
    thread_checkbutton3.start()

def checkbutton3_func():
    [eq.select() for eq in eqpt_checkbutton_list if checkbutton3_var.get() == 1]
    [eq.deselect() for eq in eqpt_checkbutton_list if checkbutton3_var.get() == 0]
    eqpt_checkbox_command()

def threading_checkbutton4():
    thread_checkbutton4 = Thread(target=checkbutton4_func)
    thread_checkbutton4.start()

def checkbutton4_func():
    [pr.select() for pr in process_checkbutton_list if checkbutton4_var.get() == 1]
    [pr.deselect() for pr in process_checkbutton_list if checkbutton4_var.get() == 0]
    process_checkbox_command()

def threading_btn5():
    thread_btn5 = Thread(target=btn5_func)
    thread_btn5.start()

def btn5_func():
    labl6.config(text='Killing selected processes...')
    try:
        for ip in ip_list:
            for selected_process in process_list_selected:
                host_name = {v: k for k, v in eqpt_dict.items()}.get(ip)
                Command_Construction_Execution(ip, User_Name, Password, selected_process, host_name)
    except Exception as e:
        file_handler.write(f'{datetime.now().replace(microsecond=0)} Error >>> {e}\n')
    labl6.config(text='Killing process completed, check logs file for status.')

labl1 = Label(window, text='Select host from below', font=(None, 9, 'bold'), bg='grey').place(x=1, y=4)
text1 = ScrolledText(window, width=14, height=12, bg='white', bd=4)
text1.place(x=3, y=25)
eqpt_dict = dict()
for eqpt, ip in zip(BeautifulSoup(open(Eqpt_XML).read(), 'xml')('equipment'),
                    BeautifulSoup(open(Eqpt_XML).read(), 'xml').findAll('ip')):
    eqpt_dict[eqpt.get('Name')] = ip.text
ip_list = list()

def eqpt_checkbox_command():
    global ip_list
    ip_list = [eqpt_dict[key] for key in eqpt_dict.keys() if var_dict_eqpt[key].get() == 1]
    file_handler.write(f'{datetime.now().replace(microsecond=0)} Selected host to proceed  >>> {ip_list}\n')

eqpt_checkbutton_list = list()
var_dict_eqpt = dict()
for eqpts in eqpt_dict.keys():
    var_dict_eqpt[eqpts] = IntVar(value=0)
    checkbutton1 = Checkbutton(text1, text=eqpts, variable=var_dict_eqpt[eqpts], onvalue=1, offvalue=0, bg='white',
                               cursor="hand2", command=eqpt_checkbox_command)
    checkbutton1.pack()
    eqpt_checkbutton_list.append(checkbutton1)
    text1.window_create('end', window=checkbutton1)

labl2 = Label(window, text='Select process to kill', font=(None, 9, 'bold'), bg='grey').place(x=155, y=4)
text2 = ScrolledText(window, width=14, height=12, bg='white', bd=4)
text2.place(x=150, y=25)
process_list = list()
for process in open(Process_to_Kill, "r").read().split('\n'):
    process_list.append(process.strip())

process_list_selected = list()
def process_checkbox_command():
    global process_list_selected
    process_list_selected = [process for process in process_list if var_dict_process[process].get() == 1]
    file_handler.write(f'{datetime.now().replace(microsecond=0)} Selected processes to proceed  >>> {process_list_selected}\n')

process_checkbutton_list = list()
var_dict_process = dict()
for process in process_list:
    var_dict_process[process] = IntVar(value=0)
    checkbutton2 = Checkbutton(text2, text=process, variable=var_dict_process[process], onvalue=1, offvalue=0,
                               bg='white',
                               cursor="hand2", command=process_checkbox_command)
    checkbutton2.pack()
    process_checkbutton_list.append(checkbutton2)
    text2.window_create('end', window=checkbutton2)

checkbutton3_var = IntVar()
checkbutton3 = Checkbutton(window, text='Select All', variable=checkbutton3_var, onvalue=1, offvalue=0, bg='Grey',
                           cursor="hand2", command=threading_checkbutton3)
checkbutton3.place(x=8, y=230)
checkbutton4_var = IntVar()
checkbutton4 = Checkbutton(window, text='Select All', variable=checkbutton4_var, onvalue=1, offvalue=0, bg='Grey',
                           cursor="hand2", command=threading_checkbutton4)
checkbutton4.place(x=155, y=230)

btn5 = Button(window, text='KILL', width=10, font=(None, 10, 'bold'), command=threading_btn5, bg='RED')
btn5.place(x=100, y=255)
frame5 = Frame(window, bg="white", bd=20, width=288,
               height=60, cursor="target").place(x=6, y=290)
labl5 = Label(frame5, text='Status:', font=(None, 9, 'bold'), bg='white')
labl5.place(x=6, y=290)

labl6 = Label(window, font=(None, 9, 'bold'), bg='white', wraplength=290, justify='left')
labl6.place(x=6, y=310)

window.mainloop()