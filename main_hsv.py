#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tello		# tello.py가져오기
import time			# time.sleep를 사용하고 싶기 떄문에
import cv2			# OpenCV를 사용하기 위해서

# 메인함수
def main():
	# Tello 클래스를 써서 drone이라는 instance(실체)를 만든다.
	drone = tello.Tello('', 8889, command_timeout=.01)  

	current_time = time.time()	# 현재 시각의 저장 변수
	pre_time = current_time		# 5초마다 'command' 전송을 위한 시각 변수

	time.sleep(0.5)		# 통신이 안정될 때까지 잠깐 기다리다

	# 트랙바를 만들기 위하여 가장 먼저 윈도우를 생성한다.
	cv2.namedWindow("OpenCV Window")

	# 트랙바의 콜백 함수는 아무것도 하지 않는 빈 함수
	def nothing(x):
		pass

	# 트랙 바의 생성
	cv2.createTrackbar("H_min", "OpenCV Window", 0, 179, nothing)		# Hue의 최대치는 179
	cv2.createTrackbar("H_max", "OpenCV Window", 128, 179, nothing)
	cv2.createTrackbar("S_min", "OpenCV Window", 128, 255, nothing)
	cv2.createTrackbar("S_max", "OpenCV Window", 255, 255, nothing)
	cv2.createTrackbar("V_min", "OpenCV Window", 128, 255, nothing)
	cv2.createTrackbar("V_max", "OpenCV Window", 255, 255, nothing)

	#Ctrl+c가 눌릴 때까지 루프
	try:
		while True:

			# (A)화상 취득
			frame = drone.read()	# 영상 1프레임 획득
			if frame is None or frame.size == 0:	# 내용이 이상하면 무시
				continue 

			# (B)여기서 화상처리
			image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)		# OpenCV용 컬러와 함께 변환
			bgr_image = cv2.resize(image, dsize=(480,360) )	# 비디오크기를 반으로 변경

			hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)	# BGR화상 -> HSV화상

			# 트랙바의 값을 매기다
			h_min = cv2.getTrackbarPos("H_min", "OpenCV Window")
			h_max = cv2.getTrackbarPos("H_max", "OpenCV Window")
			s_min = cv2.getTrackbarPos("S_min", "OpenCV Window")
			s_max = cv2.getTrackbarPos("S_max", "OpenCV Window")
			v_min = cv2.getTrackbarPos("V_min", "OpenCV Window")
			v_max = cv2.getTrackbarPos("V_max", "OpenCV Window")

			# in Range 함수로 범위 지정 2값화 -> 마스크 이미지로 사용
			mask_image = cv2.inRange(hsv_image, (h_min, s_min, v_min), (h_max, s_max, v_max)) # HSV화상이므로 터플도 HSV

			# bitwise_and로 원 이미지에 마스크를 쓴다 -> 마스크된 부분의 색상만 남는다
			result_image = cv2.bitwise_and(hsv_image, hsv_image, mask=mask_image)

			# (X) 창에 표시
			cv2.imshow('OpenCV Window', result_image)	# 윈도우에 보이는 이미지를 바꾸면 다양하게 표시할 수 있다

			# (Y) OpenCV 창에서 키 입력을 1ms 기다리다
			key = cv2.waitKey(1)
			if key == 27:					# key가 27(ESC)이면 while 루프를 탈출, 프로그램 종료
				break
			elif key == ord('t'):
				drone.takeoff()				# 이륙
			elif key == ord('l'):
				drone.land()				# 착륙
			elif key == ord('w'):
				drone.move_forward(0.3)		# 전진
			elif key == ord('s'):
				drone.move_backward(0.3)	# 후진
			elif key == ord('a'):
				drone.move_left(0.3)		# 좌 이동
			elif key == ord('d'):
				drone.move_right(0.3)		# 우 이동
			elif key == ord('q'):
				drone.rotate_ccw(20)		# 좌 선회
			elif key == ord('e'):
				drone.rotate_cw(20)			# 우 선회
			elif key == ord('r'):
				drone.move_up(0.3)			# 상승
			elif key == ord('f'):
				drone.move_down(0.3)		# 하강

			# (Z)5초 간격으로 'command'를 보내어 이상 검사함
			current_time = time.time()	# 현재시각취득
			if current_time - pre_time > 5.0 :	# 전회 시각으로부터 5초 이상 경과하였는가?
				drone.send_command('command')	# 'command'송신
				pre_time = current_time			# 전회 시각 갱신

	except( KeyboardInterrupt, SystemExit):    # Ctrl+c 누르면 이탈
		print( "SIGINTを検知" )

	# tello클래스 삭제
	del drone


# "python main.py"으로 실행되었을 때만 움직이게 하는 주술적 처리
if __name__ == "__main__":		# import되면 __main__는 들어가지 않으므로 실행인지 import인지를 판단할 수 있다.
	main()    # 메인 함수 실행