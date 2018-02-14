rm mirror_visualize.exe
pyinstaller --clean --onefile -i favicon.ico mirror_visualize.py
mv dist/mirror_visualize.exe ./
rm -r build
rm -r dist
