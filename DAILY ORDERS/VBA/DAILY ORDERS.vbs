scriptdir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Set xlapp = CreateObject("Excel.Application")
xlapp.Visible = false
Set Wb = XlApp.Workbooks.Open(scriptdir & "\DAILY ORDERS.xlsm")