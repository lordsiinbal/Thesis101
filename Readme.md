# DetectCore -- road detection only

A python application that detects, tracks and save illegaly parked vehicles.

## Requirements

Install Pytorch >= 1.7 here: https://pytorch.org/get-started/locally/

If gpu supported, install CUDA here: https://developer.nvidia.com/cuda-toolkit

## Installation guide:

clone this repo

```bash 
git clone -b gui-road https://github.com/lordsiinbal/Thesis101.git
```

Update submodule (deep_sort/deep_sort/deep/reid)

```bash 
git submodule update --init
```

Install dependencies
```bash 
pip install -r requirements.txt
```

## Usage:

### Running the mongodb server
Open cmd or terminal and change directory to 'Server/run', then run this command:
```bash 
python run.py
```
This will run the mongodb server

### Running the application
Open another cmd or terminal and change directory to 'Client/', then run this command:
```bash 
python mainui.py
```

## Repositories that have helped us:
yolov5 - https://github.com/ultralytics/yolov5

yolov5_deepsort_pytorch - https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch

deep-person-reid - https://github.com/KaiyangZhou/deep-person-reid