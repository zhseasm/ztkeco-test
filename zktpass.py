from flask import Flask, request, jsonify
import logging
import os
import sys
from zk import ZK
from flask_cors import CORS
from datetime import datetime
app = Flask(__name__)
CORS(app)

# 设置密码
PASSWORD = "password"
#进行密码验证
def authenticate(password):
    return password == PASSWORD
#获取设备信息
@app.route("/api/deviceinfo/", methods=["POST"])
def device():
    request_data = request.get_json()
    ip_address = request_data.get("ip")
    password = request_data.get("password")
    
    if authenticate(password):
        return zkt_con(ip_address)
    else:
        return jsonify({"error": "Incorrect password"})
def zkt_con(ip_address):
    # 将以下内容移到函数内部，确保在函数调用时进行
    CWD = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = os.path.dirname(CWD)
    sys.path.append(ROOT_DIR)

    conn = None
    zk = ZK(ip_address, port=4370)
    try:
        conn = zk.connect()
        # 构建设备信息
        device_info = {
            "current_time": conn.get_time(),
            "firmware_version": conn.get_firmware_version(),
            "device_name": conn.get_device_name(),
            "serial_number": conn.get_serialnumber(),
            "mac_address": conn.get_mac(),
            "face_algorithm_version": conn.get_face_version(),
            "finger_algorithm": conn.get_fp_version(),
            "platform_information": conn.get_platform(),
            "network_information": conn.get_network_params()
        }
        return jsonify(device_info)
    except Exception as e:
        # 记录错误并返回错误信息
        logging.error("Process terminated: {}".format(e))
        return jsonify({"error": str(e)})
    finally:
        if conn:
            conn.disconnect()
#设置设备时间为自己想要的
@app.route("/api/devicetime/", methods=["POST"])
def devicetime():
    request_data = request.get_json()
    ip_address = request_data.get("ip")
    password = request_data.get("password")
    new_time=request_data.get("new_time")
    # 调用连接函数并返回结果
    if authenticate(password):
        return zkt_settime(ip_address,new_time)
    else:
        return jsonify({"error": "Incorrect password"})
    
def zkt_settime(ip_address,new_time):
    CWD = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = os.path.dirname(CWD)
    sys.path.append(ROOT_DIR)
    conn = None
    zk = ZK(ip_address, port=4370)
    conn = zk.connect()
    # get current machine's time
    zkt_time = conn.get_time()
    #update new time to machine
    #newtime = datetime.today()
    new_time=datetime.strptime(new_time,"%Y-%m-%d %H:%M:%S")
    conn.set_time(new_time)
    conn.disconnect()
    return jsonify({"旧时间":zkt_time,"新时间":new_time})

#获取当前设备时间
@app.route("/api/gettime/", methods=["POST"])
def gettime():
    request_data = request.get_json()
    ip_address = request_data.get("ip")
    password = request_data.get("password")
    # 调用连接函数并返回结果
    if authenticate(password):
        return zkt_gettime(ip_address)
    else:
        return jsonify({"error": "Incorrect password"})
def zkt_gettime(ip_address):
    CWD = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = os.path.dirname(CWD)
    sys.path.append(ROOT_DIR)
    conn = None
    zk = ZK(ip_address, port=4370)
    conn = zk.connect()
    # get current machine's time
    zkt_time = conn.get_time()
    #update new time to machine
    #new_time = datetime.now()
    #conn.set_time(new_time)
    conn.disconnect()
    return jsonify({"当前卡机时间":zkt_time})

#同步设备时间为当前正常时间
@app.route("/api/uptimenow/", methods=["POST"])
def uptimenow():
    request_data = request.get_json()
    ip_address = request_data.get("ip")
    password = request_data.get("password")
    # 调用连接函数并返回结果
    if authenticate(password):
        return zkt_uptimenow(ip_address)
    else:
        return jsonify({"error": "Incorrect password"})
 
def zkt_uptimenow(ip_address):
    CWD = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = os.path.dirname(CWD)
    sys.path.append(ROOT_DIR)
    conn = None
    zk = ZK(ip_address, port=4370)
    conn = zk.connect()
    # get current machine's time
    zkt_time = conn.get_time()
    #update new time to machine
    new_time = datetime.now()
    conn.set_time(new_time)
    conn.disconnect()
    return jsonify({"旧时间":zkt_time,"新时间":new_time})

# 其他路由函数的定义，都类似于上面的样式
# 请注意在其他路由函数中也需要进行密码验证

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8090)
