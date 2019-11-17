import urllib.request
import urllib.error

import re
import sys
import time
import os

from pytube import YouTube


def getPageHtml(url):
    try:
        yTUBE = urllib.request.urlopen(url).read()
        return str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
        exit(1)


def getPlaylistUrlID(url):
    if 'list=' in url:
        eq_idx = url.index('=') + 1
        pl_id = url[eq_idx:]
        if '&' in url:
            amp = url.index('&')
            pl_id = url[eq_idx:amp]
        return pl_id
    else:
        print(url, "is not a youtube playlist.")
        exit(1)


def getFinalVideoUrl(vid_urls):
    final_urls = []
    for vid_url in vid_urls:
        url_amp = len(vid_url)
        if '&' in vid_url:
            url_amp = vid_url.index('&')
        final_urls.append('http://www.youtube.com/' + vid_url[:url_amp])
    return final_urls


def getPlaylistVideoUrls(page_content, url):
    playlist_id = getPlaylistUrlID(url)

    vid_url_pat = re.compile(r'watch\?v=\S+?list=' + playlist_id)
    vid_url_matches = list(set(re.findall(vid_url_pat, page_content)))

    if vid_url_matches:
        final_vid_urls = getFinalVideoUrl(vid_url_matches)
        print("Found", len(final_vid_urls), "videos in playlist.")
        printUrls(final_vid_urls)
        return final_vid_urls
    else:
        print('No videos found.')
        exit(1)


# function added to get audio files along with the video files from the playlist

def download_Video_Audio(path, vid_url, quality, file_no):
    try:
        yt = YouTube(vid_url)
    except Exception as e:
        print("Error:", str(e), "- Skipping Video with url '" + vid_url + "'.")
        return

    try:  # Tries to find the video in 720p
        video = yt.get('mp4', quality+'p')
    except Exception:  # Sorts videos by resolution and picks the highest quality video if a 720p video doesn't exist
        video = sorted(yt.filter("mp4"), key=lambda video: int(video.resolution[:-1]), reverse=True)[0]

    print("downloading", yt.filename + " Video and Audio...")
    try:
        bar = progressBar()
        video.download(path, on_progress=bar.print_progress, on_finish=bar.print_end)
        print("successfully downloaded", yt.filename, "!")
    except OSError:
        print(yt.filename, "already exists in this directory! Skipping video...")

    try:
        os.rename(yt.filename + '.mp4', str(file_no) + '.mp4')
        aud = 'ffmpeg -i ' + str(file_no) + '.mp4' + ' ' + str(file_no) + '.wav'
        final_audio = 'lame ' + str(file_no) + '.wav' + ' ' + str(file_no) + '.mp3'
        os.system(aud)
        os.system(final_audio)
        os.remove(str(file_no) + '.wav')
        print("sucessfully converted", yt.filename, "into audio!")
    except OSError:
        print(yt.filename, "There is some problem with the file names...")


def printUrls(vid_urls):
    for url in vid_urls:
        print(url)
        time.sleep(0.04)


if __name__ == '__main__':
        print("Welcome to Yotube Playlist Downloader.")
        print("Enter playlist url")
        url = input()
        url.replace(" ", "")

        print("Enter prefered quality of videos")
        quality = input()

        print("Enter directory url")
        directory = input()

        # make directory if dir specified doesn't exist
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(e.reason)
            exit(1)

        if not url.startswith("http"):
            url = 'https://' + url

        playlist_page_content = getPageHtml(url)
        vid_urls_in_playlist = getPlaylistVideoUrls(playlist_page_content, url)

        # downloads videos and audios
        for i, vid_url in enumerate(vid_urls_in_playlist):
            download_Video_Audio(directory, vid_url, quality, i)
            time.sleep(1)