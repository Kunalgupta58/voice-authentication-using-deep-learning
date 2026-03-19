# Venv Fix & Activation Guide

Your virtual environment is actually working correctly, but your terminal is not currently "using" it. This is why your `pip install` commands are going to your global Python instead of the project folder.

### 1. How to Activate the Environment
In your terminal (PowerShell), run this exact command:
```powershell
.\venv\Scripts\Activate.ps1
```
You will see `(venv)` appear in front of your command prompt.

### 2. How to Install Packages in the Venv
Once activated, simply run:
```powershell
pip install -r requirements.txt
```
If you don't want to activate it every time, you can run commands directly through the venv like this:
```powershell
.\venv\Scripts\pip install torch torchaudio numpy
.\venv\Scripts\python test_ml.py
```

### 3. Fixing the IDE (VS Code)
Your IDE might still be looking at the wrong Python. 
1. Press `Ctrl + Shift + P`
2. Type `Python: Select Interpreter`
3. Choose the one that says `('venv': venv) .\venv\Scripts\python.exe`

I have also updated your project config to tell the IDE to expect Python 3.13 instead of 3.11.

### 4. Starting the App Reliably
Use one of these commands from the project folder:

```powershell
.\start_localhost.ps1
```

or:

```cmd
start_localhost.bat
```

Both start the backend on:
```text
http://127.0.0.1:8000
```

In VS Code, you can also use the `Voice Auth Localhost` launch configuration from the Run and Debug panel.
