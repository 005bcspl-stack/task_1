SENSEX Zerodha Data Tool

This project is a Python-based tool built to work with market data using the Zerodha Kite API. It focuses on organizing tasks, generating outputs, and providing a simple GUI interface to interact with the data.

The goal of this project is to make market data handling more structured and easier to analyze.

Project Structure

gui.py
Provides a graphical interface to run tasks and interact with the system without needing to use the terminal every time.

tasks/
Contains different task modules related to market data processing and analysis.

output/task1/
Stores generated outputs from Task 1. This may include processed data files, reports, or analysis results.

logs/
Keeps log files that help track program execution, errors, and activity history. Useful for debugging and monitoring.

What This Project Does

Connects to Zerodha Kite API

Runs different market data–related tasks

Saves processed results into organized output folders

Maintains logs for tracking execution

Provides a GUI for easier operation

How to Run
1. Install dependencies
pip install pandas kiteconnect openpyxl


(Add any additional libraries if your tasks require them.)

2. Add your API credentials

Make sure your API keys are stored securely (usually in a separate file like keys.py).

⚠ Do not upload API credentials to GitHub.

3. Run the GUI
python gui.py


Use the interface to run the required tasks.

Logs

All runtime information and errors are recorded inside the logs folder.
If something doesn’t work as expected, checking these logs is the first step.

Output

Each task saves its results inside the output/ directory in a structured way, making it easier to track and review generated data.

Suggested .gitignore
__pycache__/
logs/
*.xlsx
keys.py


This keeps temporary files, logs, and sensitive data out of version control.

Future Improvements

Add more automated analysis tasks

Improve GUI features and usability

Add data visualization

Add support for more market instruments
