## Face Recognition with 3D imaging, OpenCV and Neural Nets (FR3ONN)

### Overview

Face Recognition with 3D imaging, OpenCV and Neural Nets - a face recognition system using OpenCV, Intel(R) Joule(TM), Intel(R) RealSense(TM), 3D prototyping and printing. The system can open doors and storages, can notify when someone comes and so on. And it will be resistant to spoofing. For more information read our [article](<ADD_A_LINK>) (in Russian).

### Requirements

- Intel(R) Joule(TM) Development Kit
- Ubuntu* Desktop 16.04 LTS
- Python* 3.5 or 3.6
- [OpenCV](https://github.com/opencv/opencv) (need to build a Python module)
- [libmraa](https://github.com/intel-iot-devkit/mraa) (need to build a Python module)
- The following packages: ```apt install -y --fix-missing build-essential cmake gfortran git wget curl graphicsmagick libgraphicsmagick1-dev libatlas-dev libavcodec-dev libavformat-dev libboost-all-dev libgtk2.0-dev libjpeg-dev liblapack-dev libswscale-dev pkg-config python3-dev python3-numpy software-properties-common zip```
- [dlib](https://github.com/davisking/dlib.git): ```cd dlib; mkdir build; cd build; cmake .. -DUSE_AVX_INSTRUCTIONS=1; cmake --build . ; cd .. ; python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA```
- [face_recognition](https://github.com/ageitgey/face_recognition): ```pip3 install face_recognition```
- web camera (Intel(R) RealSense(TM) is preferable)

### Run

```python3 launcher.py [--db_dir <db_dir>] [--camera <camera>]```,  
where ```<db_dir>``` is a path to custom database, ```<camera>``` is a camera number (0 by default) or a path to video file.

_Intel, Intel Joule and Intel RealSense are trademarks of Intel Corporation or its subsidiaries in the U.S. and/or other countries._  
_\* Other names and brands may be claimed as the property of others._
