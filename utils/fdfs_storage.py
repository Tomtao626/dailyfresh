from fdfs_client.client import Fdfs_client, get_tracker_conf


def fastDFSStorage(name, content):
    """自定义上传文件"""
    tracker_path = get_tracker_conf('./utils/fdfs/client.conf')
    client = Fdfs_client(tracker_path)
    res = client.upload_appender_by_buffer(content.read())
    if res.get('Status') != 'Upload successed.':
        # 上传失败
        raise Exception('上传文件到fast dfs失败')
    # 获取返回的文件ID
    filename = res.get('Remote file_id')
    return filename.decode()
