# 📷 MediaPipe를 이용한 손가락 인식 리듬게임  

개발 배경 : 키보드를 사용하는 리듬게임에서 이미지로 간단라게 즐기는 리듬게임을 개발하고싶었음

### 사용 기술 : MediaPipe  
  
-Ondevice MachineLearning 도구  
-Handmarker, Image Classification, Text Recognization...  
-MediaPipe의 Hands의 INDEX_FINGER_TIP(검지 손가락의 끝 부분)  LandMarks를 추출   
-Non \- max Suppersion을 사용, 후보군 정렬 후 높으 확률의 후보 남기고 위치 추출  
-Enconder,Deconder 으로 특징을 추출, Decoder을 사용하여 손 여부, 좌표룰 반환  

### 구현 화면
![image](https://github.com/user-attachments/assets/77da3a9b-ed13-4edf-891b-72cd707fd430)  
파란색 직사각형 구역은 손가락을 기준으로 노트 판정 영역 범위, 검은 선은 판정 구역, 초록색 직사각형은 4개의 범위로 나눈것(4key 와 비슷)  

