# Discord Club Bot
A bot for Discord that takes suggestions from users for an "album of the week" or "movie of the week" and posts a poll for users to vote on. 
## Commands
```python
$suggest <album name / song name> by <artist>
```
Suggests an album or song by an artist when posted in the music chat.
The last Monday of every month is singles week, where everyone suggests a song that is added to a playlist.
```python
$suggest <movie name>
```
Suggests a movie when posted in the movie chat.
```python
$list
```
Lists all current suggestions and the users they're associated with depending on which chat it is posted in.
```python
$delete
```
Delete your current suggestion.
