class NoThumbnailError(FileNotFoundError):
    """当缩略图不存在时引发的异常。"""
    pass
class ImageExistError(Exception):
    """当图片已存在时引发的异常。"""
    pass