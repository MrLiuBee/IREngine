from aip import AipNlp

APP_ID = '10637556'
API_KEY = 'rm0HA7EqfQ16HdOZMqwHkho5'
SECRET_KEY = '3rM91Nj9Z3aLarTgMqvbexdwl0fN3vNd'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
text="我们这byd电动🚕报价20+，zf补10+"
text = ''.join(e for e in text if e.isalnum())
resp = client.sentimentClassify(text)
sentiment = resp['items'][0]['sentiment']
print(resp)
# pprint(resp)
print("分析的文本为：",text)
print("情感分析结果为：",end='')
if sentiment == 0:
    print(sentiment,"负向")
elif sentiment ==1:
    print(sentiment,"中性")
else:
    print(sentiment,"正向")





# if len(one) > 1:
# 						fee = feel_analyse(one[1])
# 						if fee == 0:
# 							one.append("负向")
# 						elif fee == 1:
# 							one.append("中性")
# 						else:
# 							one.append("正向")
# 					else:
# 						continue
