from agora import AgoraRTC
from time import sleep
client = AgoraRTC.create_watcher('6a6faf60981942e98d234a18a4f5313d','channel-x')


def sync_main():
    x = client.get_users()
    print(x)
    user1 = x[0]
    print(user1.id)

    with open("synctest.jpg", "wb") as f:
        f.write(user1.frame)

    client.unwatch()


sync_main()
