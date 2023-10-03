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
python app.py
```

### I18n

To help with the translation, do the following:

```shell
pylupdate5 app.py -ts ./lang/*.ts
# Manually edit the ts file you want to translate. e.g. ./lang/zh_CN.ts
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

