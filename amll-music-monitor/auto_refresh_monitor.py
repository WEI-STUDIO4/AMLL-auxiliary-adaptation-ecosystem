import time
import threading
from datetime import datetime

class AutoRefreshMonitor:
    """自动刷新监控器"""
    
    def __init__(self, music_tracker):
        self.music_tracker = music_tracker
        self.is_running = False
        self.refresh_thread = None
        self.last_display = None
    
    def start_auto_refresh(self, display_callback):
        """开始自动刷新显示"""
        self.is_running = True
        self.display_callback = display_callback
        
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
        
        print("🔄 启用自动刷新显示...")
    
    def _refresh_loop(self):
        """自动刷新循环"""
        while self.is_running:
            try:
                current_track = self.music_tracker.get_current_track()
                
                # 如果当前有曲目在播放，定期更新显示时间
                if current_track:
                    self.display_callback(current_track)
                
                time.sleep(5)  # 每5秒刷新一次显示
                
            except Exception as e:
                print(f"刷新显示错误: {e}")
                time.sleep(10)
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.is_running = False
        print("⏹️ 停止自动刷新")