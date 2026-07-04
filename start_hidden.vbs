' Starts the pharmacy dashboard silently in the background (no Command Prompt window).
' To use: create a shortcut to this file in your Startup folder (Win+R, type shell:startup).
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "cmd /c python app.py", 0, False
