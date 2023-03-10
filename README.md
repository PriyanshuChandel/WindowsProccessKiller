# Kill - A Windows process killer tool
Kill is a Windows process killer tool developed using Python. It allows you to select one or more hosts, select one or more processes to kill, and then execute the kill command on those hosts simultaneously.

## Getting Started

### Prerequisites
- `Python 3.x`: The script requires Python 3.x to be installed on the system. You can download and install Python 3.x from the official Python [website](https://www.python.org/downloads/).
- `subprocess` module: The script uses the subprocess module to run Windows commands. The module should be installed by default with Python. If it's not installed, you can install it using pip by running the command `pip install subprocess`
- `tkinter` module: The script uses the tkinter module to create a GUI. The module should be installed by default with Python. If it's not installed, you can install it using pip by running the command `pip install tkinter`
- `bs4` module: The script uses the BeautifulSoup module to parse XML data. You can install it using pip by running the command `pip install beautifulsoup4`
- `datetime` module: The script uses the datetime module to generate timestamps for the log file. The module should be installed by default with Python.
- `threading` module: The script uses the threading module to run processes in different threads. The module should be installed by default with Python.
- `os` modules: The script uses the os.path and os modules to manage files and paths. The modules should be installed by default with Python.

Make sure you have all these requirements installed before running the script.

### Installation
Once you have Python and the required libraries installed, you can download the source code from this repository or clone it using one of the following method:
- Clone: `git clone https://github.com/<username>/<repository>.git`
- Download: you can also download the ZIP file and extract it to your desired location.

### Usage
To run the program, simply navigate to the folder where you downloaded/cloned the source code and run the following command:
> `python KillGUI.py`

This will launch the GUI window of the program, which allows you to select hosts and processes to kill. The program has the following components:

#### Host selection
On the left-hand side of the GUI window, there is a list of hosts that you can select. The list is populated from an XML file located at conf/EQPT.xml (you have to configured it accordingly). You can select one or more hosts by clicking on the checkboxes next to the host names. Once you have selected the hosts, the selected host IPs will be displayed in the log file.

#### Process selection
On the right-hand side of the GUI window, there is a list of processes that you can select. The list is populated from a configuration file located at conf/ProcessToKill.conf (you have to configured it accordingly). You can select one or more processes by clicking on the checkboxes next to the process names. Once you have selected the processes, the selected process names will be displayed in the log file.

#### Log file
The log file is located in the log folder and is named based on the timestamp when the program is run. The log file displays the selected host IPs and the selected process names. It also displays the output and error messages generated by the Taskkill command when it is executed on the selected hosts and processes.

#### Kill button
Once you have selected the hosts and processes to kill, click the "Kill" button to execute the Taskkill command on the selected hosts and processes. The program will create a separate thread to run the Taskkill command on each host, allowing you to kill multiple processes on multiple hosts simultaneously. Once the process is complete, a message will be displayed in the GUI window indicating that the process has completed and you can check the log file for the results.

#### Contributions
Contributions to this repo are welcome. If you find a bug or have a suggestion for improvement, please open an issue on the repository. If you would like to make changes to the code, feel free to submit a pull request.

#### Acknowledgments
This program was created as a part of a programming challenge. Special thanks to the challenge organizers for the inspiration.
