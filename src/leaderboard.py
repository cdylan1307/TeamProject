import json
import os
from datetime import datetime

class LeaderboardManager:
    def __init__(self, filename="leaderboard.json"):
        self.filename = filename
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        """Load scores from file, create empty list if file doesn't exist"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
            else:
                self.scores = []
        except (json.JSONDecodeError, FileNotFoundError):
            self.scores = []
    
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def add_score(self, player_name, total_time_seconds):
        """Add a new score to the leaderboard"""
        score_entry = {
            "name": player_name,
            "time": total_time_seconds,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.scores.append(score_entry)
        # Sort by time (fastest first)
        self.scores.sort(key=lambda x: x["time"])
        # Keep only top 10 scores
        self.scores = self.scores[:10]
        self.save_scores()
    
    def get_top_3(self):
        """Get top 3 players"""
        return self.scores[:3]
    
    def format_time(self, seconds):
        """Format time as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_leaderboard_text(self):
        """Get formatted leaderboard text for display"""
        top_3 = self.get_top_3()
        if not top_3:
            return ["No records yet!"]
        
        lines = []
        for i, entry in enumerate(top_3):
            rank = i + 1
            name = entry["name"][:12]  # Limit name length
            time_str = self.format_time(entry["time"])
            lines.append(f"{rank}. {name} - {time_str}")
        
        return lines


class GameTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.is_running = False
        self.total_time = 0
        self.paused_time = 0  # Track total paused duration
        self.pause_start = None  # When current pause started
        self.is_paused = False
    
    def start(self):
        """Start the timer"""
        import time
        self.start_time = time.time()
        self.is_running = True
        self.total_time = 0
        self.paused_time = 0
        self.is_paused = False
    
    def pause(self):
        """Pause the timer (for cutscenes)"""
        if self.is_running and not self.is_paused:
            import time
            self.pause_start = time.time()
            self.is_paused = True
    
    def resume(self):
        """Resume the timer after pause"""
        if self.is_running and self.is_paused:
            import time
            if self.pause_start:
                self.paused_time += time.time() - self.pause_start
                self.pause_start = None
            self.is_paused = False
    
    def stop(self):
        """Stop the timer and return total time"""
        if self.is_running and self.start_time:
            import time
            self.end_time = time.time()
            # Account for any current pause
            if self.is_paused and self.pause_start:
                self.paused_time += time.time() - self.pause_start
            
            self.total_time = self.end_time - self.start_time - self.paused_time
            self.is_running = False
            self.is_paused = False
        return self.total_time
    
    def get_current_time(self):
        """Get current elapsed time without stopping"""
        if self.is_running and self.start_time:
            import time
            current_time = time.time()
            if self.is_paused and self.pause_start:
                # Don't count current pause in elapsed time
                return current_time - self.start_time - self.paused_time - (current_time - self.pause_start)
            else:
                return current_time - self.start_time - self.paused_time
        return self.total_time
    
    def format_time(self):
        """Format current time as MM:SS"""
        seconds = self.get_current_time()
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_time(self, seconds=None):
        """Format time as MM:SS"""
        if seconds is None:
            seconds = self.get_current_time()
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"