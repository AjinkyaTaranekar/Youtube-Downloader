import urllib.request
import urllib.error

import re
import sys
import time
import os

import pafy

class progressBar:
    def __init__(self, barlength=25):
        self.barlength = barlength
        self.position = 0
        self.longest = 0

    def print_progress(self, cur, total, start):
        currentper = cur / total
        elapsed = int(time.process_time() - start) + 1
        curbar = int(currentper * self.barlength)
        bar = '\r[' + '='.join(['' for _ in range(curbar)])  # Draws Progress
        bar += '>'
        bar += ' '.join(['' for _ in range(int(self.barlength - curbar))]) + '] '  # Pads remaining space
        bar += bytestostr(cur / elapsed) + '/s '  # Calculates Rate
        bar += getHumanTime((total - cur) * (elapsed / cur)) + ' left'  # Calculates Remaining time
        if len(bar) > self.longest:  # Keeps track of space to over write
            self.longest = len(bar)
            bar += ' '.join(['' for _ in range(self.longest - len(bar))])
        sys.stdout.write(bar)

    def print_end(self, *args):  # Clears Progress Bar
        sys.stdout.write('\r{0}\r'.format((' ' for _ in range(self.longest))))


def getHumanTime(sec):
    if sec >= 3600:  # Converts to Hours
        return '{0:d} hour(s)'.format(int(sec / 3600))
    elif sec >= 60:  # Converts to Minutes
        return '{0:d} minute(s)'.format(int(sec / 60))
    else:  # No Conversion
        return '{0:d} second(s)'.format(int(sec))


def bytestostr(bts):
    bts = float(bts)
    if bts >= 1024 ** 4:  # Converts to Terabytes
        terabytes = bts / 1024 ** 4
        size = '%.2fTb' % terabytes
    elif bts >= 1024 ** 3:  # Converts to Gigabytes
        gigabytes = bts / 1024 ** 3
        size = '%.2fGb' % gigabytes
    elif bts >= 1024 ** 2:  # Converts to Megabytes
        megabytes = bts / 1024 ** 2
        size = '%.2fMb' % megabytes
    elif bts >= 1024:  # Converts to Kilobytes
        kilobytes = bts / 1024
        size = '%.2fKb' % kilobytes
    else:  # No Conversion
        size = '%.2fb' % bts
    return size

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
        print("Veronica => ",url, "is not a youtube playlist. <-_->")
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
        print("Veronica => Found", len(final_vid_urls), "videos in playlist. {^$^}")
        printUrls(final_vid_urls)
        return final_vid_urls
    else:
        print('Veronica => No videos found. <-_->')
        exit(1)


# function added to get audio files along with the video files from the playlist

def download_Video_Audio(path, vid_url, quality, file_no):
    try:
        video = pafy.new(vid_url)
    except Exception as e:
        print("Veronica => T_T Error:", str(e), "- Skipping Video with url '" + vid_url + "'.")
        return

    streams = video.streams
    for i in streams:
        print(i)

    fileTitle=video.title

    print("Veronica => ^_^ downloading, ", fileTitle + " video")
    try:
        i = 1
        for vid in streams:
            #print(vid.mediatype=='normal' , vid.extension=='mp4' , str(quality) in vid.quality)
            path=path
            if (vid.mediatype=='normal' and vid.extension=='mp4'):
                if str(quality) in vid.quality:
                    #bar = progressBar()
                    #bar.print_progress(vid.get_filesize(), video.length, 0)
                    #bar.print_end()
                    vid.download(path)
                    break
                else:
                    print("Veronica => ",quality, "not found, downloading the next quality of ", streams[i+1].resolution)
                    #bar = progressBar()
                    #bar.print_progress(streams[i+1].get_filesize(), video.length, 0)
                    #bar.print_end()
                    streams[i+1].download(path)
                    break

        i += 1

        print("Veronica => Successfully downloaded", fileTitle, "!")
    except OSError:
        print("Veronica => Seems like ", fileTitle, "already exists in this directory! So, I am skipping video...")

def printUrls(vid_urls):
    for url in vid_urls:
        print(url)
        time.sleep(0.04)


if __name__ == '__main__':
        print("Welcome to Youtube Video Downloader.")
        print("Hello, I am Veronica \(^_^)/, your Assistant.")
        print("Veronica => What would you like to download?")

        print("Veronica => 1. Video \nVeronica => 2. Playlist")
        print("User => ",end="")
        choice = int(input())
        if choice ==1:
            print("Veronica => Enter video url")
            print("User => ",end="")
            url = input()
            url = url.replace(" ", "")
            # url ="https://www.youtube.com/playlist?list=PLqM7alHXFySH8VivqUPnNFJ0kxgzgHrVb"

            print("Veronica => Enter prefered quality of video")
            print("User => ", end="")
            quality = input()
            # quality=720

            print("Veronica => Enter directory url")
            print("User => ", end="")
            directory = input()

            # make directory if dir specified doesn't exist
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                print(e.reason)
                exit(1)

            if not url.startswith("http"):
                url = 'https://' + url

            download_Video_Audio(directory, url, quality, 1)

        elif choice == 2:
            print("Veronica => Enter playlist url")
            print("User => ", end="")
            url = input()
            url = url.replace(" ", "")
            # url ="https://www.youtube.com/playlist?list=PLqM7alHXFySH8VivqUPnNFJ0kxgzgHrVb"

            print("Veronica => Enter prefered quality of videos")
            print("User => ", end="")
            quality = input()
            # quality=720

            print("Veronica => Enter directory url")
            print("User => ", end="")
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
        else:
            print("Veronica => OOPS, Pls. select from 1 or 2")
