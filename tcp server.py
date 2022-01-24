#-*- encoding:utf-8 -*-

#若遇到無法開啟相機，可能是卡片有裝motion，相機資源被motion daemon占用
#只要在終端機輸入
#$ sudo /etc/init.d/motion stop
#即可停止motion daemon，
#也就能成功使用相機資源(能使用)

import socket
import cv2
import numpy

(w_camera, h_camera) = (640,480) #照片尺寸 # FIXME: 實測出來，要根據攝像頭尺寸去改!!

#jetbot不支援capture = cv2.VideoCapture(0)  得用gs stream
#可能是因為jetbot的相機是沒有id的
#------------------------------------------------------------------------------------
gst_pipeline = ("nvarguscamerasrc ! "
                "video/x-raw(memory:NVMM), "
                "width=3820, height=2464, "
                "format=(string)NV12, framerate=21/1 ! "
                "nvvidconv flip-method=0 ! "
                "video/x-raw, width=1920, height=1080, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                )
                
capture = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)   

server_IP = "192.168.43.241"
server_PORT = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((server_IP, server_PORT))
s.listen(True)

print("server is waiting for request......................")
conn, addr = s.accept()

#client傳給server的文字訊息---這兩則訊息是用來區分哪個訊息已經傳送了
key_01 = 'len ok!'
key_02 = 'img ok and show ok!!'

#圖片轉JPG的encode，為了壓縮圖片，讓圖片可以傳輸更快
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

flag5 = 0

while 1:
    #print("hi 1")
    
    ret, frame = capture.read() #拍一張照
#    print(frame.shape)
    frame = cv2.resize(frame, (w_camera, h_camera)) #(w,h) 改成 (800,540)
#    frame = cv2.flip(frame, 1)
#    cv2.imshow('MediaPipe Hands', frame)
#    cv2.waitKey(1)

    #--------------------------------------------
    #當呼叫send的時候，資料並不是即時發給客戶端的。
    # 而是放到了系統的socket傳送緩衝區裡，
    # 等緩衝區滿了、或者資料等待超時了，資料才會傳送，
    # 所以有時候傳送太快的話，前一份資料還沒有傳給客戶端，
    # 那麼這份資料和上一份資料一起發給客戶端的時候就會造成“粘包” 。
    #(這也是為什麼接收端接收到的資料是幾份資料混雜起來的)
    #--------------------------------------------

    #傳送檔案
    #---------------------------------------------------------
    # 首先對圖片進行編碼，因爲socket不支持直接發送圖片
    # (這樣才能存進去buffer，SOCKET會用send()將data存入buffer，然後等時限到或是滿了，buffer內的資料才會傳送過去)
    result, img_encode = cv2.imencode('.jpg', frame, encode_param)
#    print(imgencode)

    #圖片做編碼-->才能壓縮，以讓傳輸變快
    data_encode = numpy.array(img_encode)
#    print(data_encode.shape) #(xxxx, 1)，裡面每個值都是0-255
#    print(data_encode) #FIXME:DEBUG用

    #把array變成str
    stringData = data_encode.tostring()

    len_str_data = str(data_encode.shape[0])  #54666

    # 首先發送圖片編碼後的長度
    #int to bytes-like object
    #只有str才有encode()
    #encode為bytes-like object(好像是UTF-8編碼)
    encode_len_str_data = len_str_data.encode("utf-8")
#    print(encode_len_str_data) #FIXME:DEBUG用
    conn.send(encode_len_str_data)  #encode str as UTF-8 bytes. 
    #---------------------------------------------------------


    #先做上一份資料client已經接收完畢的確認
    #等對面的接收端傳訊息給這一端
    #---------------------------------------------------------
    #server接收來自client的data
    clientMessage = str(conn.recv(1024)).encode('utf-8')

    #印出client傳給server的data
#    print('message sent from client:', clientMessage)
    if clientMessage==key_01:
    #--------------------------------------------------------- 

        #確認對面已經接收完畢，即可傳下一份資料
        # 如此是為了避免黏包:
        #   Server傳太快，client收太慢，
        #   讓上一份資料和這份資料同時擠進server端的buffer，
        #   造成後來對面的接收到錯誤的資料。
        #---------------------------------------------------------
        #發送圖片
        conn.send(stringData)  #stringData是'bytes' object，所以不用encode()
        #---------------------------------------------------------


    #server等client展示完圖片，並且client傳訊息過來給Server後才會再次開始傳圖片(才會進下個循環)
    #---------------------------------------------------------
    #server接收來自client的data
    #clientMessage = str(conn.recv(1024), encoding='utf-8')
    clientMessage = str(conn.recv(1024)).encode('utf-8')

    #印出client傳給server的data
#    print('message sent from client:', clientMessage)
    if clientMessage==key_02:
    #---------------------------------------------------------

        cv2.waitKey(1)
#        print("send one package")

conn.close()
cv2.destroyAllWindows()