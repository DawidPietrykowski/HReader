pyinstaller --distpath bin/fdash fdash/fdash.spec
Xcopy fdash\assets bin\fdash\assets\ /s /y
Xcopy fdash\lang bin\fdash\lang\ /s /y