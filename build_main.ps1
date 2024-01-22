pyinstaller -w -y ./qt_main.py


Copy-Item ./.env -Destination ./dist/main -Force
Copy-Item -Path ./prompts/ -Destination ./dist/main/prompts -Recurse -Force
Copy-Item -Path ./resources/ -Destination ./dist/main/resources/ -Recurse -Force