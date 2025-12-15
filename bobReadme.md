#安装依赖
```bash
pip install -r requirements.txt 
pip install -e .

```
#设备检查
```bash
# 检查已连接的设备
adb devices

# 输出结果应显示你的设备，如pc本地没有启动服务，会自动启动：
#* daemon not running; starting now at tcp:5037
#* daemon started successfully
#List of devices attached
#b8abde5f        device    这是在安卓端被授权成功的手机设备

```
#启动方式 
在ide右下中建立powershell终端进行启动。

##命令行方式
```bash
-python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model "autoglm-phone" --apikey "2b55beee279d437ea8c7460e29bc12b0.X0JeFydsJjZjp4Rf" "打开美团搜索附近的火锅店"
```
##服务方式
参数已经固化到app的参数对象内。
```bash
-python app.py 
```
##网页地址
http://localhost:5001/
http://192.168.1.8:5001/