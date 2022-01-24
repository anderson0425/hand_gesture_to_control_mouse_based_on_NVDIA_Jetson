# hand_gesture_to_control_mouse_based_on_NVDIA_Jetson

Steps
----
- **Opencv** to take pictures
- **TCP/IP socket** to transfer **Image data** as file-type in the **internal Network** from Jetbot to windows Laptop (from server to client)
  - use **socket** in order to transfer image **quickly to meet immediacy**
- Google **mediapipe hand detection**
  - use mediapipe to **avoid the mis-detect** of the gesture by position and angles of the 21 nodes per hand
- **Pyautogui** module to **control mouse** according to the detection result.
  - use Pyautogui module to do the behavior such as **mouse click, mouse double-click, mouse move, mouse drag, screen shot**.

server & client
----
- execute `tcp client.py` on Windows laptop (client)
- execute `tcp server.py` on Jetbot (server)
- Jetbot will keep transfering image to the laptop in the time of connection.
