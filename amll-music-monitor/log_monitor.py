import re
import time
import os
import threading
from typing import Callable, Optional

class AMLLLogMonitor:
    """AMLL 日志监控器 - 改进版"""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.last_position = 0
        self.is_monitoring = False
        self.callback = None
        self.current_session = None
        self.monitor_thread = None
        
    def start_monitoring(self, callback: Callable):
        """开始监控"""
        self.callback = callback
        
        if not os.path.exists(self.log_path):
            print(f"❌ 错误: 找不到日志文件 {self.log_path}")
            return False
        
        # 初始化文件位置 - 从文件末尾开始监控
        self.last_position = os.path.getsize(self.log_path)
        self.is_monitoring = True
        
        # 在单独线程中运行监控
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"🎵 开始实时监控 AMLL Player 日志...")
        return True
    
    def _monitor_loop(self):
        """实时监控循环"""
        consecutive_errors = 0
        max_errors = 5
        
        while self.is_monitoring:
            try:
                self._check_log_updates()
                consecutive_errors = 0  # 重置错误计数
                time.sleep(0.5)  # 更频繁的检查（0.5秒）
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    print(f"❌ 监控错误过多，停止监控: {e}")
                    break
                print(f"⚠️ 监控错误 ({consecutive_errors}/{max_errors}): {e}")
                time.sleep(2)
    
    def _check_log_updates(self):
        """检查日志更新 - 改进版"""
        if not os.path.exists(self.log_path):
            return
        
        try:
            current_size = os.path.getsize(self.log_path)
            
            # 处理文件被重置的情况（比如程序重启）
            if current_size < self.last_position:
                print("📄 检测到日志文件重置，重新开始监控...")
                self.last_position = 0
            
            # 如果有新内容
            if current_size > self.last_position:
                with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    new_content = f.read()
                    self.last_position = f.tell()
                
                if new_content.strip():
                    self._process_log_content(new_content)
                    
        except PermissionError:
            print("⚠️ 无法访问日志文件，可能被其他进程占用")
            time.sleep(1)
        except Exception as e:
            print(f"❌ 读取日志文件错误: {e}")
            raise
    
    def _process_log_content(self, content: str):
        """处理日志内容 - 改进版"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 1. 首先检测会话切换
            session_to_amll = re.search(r'会话切换:[^"]*"-> "net\.stevexmh\.amllplayer"', line)
            if session_to_amll:
                self.current_session = "amll"
                print("🔊 AMLL Player 变为活动状态")
                continue
            
            session_from_amll = re.search(r'会话切换: "net\.stevexmh\.amllplayer" -> "([^"]+)"', line)
            if session_from_amll:
                other_app = session_from_amll.group(1)
                self.current_session = None
                print(f"🔇 AMLL Player 暂停，切换到: {other_app}")
                continue
            
            # 2. 检测 AMLL Player 的音乐信息（无论会话状态）
            music_match = re.search(r"\[SmtcRunner\] 新曲目信息: '([^']*)' - '([^']*)'", line)
            if music_match:
                artist = music_match.group(1).strip()
                title = music_match.group(2).strip()
                
                # 只在 AMLL Player 会话中处理，或者如果artist/title有效
                if self.current_session == "amll" or (artist and title and artist != "未知歌手" and title != "未知歌曲"):
                    print(f"🎵 检测到音乐信息: '{artist}' - '{title}'")
                    if self.callback:
                        self.callback(artist, title)
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("🛑 AMLL Player 监控已停止")