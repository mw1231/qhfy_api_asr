from txasr import TencentASR
import time

asr = TencentASR('','') #secret things....oh shit
task_id = asr.send_audio("0006.wav")
if task_id:
    print('发送录音文件成功，识别任务ID为：', task_id)
    print('等待识别结果...')
    time.sleep(10)
    result = asr.get_result(task_id)
    if result:
        print('识别结果：')
        for line in result:
            print('->:' + line.strip())
    else:
        print('获取识别结果失败')
else:
    print('发送录音文件失败')
