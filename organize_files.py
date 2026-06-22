import os
import shutil

def organize_project_files():
    """Organize all project files into appropriate folders"""
    
    # Define the folder structure
    folders_to_create = [
        'audio',
        'sprites', 
        'backgrounds',
        'data',
        'src',  # For Python source files
        'docs'  # For documentation
    ]
    
    # Create folders if they don't exist
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
    
    # Define file mappings (source: destination folder)
    file_mappings = {
        # Audio files
        'arrow.mp3': 'audio',
        'axes.mp3': 'audio', 
        'backgroundMusic.mp3': 'audio',
        'buy.mp3': 'audio',
        'fail.mp3': 'audio',
        'hector.mp3': 'audio',
        'hitting.mp3': 'audio',
        'mouse.mp3': 'audio',
        'shoot.mp3': 'audio',
        'sword.mp3': 'audio',
        'win.mp3': 'audio',
        
        # Background images
        'jungle.jpg': 'backgrounds',
        'forest.png': 'backgrounds', 
        'sea.jpg': 'backgrounds',
        
        # Sprite images
        'player.png': 'sprites',
        'rock.png': 'sprites',
        'arrow.png': 'sprites',
        'axes.png': 'sprites',
        'ske1.png': 'sprites',
        'ske2.png': 'sprites',
        'sword1.png': 'sprites',
        'sword2.png': 'sprites', 
        'sword3.png': 'sprites',
        
        # Enemy/Character sprites (ac, e, s series)
        'ac1.png': 'sprites',
        'ac2.png': 'sprites',
        'ac3.png': 'sprites',
        'ac4.png': 'sprites',
        'ac5.png': 'sprites',
        'ac6.png': 'sprites',
        'ac7.png': 'sprites',
        'ac8.png': 'sprites',
        'ac9.png': 'sprites',
        'ac10.png': 'sprites',
        'e2.png': 'sprites',
        'e3.png': 'sprites',
        'e4.png': 'sprites',
        'e5.png': 'sprites',
        'e6.png': 'sprites',
        'e7.png': 'sprites',
        's1.png': 'sprites',
        's2.png': 'sprites',
        
        # Source code files
        'animation_system.py': 'src',
        'cutscene.py': 'src',
        'dealer.py': 'src',
        'leaderboard.py': 'src',
        'level2.py': 'src',
        'level3.py': 'src',
        
        # Data files
        'leaderboard.json': 'data',
        
        # Documentation
        'CHANGES_SUMMARY.md': 'docs',
    }
    
    # Move files
    moved_files = []
    for filename, dest_folder in file_mappings.items():
        if os.path.exists(filename):
            try:
                dest_path = os.path.join(dest_folder, filename)
                shutil.move(filename, dest_path)
                moved_files.append(f"{filename} -> {dest_folder}/")
                print(f"Moved: {filename} -> {dest_folder}/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"File not found: {filename}")
    
    print(f"\nOrganization complete! Moved {len(moved_files)} files.")
    print("\nNew folder structure:")
    print("├── audio/          # All .mp3 sound files")
    print("├── backgrounds/    # Background images") 
    print("├── sprites/        # Character and object sprites")
    print("├── images/         # Existing organized images")
    print("├── animations/     # Existing animation frames")
    print("├── src/            # Python source code")
    print("├── data/           # Game data files")
    print("├── docs/           # Documentation")
    print("└── Main.py         # Main game file (kept in root)")

if __name__ == "__main__":
    organize_project_files()