"""
用户认证模块
- SQLite 数据库管理用户账户和用户数据
- 密码使用 werkzeug.security 哈希
- 支持：注册、登录、登出、会话状态查询
"""

import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化用户数据库表"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT     UNIQUE NOT NULL,
            email       TEXT     UNIQUE,
            password    TEXT     NOT NULL,
            nickname    TEXT     DEFAULT '',
            avatar      TEXT     DEFAULT '',
            created_at  TEXT     NOT NULL DEFAULT (datetime('now', 'localtime')),
            last_login  TEXT
        )
    """)

    # 用户收藏
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_favorites (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            spot_id     INTEGER NOT NULL,
            spot_name   TEXT    NOT NULL DEFAULT '',
            spot_data   TEXT    DEFAULT '{}',
            added_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, spot_id)
        )
    """)

    # 用户最近浏览
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_recent_views (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            spot_id     INTEGER NOT NULL,
            spot_name   TEXT    NOT NULL DEFAULT '',
            spot_data   TEXT    DEFAULT '{}',
            viewed_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # 为最近浏览创建索引加速去重查询
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recent_views_user_spot
        ON user_recent_views(user_id, spot_id)
    """)

    # 用户偏好
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER UNIQUE NOT NULL,
            interests   TEXT    DEFAULT '[]',
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 用户打卡记录
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_checkins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            spot_id     INTEGER NOT NULL,
            spot_name   TEXT    NOT NULL DEFAULT '',
            status      TEXT    NOT NULL DEFAULT 'none',
            entries     TEXT    DEFAULT '[]',
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, spot_id)
        )
    """)

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# 用户认证
# ═══════════════════════════════════════════

def register_user(username, password, email="", nickname=""):
    """注册新用户。成功返回 user dict，失败返回 None + 错误信息"""
    if not username or not password:
        return None, "用户名和密码不能为空"
    if len(username) < 2 or len(username) > 20:
        return None, "用户名长度 2~20 个字符"
    if len(password) < 6:
        return None, "密码至少 6 位"

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            return None, "用户名已被注册"

        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, email, password, nickname) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, nickname or username)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "nickname": nickname or username
        }, None
    except Exception as e:
        return None, f"注册失败：{e}"
    finally:
        conn.close()


def authenticate(username, password):
    """验证登录。成功返回 user dict，失败返回 None"""
    if not username or not password:
        return None

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, username)
        ).fetchone()
        if not user:
            return None

        if not check_password_hash(user["password"], password):
            return None

        # 更新最后登录时间
        conn.execute(
            "UPDATE users SET last_login = datetime('now', 'localtime') WHERE id = ?",
            (user["id"],)
        )
        conn.commit()

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"] or "",
            "nickname": user["nickname"] or user["username"],
            "avatar": user["avatar"] or "",
            "created_at": user["created_at"]
        }
    finally:
        conn.close()


def get_user_by_id(user_id):
    """根据 ID 获取用户信息"""
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return None
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"] or "",
            "nickname": user["nickname"] or user["username"],
            "avatar": user["avatar"] or "",
            "created_at": user["created_at"]
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════
# 用户数据 CRUD
# ═══════════════════════════════════════════

# --- 收藏 ---

def get_user_favorites(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT spot_id, spot_name, spot_data, added_at FROM user_favorites "
            "WHERE user_id = ? ORDER BY added_at DESC LIMIT 50",
            (user_id,)
        ).fetchall()
        return [{
            "id": r["spot_id"],
            "name": r["spot_name"],
            "added_at": r["added_at"],
            **json.loads(r["spot_data"])
        } for r in rows]
    finally:
        conn.close()


def set_user_favorite(user_id, spot_id, spot_name="", spot_data=None):
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO user_favorites (user_id, spot_id, spot_name, spot_data, added_at) "
            "VALUES (?, ?, ?, ?, datetime('now', 'localtime'))",
            (user_id, spot_id, spot_name, json.dumps(spot_data or {}, ensure_ascii=False))
        )
        conn.commit()
        return True
    finally:
        conn.close()


def remove_user_favorite(user_id, spot_id):
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM user_favorites WHERE user_id = ? AND spot_id = ?",
            (user_id, spot_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def batch_sync_favorites(user_id, favorites):
    """批量同步收藏数据（登录时合并 LocalStorage）"""
    conn = get_db()
    try:
        for fav in favorites:
            spot_id = fav.get("id")
            if not spot_id:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO user_favorites (user_id, spot_id, spot_name, spot_data, added_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, spot_id, fav.get("name", ""),
                 json.dumps(fav, ensure_ascii=False), fav.get("added_at", datetime.now().isoformat()))
            )
        conn.commit()
    finally:
        conn.close()


# --- 最近浏览 ---

def get_user_recent_views(user_id, limit=20):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT spot_id, spot_name, spot_data, viewed_at FROM user_recent_views "
            "WHERE user_id = ? ORDER BY viewed_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [{
            "id": r["spot_id"],
            "name": r["spot_name"],
            "viewed_at": r["viewed_at"],
            **json.loads(r["spot_data"])
        } for r in rows]
    finally:
        conn.close()


def add_user_recent_view(user_id, spot_id, spot_name="", spot_data=None):
    conn = get_db()
    try:
        # 先删旧记录再插入，保持时间戳最新
        conn.execute(
            "DELETE FROM user_recent_views WHERE user_id = ? AND spot_id = ?",
            (user_id, spot_id)
        )
        conn.execute(
            "INSERT INTO user_recent_views (user_id, spot_id, spot_name, spot_data) "
            "VALUES (?, ?, ?, ?)",
            (user_id, spot_id, spot_name, json.dumps(spot_data or {}, ensure_ascii=False))
        )
        # 只保留最近 20 条
        conn.execute("""
            DELETE FROM user_recent_views WHERE id NOT IN (
                SELECT id FROM user_recent_views WHERE user_id = ?
                ORDER BY viewed_at DESC LIMIT 20
            ) AND user_id = ?
        """, (user_id, user_id))
        conn.commit()
    finally:
        conn.close()


def clear_user_recent_views(user_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM user_recent_views WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


# --- 偏好 ---

def get_user_preferences(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT interests, updated_at FROM user_preferences WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if row:
            return {
                "interests": json.loads(row["interests"]),
                "updated_at": row["updated_at"]
            }
        return {"interests": [], "updated_at": None}
    finally:
        conn.close()


def set_user_preferences(user_id, interests):
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO user_preferences (user_id, interests, updated_at) "
            "VALUES (?, ?, datetime('now', 'localtime'))",
            (user_id, json.dumps(interests, ensure_ascii=False))
        )
        conn.commit()
    finally:
        conn.close()


# --- 打卡 ---

def get_user_checkins(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT spot_id, spot_name, status, entries, updated_at FROM user_checkins "
            "WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        result = {}
        for r in rows:
            result[r["spot_id"]] = {
                "spot_id": r["spot_id"],
                "spot_name": r["spot_name"],
                "status": r["status"],
                "entries": json.loads(r["entries"]),
                "updated_at": r["updated_at"]
            }
        return result
    finally:
        conn.close()


def set_user_checkin(user_id, spot_id, spot_name, status, entries=None):
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO user_checkins "
            "(user_id, spot_id, spot_name, status, entries, updated_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))",
            (user_id, spot_id, spot_name, status,
             json.dumps(entries or [], ensure_ascii=False))
        )
        conn.commit()
    finally:
        conn.close()


def batch_sync_checkins(user_id, checkins):
    """批量同步打卡数据"""
    conn = get_db()
    try:
        for spot_id_str, data in checkins.items():
            spot_id = int(spot_id_str)
            conn.execute(
                "INSERT OR REPLACE INTO user_checkins "
                "(user_id, spot_id, spot_name, status, entries, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, spot_id, data.get("spot_name", ""),
                 data.get("status", "none"),
                 json.dumps(data.get("entries", []), ensure_ascii=False),
                 data.get("updated_at", datetime.now().isoformat()))
            )
        conn.commit()
    finally:
        conn.close()


# ═══════════════════════════════════════════
# 初始化
# ═══════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    print("数据库已初始化！")
