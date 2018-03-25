import os
import sys
import pip
from contextlib import contextmanager
from subprocess import Popen, STDOUT


def toast_message(message):
    print("[*] {}".format(str(message)))


class Downloader:
    def __init__(self):
        self.opts = None
        self.args = None

    @contextmanager
    def suppress_stdout(self):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def check_compatibility(self):
        # Check OS system
        if sys.platform not in ['linux', 'linux2']:
            toast_message('Frost only works on Linux platform.' +
                          'Seems like your OS is something else.')
            return False

        # Check youtube_dl. If not installed, install it using `pip`.
        installed_pkgs = [pkg.key for pkg in pip.get_installed_distributions()]
        if 'youtube-dl' not in installed_pkgs:
            with self.suppress_stdout():
                pip.main(['install', 'youtube-dl'])

        # Check ffmpeg. If not installed, install it using `apt` command.
        proc = Popen('apt-get install -y ffmpeg',
                     shell=True, stdin=None, stdout=open(os.devnull, "wb"),
                     stderr=STDOUT, executable="/bin/bash")
        proc.wait()

        # Check nautilus. If not installed, install it using `apt` command.
        proc = Popen('apt-get install -y nautilus',
                     shell=True, stdin=None, stdout=open(os.devnull, "wb"),
                     stderr=STDOUT, executable="/bin/bash")
        proc.wait()
        return True

    def check_options(self):
        from optparse import OptionParser

        # Set options
        parser = OptionParser()
        parser.add_option('-d', '--dir', dest='dir',
                          help='specify a directory for saving files')
        parser.add_option('-i', '--index', action='store_true', dest='verbose',
                          help='specify channel ID')

        (self.opts, self.args) = parser.parse_args()

        # Check validity
        if len(self.args) == 0:
            toast_message(
                'There should be at least one ID of a video/playlist/channel.')
            return False

        return True

    def download(self):
        import youtube_dl

        # Change directory if specified
        if self.opts.dir is not None:
            try:
                os.chdir(self.opts.dir)
            except Exception:
                x = input(
                    "[*] Cannot find `{}`.".format(self.opts.dir) +
                    "Do you like to create a new one? [Y/n] ")
                if x.lower() != 'y':
                    return False

                try:
                    os.mkdir(self.opts.dir)
                    toast_message(
                        'Created directory `{}`'.format(self.opts.dir))
                    os.chdir(self.opts.dir)
                except Exception:
                    toast_message("Unable to create directory. Abort.")
                    return False

            toast_message('Directory set to {}'.format(self.opts.dir))

        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }],
            'ignoreerrors': True,
            'nooverwrites': True,
            # 'verbose': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.args)

        return True


def main():
    downloader = Downloader()
    if downloader.check_compatibility() and downloader.check_options():
        response = downloader.download()
        if response:
            toast_message('Operation complete.')


if __name__ == "__main__":
    main()
