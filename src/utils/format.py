from datetime import datetime

def format_size(size: int | None) -> str:
    if not size:
        return ""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"

def format_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M")

def format_dimension(width: int | None, height: int | None) -> str:
    if not width or not height:
        return ""
    return f"{width} x {height}"