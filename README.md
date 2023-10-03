# JH PDF Merger

## Developing

### Install dependencies

```shell
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```
### Runnning

```shell
lrelease ./lang/*.ts # Generate ./lang/*.qm files
python app.py
```
`lrelease` is shipped with Qt. You can find it in the Qt installation directory. e.g.
```
C:\Qt\Qt5.14.2\5.14.2\mingw73_64\bin\lrelease.exe
```

If you don't want to install Qt, you can get *.qm files from our latest release. Download the zip file and extract it, *qm files are in the `lang/` folder.


### I18n

To help with the translation, do the following steps.

First run pylupdate5 to update the .ts files.

```shell
pylupdate5 app.py -ts ./lang/*.ts
```
Then manually edit the ts file you want to translate. e.g. ./lang/zh_CN.ts

Finally use Qt’s lrelease utility to convert the .ts files to .qm files.
```shell
lrelease ./lang/*.ts
```

### Packaging

To package the application, run the following command.

```shell
lrelease ./lang/*.ts # Generate ./lang/*.qm files
pip install PyInstaller
pyinstaller app.spec
```
Now you can find `dist/jh_pdf_merger` folder, which contains the executable file `JH PDF Merger.exe` and all the dependencies.
You can copy this folder to anywhere you want.

