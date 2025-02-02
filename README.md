# config2restore
Using config.json to restore cocos2d's directory

Already test for fighting bellonas

# Requirements
module
```
pip install orjosn
```

# Usage
Restore and decrypt spine files
```
python Cocos2d_restore.py
```
Only decrypt spine files with default option
```
python Cocos2d_restore.py -s
```
If you want to decrypt specific files or folder, you can use option `-n`
```
python Cocos2d_restore.py -n examplefolder
```
