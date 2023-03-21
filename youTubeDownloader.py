from pytube import YouTube
from sys import argv

link = argv[1]
yt = YouTube(link=link)

print("Title: ", yt.title)
print("View: ", yt.view)

yd = yt.streams.get_highest_resolution()

yd.download('./youTubeDownload')