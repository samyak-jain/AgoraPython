# Agora-community-sdk

**IMPORTANT: This repository is deprecated. Please use this repository instead: https://github.com/AgoraIO-Community/Agora-Python-SDK**


<br />

A python library to stream video from agora servers.  
To install -   
```pip install agora-community-sdk```

You will also need to download the chromium driver from http://chromedriver.chromium.org

## Code Example:

```python
from agora_community_sdk import AgoraRTC
client = AgoraRTC.create_watcher("app-id", "path to chromium driver")
client.join_channel("channel-name")

users = client.get_users() # Gets references to everyone participating in the call

user1 = users[0] # Can reference users in a list

binary_image = user1.frame # Gets the latest frame from the stream as a PIL image

with open("test.jpg") as f:
    f.write(binary_image) # Can write to file

client.unwatch() # Stop listening to the channel. Not calling this can cause memory leaks
```

## AI Example

A working application can be cloned from https://github.com/samyak-jain/ssd.pytorch  
Download the weights from the readme   
Run demo/demo.ipynb
