import time
import json
import base64
import re
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class TencentASR:
    def __init__(self, secret_id, secret_key):
        """
        初始化腾讯云ASR对象
        :param secret_id: 腾讯云账号的SecretId
        :param secret_key: 腾讯云账号的SecretKey
        # :param region: 地域信息，例如'ap-guangzhou'
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        # self.region = region
        self.cred = credential.Credential(secret_id, secret_key)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        self.httpProfile = HttpProfile()
        self.httpProfile.endpoint = "asr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        self.clientProfile = ClientProfile()
        self.clientProfile.httpProfile = self.httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        self.client = asr_client.AsrClient(self.cred, "", self.clientProfile)
        self.params = {
                    "EngineModelType": "16k_zh_dialect",
                    "ChannelNum": 1,
                    "ResTextFormat": 0,
                    "SourceType": 1,
                    "FilterModal": 1
        }

    def send_audio(self, audio_path):
        """
        发送录音文件进行识别
        :param audio_path: 需要识别的语音文件路径
        :return: 识别任务ID，如果出现错误则返回None
        """
        with open(audio_path, 'rb') as f:
            speech = base64.b64encode(f.read()).decode('utf-8')

        self.params['Data'] = speech
        req = models.CreateRecTaskRequest()
        req.from_json_string(json.dumps(self.params))

        try:
            resp = self.client.CreateRecTask(req)
            task_id = json.loads(resp.to_json_string())['Data']['TaskId']
            return task_id
        except TencentCloudSDKException as err:
            print(err)
            return None

    def get_result(self, task_id, timeout=60):
        """
        获取识别结果
        :param task_id: 识别任务ID
        :param timeout: 超时时间，默认为60秒
        :return: 识别结果，如果出现错误则返回None
        """
        start_time = time.time()
        while True:
            req = models.DescribeTaskStatusRequest()
            params = {
                "TaskId": task_id,
            }
            req.from_json_string(json.dumps(params))

            try:
                resp = self.client.DescribeTaskStatus(req)
                resp_j = json.loads(resp.to_json_string())
                status = resp_j['Data']['Status']
                if status == 2:  # 任务处理成功
                    text_j = resp_j['Data']['Result']
                    pattern = r'\[\d+:\d+\.\d+,\d+:\d+\.\d+\]'
                    result = re.sub(pattern, '', text_j).strip()
                    lines = result.split('\n')
                    return lines
                elif status == 1:  # 任务正在处理中
                    if time.time() - start_time > timeout:
                        print("Timeout")
                        return None
                    time.sleep(1)
                else:  # 任务处理失败
                    print("Task failed")
                    return None
            except TencentCloudSDKException as err:
                print(err)
                return None
