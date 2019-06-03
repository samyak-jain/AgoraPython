# TODO

## Top Level Methods

- appid -> client
- client, channelName -> watcher

## watcher methods

- getUsers() -> List[User]

## User method

- getID() -> str
- getFrame() -> ImgLike


## Example Code:

```python
client = Agora(appid)
watcher = client.watch(channel)

with watcher.getUsers() as users:
	for user in users:
		id = user.getID()
		if id == given_id:
			frame = user.getFrame()
			inferenced_image = inference(frame)
			view(inferenced_image)
```
