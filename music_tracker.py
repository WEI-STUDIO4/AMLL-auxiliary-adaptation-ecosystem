import json
import os
from datetime import datetime
from collections import Counter
from typing import Dict, Optional, List

class MusicTracker:
    def __init__(self, history_file: str = "amll_music_history.json",
                 log_file: str = "music_playback.log"):
        self.history_file = history_file
        self.log_file = log_file
        self.current_track = None
        self.history = self._load_history()
        self.last_logged_track = None

        # 持久化计数器
        self._count_file = "play_count.json"
        self._play_counter = self._load_counts()

    # -------------- 持久化相关 --------------
    def _load_counts(self) -> Counter:
        if os.path.exists(self._count_file):
            try:
                with open(self._count_file, "r", encoding="utf-8") as f:
                    return Counter(json.load(f))
            except Exception as e:
                print(f"读取计数文件失败: {e}")
        return Counter()

    def _save_counts(self):
        try:
            with open(self._count_file, "w", encoding="utf-8") as f:
                json.dump(dict(self._play_counter), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存计数文件失败: {e}")

    # -------------- 原有功能 --------------
    def _load_history(self) -> List[Dict]:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
        return []

    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    # -------------- 日志写入（含作者） --------------
    def _save_to_playback_log(self, artist: str, title: str, play_count: int):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # ★★★ 把作者加进来 ★★★
            log_entry = f"[{timestamp}] {artist} - {title} (第 {play_count} 次)\n"
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"📝 已记录到播放日志: {artist} - {title} (第 {play_count} 次)")
        except Exception as e:
            print(f"保存播放日志失败: {e}")

    # -------------- 核心更新 --------------
    def update_track(self, artist: str, title: str):
        if artist == "未知歌手" and title == "未知歌曲":
            return 0
        if not artist and not title:
            return 0

        track_key = f"{artist}|{title}"

        if (self.current_track and
            self.current_track.get("artist") == artist and
            self.current_track.get("title") == title):
            return 0

        if (self.last_logged_track and
            self.last_logged_track.get("key") == track_key):
            return 0

        self._play_counter[track_key] += 1
        play_count = self._play_counter[track_key]

        self.current_track = {
            "artist": artist,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "software": "AMLL Player",
            "key": track_key,
        }

        self.history.append(self.current_track.copy())
        self._save_history()
        self._save_to_playback_log(artist, title, play_count)
        self._save_counts()
        self.last_logged_track = self.current_track.copy()

        return play_count

    # -------------- 查询接口 --------------
    def get_current_track(self) -> Optional[Dict]:
        return self.current_track

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]

    def format_track_info(self, track_info: Dict) -> str:
        if not track_info:
            return "🎵 未检测到播放内容"
        artist = track_info.get("artist", "未知艺术家")
        title = track_info.get("title", "未知标题")
        return f"🎵 {title}\n🎤 {artist}\n⏰ {datetime.now().strftime('%H:%M:%S')}"