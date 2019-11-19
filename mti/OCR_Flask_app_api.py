import requests
api = "http://localhost:5000/api/ocr"
files = {'image': open('../ocr_using_video/test.png', 'rb')}

params = {"preprocess" : "blur"}
print(requests.post(api,params,files=files ).text)