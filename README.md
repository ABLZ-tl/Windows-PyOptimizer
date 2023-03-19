# Windows Optimizing

This is a program that helps optimize Windows performance by cleaning up junk files, managing startup programs, and cleaning up the registry. It provides a simple graphical user interface for users to perform these actions.

## Requirements

* Python 3.x
* PyQt5
* winreg
* subprocess
* os
* sys
* winshell
* win32con

## Installation

1. Clone the repository: `git clone https://github.com/ABLZ-tl/Windows-PyOptimizer.git`
2. Install the required dependencies by running `pip install -r requirements.txt` in the project directory.
3. Run the program by executing `python optimizer.py` in the project directory.

## Usage

1. Clean Registry: This action will remove unused registry entries that could improve system performance. A backup of the registry will be created automatically before making any changes.
2. Restore Registry: This action restores a backup of the registry. The user is prompted to select the backup file to restore.
3. Clean Junk Files: This action removes temporary and junk files from the system. The Recycle Bin is also emptied.
4. Manage Startup Programs: This action allows the user to manage the programs that run at startup. The user can choose which programs to enable or disable.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome. Please submit a pull request with your changes.

## Credits

This project was created by Alan Baruch Lozano Zamora.
