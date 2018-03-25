# Project Faust
# Code Reference:
#   https://stackoverflow.com/questions/44210656/
#   https://stackoverflow.com/questions/8481943/


import os
import sys
import pip
from contextlib import contextmanager
from subprocess import Popen, STDOUT


class MessageToast:
    def __init__(self, message):
        return "[*] {}".format(str(message))


class Compatible:
    @contextmanager
    def suppress_stdout(self):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def __init__(self):
        # Check OS system
        if sys.platform not in ['linux', 'linux2']:
            MessageToast('Frost only works on Linux platform.' +
                         'Seems like your OS is something else.')
            return False

        # Check youtube_dl. If not installed, install it using `pip`.
        installed_pkgs = [pkg.key for pkg in pip.get_installed_distributions()]
        if 'youtube_dl' not in installed_pkgs:
            with self.suppress_stdout():
                pip.main(['install', 'youtube_dl'])

        # Check ffmpeg. If not installed, install it using `apt` command.
        proc = Popen('apt-get install -y ffmpeg',
                     shell=True, stdin=None, stdout=open(os.devnull, "wb"),
                     stderr=STDOUT, executable="/bin/bash")
        proc.wait()
        return True


class Download:
    def __init__(self, item):
        import youtube_dl

        # Convert item into string
        if type(item) == str:
            item = [item]

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
                'prefer_ffmpeg': True
            }],
            'ignoreerrors': True,
            'nooverwrites': True,
            'verbose': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(item)


class AnalyzeOptions:
    def __init__(self):
        pass

    def is_valid(self):
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('-u', '--url', dest='url',
                          help='URL of a video')
        parser.add_option('-c', '--channel', dest='channel',
                          help='Channel ID')
        parser.add_option('-p', '--playlist', dest='playlist',
                          help='Playlist ID or video URL with a playlist')
        (options, args) = parser.parse_args()

        print(options)
        print(args)
        return True


def main():
    # Check if the platform is compatible and necessary modules are set.
    # sys.exit(0) if not Compatible() else None

    # Read options and settings
    sys.exit(0) if not AnalyzeOptions().is_valid() else None


if __name__ == "__main__":
    main()
