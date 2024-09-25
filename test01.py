from minio import Minio
import os

minio_client = Minio('truenas.lan:9000/',
                     access_key='TQUDCSxXiw5D5hPBbm5J',
                     secret_key='DB63Vk3qU81LQ0szSM7DyrL9rfswJG2qmjJ0BAqU',
                     secure=False)

local_dir = r"C:\Code\ML\Audio\aaa"

# 设置存储桶名称和要上传到存储桶的目标路径前缀
bucket_name = 'label-studio-data'
dest_prefix = 'uploaded-dir'  # 可选,设置为None则直接上传到存储桶根目录

# 遍历本地文件夹,上传所有文件到Minio
for root, dirs, files in os.walk(local_dir):
    for file in files:
        # 构造源文件路径
        file_path = os.path.join(root, file)
        # 保留文件夹结构,构造在Minio存储桶中的对象名称
        object_name = os.path.relpath(file_path, local_dir)
        object_name = object_name.replace('\\', '/')

        if dest_prefix:
            object_name = dest_prefix + '/' + object_name
        try:
            # 上传文件
            minio_client.fput_object(bucket_name, object_name, file_path)
            print(f'Uploaded {file_path} as {object_name}')
        except Exception as e:
            print('error: ', e)