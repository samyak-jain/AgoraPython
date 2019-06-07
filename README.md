# Agora-community-sdk

A python library to stream video from agora servers.  
To install -   
```pip install agora-community-sdk```

## Code Example:

```python
from agora_community_sdk import AgoraRTC
client = AgoraRTC("app-id")
client.join_channel("channel-name")

users = client.get_users() # Gets references to everyone participating in the call

user1 = users[0] # Can reference users in a list
print(user1.id) # Can also access users based on uid

binary_image = user1.frame # Gets the latest frame from the stream as a blob
b64_image = user1.b64_frame # Get latest frame in base64 encoded format

with open("test.jpg") as f:
    f.write(binary_image) # Can write to file

client.unwatch() # Stop listening to the channel. Not calling this can cause memory leaks
```

Can also use with statement - 

```python
from agora_community_sdk import AgoraRTC

with AgoraRTC("app-id") as client:
    client.join_channel("channel-name")
    
    users = client.get_users()
    user1 = users[0]
    
    frame = user1.frame
    b64_frame = user1.frame

```