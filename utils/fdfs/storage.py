from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf


class FDFSStorage(Storage):
    """实现文件上传存储"""

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        """保存文件时使用"""
        # name:你选择的上传文件的名字
        # content:包含你上传文件内容的File对象
        # 创建一个Fdfs_clinet对象

        client = Fdfs_client(get_tracker_conf('./utils/fdfs/client.conf'))

        # 上传文件到fast dfs系统中
        res = client.upload_appender_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast dfs失败')
        # 获取返回的文件ID
        filename = res.get('Remote file_id')
        return filename.decode()

    def exists(self, name):
        """Django判断文件名称"""
        return False

    def url(self, name):
        """返回访问文件的url路径"""
        return name
