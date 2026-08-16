class NoThumbnailError(FileNotFoundError):
    """当缩略图不存在时引发的异常。"""
    pass