# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> multi_xiancheng
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2020/1/8 0008 21:00
@Desc   ：
=================================================='''

from threading import Thread
import threading
import time
def active(max):
    for i in range(max):
        print(threading.current_thread().getName() +" "+ str(i))
th1 = Thread(target=active,args=(5,),daemon=True)
th1.start()
for i in range(10):
    th = Thread(target=active,args=(5,))
    th.start()
    # if i==6:
    #     th.join()
    # time.sleep(0.5)
print("game over")