from src.fileLoading import fileLoader as fLoader

path = fLoader.loadDll('DLLS/DobotDll.dll')

print (path)