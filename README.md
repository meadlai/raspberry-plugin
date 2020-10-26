# raspberry-plugin

This is a Rest Plugin, which contains a HTTP Server starting inside of a new Thread.
It accepts the HTTP PUT method, and speaks the 'Text' if the request has data along with it, or it does the recording and return the 'Text' response to rest client.

## Rest API

  - Speak
  
      http://raspberrypi:9090/speak?帅哥你是这条街最靓的仔
      
      return result: {"code": 0, "message": "success"}
      
  - Listen
  
      http://raspberrypi:9090/listen?7
      
      return result: {"code": 0, "message": "测试语音识别的准确度后面的单位是秒"}
      
      the digital number followed in the end is the time of recording second.
      
  
  
