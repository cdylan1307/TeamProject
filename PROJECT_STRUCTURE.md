# Project Organization Structure

## 📁 Folder Structure
```
Project Root/
├── 🎵 audio/                  # All audio files (.mp3)
│   ├── arrow.mp3
│   ├── axes.mp3
│   ├── backgroundMusic.mp3
│   ├── buy.mp3
│   ├── fail.mp3
│   ├── hector.mp3
│   ├── hitting.mp3
│   ├── mouse.mp3
│   ├── shoot.mp3
│   ├── sword.mp3
│   └── win.mp3
│
├── 🖼️ sprites/                # Character & object sprites
│   ├── ac1.png - ac10.png     # Character sprites (ac series)
│   ├── e2.png - e7.png        # Enemy sprites (e series)  
│   ├── s1.png, s2.png         # Special sprites (s series)
│   ├── player.png             # Main player sprite
│   ├── rock.png               # Projectile sprite
│   ├── arrow.png              # Arrow sprite
│   ├── axes.png               # Axe weapon sprite
│   ├── ske1.png, ske2.png     # Skeleton sprites
│   └── sword1-3.png           # Sword weapon sprites
│
├── 🌄 backgrounds/            # Background images
│   └── (moved background files here)
│
├── 🎬 animations/             # Animation frame sequences
│   ├── Chiron/
│   └── Player/
│
├── 🖼️ images/                 # Organized game images
│   ├── Bard Idle/
│   ├── hector/
│   └── lv1background.png, lv3background.png
│
├── 📂 src/                    # Python source code
│   ├── animation_system.py    # Animation handling
│   ├── cutscene.py           # Cutscene system
│   ├── dealer.py             # Dealer/shop system
│   ├── leaderboard.py        # Score tracking
│   ├── level2.py             # Level 2 game logic
│   └── level3.py             # Level 3 game logic
│
├── 💾 data/                   # Game data files
│   └── leaderboard.json      # High scores
│
├── 📚 docs/                   # Documentation
│   └── CHANGES_SUMMARY.md    # Change log
│
├── 📱 Main.py                 # Main game entry point
└── 🔧 organize_files.py       # Organization script
```

## ✅ Changes Made

### 1. **File Organization**
- ✅ All audio files (.mp3) moved to `audio/` folder
- ✅ All sprite images moved to `sprites/` folder  
- ✅ All Python modules moved to `src/` folder
- ✅ Game data moved to `data/` folder
- ✅ Documentation moved to `docs/` folder

### 2. **Import Path Updates**
- ✅ Updated `Main.py` imports to use `src.` prefix
- ✅ Updated `level3.py` imports for new structure
- ✅ Fixed all file paths in code to match new organization

### 3. **Asset Path Updates**
- ✅ Audio files: `"sound.mp3"` → `"audio/sound.mp3"`
- ✅ Sprites: `"sprite.png"` → `"sprites/sprite.png"`  
- ✅ Backgrounds: `"bg.jpg"` → `"backgrounds/bg.jpg"`

## 🚀 Benefits

1. **Clean Organization**: Files grouped by type and purpose
2. **Easy Maintenance**: Clear separation of assets, code, and data
3. **Scalability**: Easy to add new assets in appropriate folders
4. **Professional Structure**: Standard game development folder layout
5. **Better Collaboration**: Team members can easily find files

## 📝 Usage Notes

- Keep `Main.py` in root as the main entry point
- Add new audio files to `audio/` folder
- Add new sprites to `sprites/` folder
- Add new Python modules to `src/` folder
- The organization script can be rerun if needed

Your project is now beautifully organized and much easier to maintain! 🎉