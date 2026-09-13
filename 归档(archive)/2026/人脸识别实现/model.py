# 自动下载模型（如果文件不存在）
import urllib.request

model_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
weights_url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"

urllib.request.urlretrieve(model_url, "deploy.prototxt")
urllib.request.urlretrieve(weights_url, "res10_300x300_ssd_iter_140000.caffemodel")