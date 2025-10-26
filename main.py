#!/usr/bin/env python3
"""
AMLL Player 音乐检测器 - 实时监控版
"""

import os
import sys
import time
from datetime import datetime
from colorama import init, Fore, Back, Style

# 初始化 colorama
init(autoreset=True)

from log_monitor import AMLLLogMonitor
from music_tracker import MusicTracker
from auto_refresh_monitor import AutoRefreshMonitor
from config import Config

# 创建全局实例
music_tracker = MusicTracker(
    history_file=Config.HISTORY_FILE,
    log_file=Config.PLAYBACK_LOG_FILE
)

class AMLLMusicDetector:
    """AMLL 音乐检测器 - 实时版"""
    
    def __init__(self):
        self.monitor = AMLLLogMonitor(Config.LOG_PATH)
        self.auto_refresh = AutoRefreshMonitor(music_tracker)
        self.is_running = False
    
    def on_music_detected(self, artist: str, title: str):
        """音乐检测回调函数"""
        if music_tracker.update_track(artist, title):
            # 新曲目被检测到
            self._display_music_info(artist, title, is_new=True)
    
    def _display_music_info(self, artist: str, title: str, is_new=False):
        """显示音乐信息"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        if is_new:
            print(f"\n{Fore.GREEN}🎵 检测到新曲目! {Style.RESET_ALL}")
        else:
            print(f"\n{Fore.CYAN}🔄 更新显示 {Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}┌{'─' * 50}┐")
        print(f"{Fore.CYAN}│ {Fore.YELLOW}歌曲: {Fore.WHITE}{title:<42} {Fore.CYAN}│")
        print(f"{Fore.CYAN}│ {Fore.YELLOW}艺术家: {Fore.WHITE}{artist:<40} {Fore.CYAN}│")
        print(f"{Fore.CYAN}│ {Fore.YELLOW}时间: {Fore.WHITE}{current_time:<40} {Fore.CYAN}│")
        print(f"{Fore.CYAN}└{'─' * 50}┘{Style.RESET_ALL}")
    
    def display_current_track(self, track_info):
        """显示当前曲目（用于自动刷新）"""
        if track_info:
            artist = track_info.get('artist', '未知艺术家')
            title = track_info.get('title', '未知标题')
            self._display_music_info(artist, title, is_new=False)
        else:
            print(f"{Fore.YELLOW}⏳ 等待检测播放内容... {datetime.now().strftime('%H:%M:%S')}")
    
    def start_monitoring(self):
        """开始监控"""
        if not os.path.exists(Config.LOG_PATH):
            print(f"{Fore.RED}❌ 错误: 找不到日志文件 {Config.LOG_PATH}")
            print(f"{Fore.YELLOW}请确保:")
            print(f"  1. AMLL Player 已安装")
            print(f"  2. 日志文件路径正确")
            print(f"  3. 有足够的文件读取权限")
            return False
        
        print(f"{Fore.GREEN}🚀 启动 AMLL Player 实时音乐检测器")
        print(f"{Fore.CYAN}📁 日志文件: {Config.LOG_PATH}")
        print(f"{Fore.CYAN}⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}📝 播放日志: {Config.PLAYBACK_LOG_FILE}")
        print(f"{Fore.YELLOW}按 Ctrl+C 停止监控...\n")
        
        self.is_running = True
        
        # 启动日志监控
        if not self.monitor.start_monitoring(self.on_music_detected):
            return False
        
        # 启动自动刷新显示
        self.auto_refresh.start_auto_refresh(self.display_current_track)
        
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        self.monitor.stop_monitoring()
        self.auto_refresh.stop_auto_refresh()
        
        # 显示播放历史
        self._display_history()
    
    def _display_history(self):
        """显示播放历史"""
        recent_history = music_tracker.get_recent_history(5)
        if recent_history:
            print(f"\n{Fore.CYAN}📋 最近播放的 5 首曲目:")
            print(f"{Fore.CYAN}┌{'─' * 60}┐")
            for i, track in enumerate(reversed(recent_history)):
                artist = track.get('artist', '未知艺术家')
                title = track.get('title', '未知标题')
                time_str = datetime.fromisoformat(track['timestamp']).strftime('%H:%M')
                print(f"{Fore.CYAN}│ {Fore.WHITE}{len(recent_history)-i:2d}. {title:<30} - {artist:<15} [{time_str}] {Fore.CYAN}│")
            print(f"{Fore.CYAN}└{'─' * 60}┘")
        else:
            print(f"{Fore.YELLOW}📝 暂无播放历史")
    
    def run(self):
        """运行监控"""
        try:
            if self.start_monitoring():
                # 保持程序运行
                while self.is_running:
                    time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 接收到停止信号...")
            self.stop_monitoring()
            print(f"{Fore.GREEN}👋 程序已退出")

def main():
    """主函数"""
    print(f"{Fore.MAGENTA}{Style.BRIGHT}")
    print("    ___    __  __ __   __    ____   __    ___   ____      ")
    print("   /   |  / / / // /  / /   / __ ) / /   /   | / __ \\   ")
    print("  / /| | / / / // /  / /   / __  |/ /   / /| |/ / / /    ")
    print(" / ___ |/ /_/ // /  / /___/ /_/ / /___/ ___ / /_/ /      ")
    print("/_/  |_|\\____//_/  /_____/_____/_____/_/  |_\\____/     ")
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.CYAN}AMLL Player 专用音乐检测器 v2.0 - 实时监控版")
    print(f"{Fore.CYAN}=" * 50)
    
    detector = AMLLMusicDetector()
    detector.run()

if __name__ == "__main__":
    main()