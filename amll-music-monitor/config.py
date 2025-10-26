# config.py
import os

def _find_amll_log():
    """
    软编码：自动发现 AMLL Player 日志文件
    返回第一个存在的路径；若全部不存在，返回 None
    """
    candidates = [
        # 当前用户本地数据目录
        os.path.expanduser(r"~\.amll-player\logs\amll-player.log"),
        # 安装版默认路径（C 盘）
        os.path.expanduser(r"~\AMLL Player\amll-player.log"),
        # 部分系统管理员路径
        r"C:\Users\Administrator\AMLL Player\amll-player.log",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)
    return None


class Config:
    """配置文件：所有参数集中管理"""

    # ① 自动发现日志；发现不到则为 None，运行时会提示用户
    LOG_PATH = _find_amll_log()

    # ② 其他配置
    CHECK_INTERVAL = 1  # 秒
    HISTORY_FILE = "amll_music_history.json"
    PLAYBACK_LOG_FILE = "music_playback.log"
    TARGET_SOFTWARE = "net.stevexmh.amllplayer"

    # ③ 歌词目录（可选）
    LYRICS_DIR = "lyrics"
    SUPPORTED_LYRICS_FORMATS = [".lrc", ".ttml", ".txt"]