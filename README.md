#### 环境

##### Python 3.9 +

##### CUDA 11.8

下载链接：https://developer.nvidia.com/cuda-11-8-0-download-archive

##### pytorch

```shell
pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
```

##### numpy

```shell
# 需要更换一下版本
pip uninstall numpy
pip install numpy==1.26.4
```

##### 安装opencv

```shell
pip install opencv-python==4.10.0.84
```

##### 安装CLIP

```shell
pip install git+https://github.com/openai/CLIP.git
# 如果网络问题无法安装，用以下方法
git clone https://github.com/openai/CLIP.git
pip install D:/repository/CLIP
```

##### 安装其他依赖

```shell
pip install Pillow
pip install PySide6
pip install pandas
pip install requests
```



#### 配置

##### 全局配置：config.json

| 配置项                | 描述                                                         | 默认值                               |
| --------------------- | ------------------------------------------------------------ | ------------------------------------ |
| font_file             | 测试UI使用，无需修改                                         | resources/微软雅黑.ttf               |
| device                | 无需修改                                                     | cuda                                 |
| model_directory       | CLIP模型所在目录                                             |                                      |
| fps                   | 主循环循环体执行频率，CPU占用过高可以调小一点                | 25                                   |
| notify_url            | 识别到物体时，将通知推送到指定的URL                          | http://localhost:9999/update_display |
| enable_network_notify | 是否启用网络通知，部署需要设置为 true                        | true                                 |
| video_stream          | opencv VideoCapture的第一个参数，部署时需要打开OBS开启虚拟摄像机，这里设置为1，即使用obs的虚拟摄像机 | 1                                    |
| object_configs        | 留空即可，这部分配置转移到了excel                            | []                                   |



###### NOTE

程序有一个主循环，每一次循环都会抓取一帧图像，调用一次CLIP模型计算与所有物品文本的相似度，并将结果保存下来。当某个相似度达到配置的阈值（trigger_prob_threshold）会触发一次**汇总**，汇总就是把前面25帧（summarize_frames）的结果遍历一遍，如果达到相似度>summarize_prob的帧数占比超过frame_proportion，则确认该物体为识别结果。

当时是怕CLIP计算出来的相似度抖动幅度太大，整了这么一出。



##### 物品列表：objectList.xlsx

| 字段                   | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| name                   | 物品名                                                       |
| text                   | 调用CLIP模型使用的文本                                       |
| trigger_prob_threshold | 触发汇总的阈值，和summarize_prob保持一致就行了，识别率低的话，将这个值调低点即可 |
| summarize_frames       | 25即可，如果fps是25，则代表汇总过去一秒内产生的识别结果      |
| summarize_prob         | 与trigger_prob_threshold保持一致即可                         |
| frame_proportion       | 0.8即可                                                      |
| 其他字段               | 程序没有用到，不用管，保留就行。<br />有些文本会冲突，比如apple和手机，识别苹果手机时两者冲突，打算隔离开来计算相似度，不过没有用到。 |



#### 运行

调试运行

```shell
python main.py --test
```

控制台运行

```shell
python main.py
```





