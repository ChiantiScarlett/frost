import os
import sys
import pip
from contextlib import contextmanager
from subprocess import Popen, STDOUT


def toast_message(message):
    print("[frost] {}".format(str(message)))


class Downloader:
    def __init__(self):
        self.opts = None
        self.args = None
        self.prev_items = None
        self.new_items = None

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

        # Check youtube-dl & mutagen. If not installed, install it using `pip`.
        installed_pkgs = [pkg.key for pkg in pip.get_installed_distributions()]
        required_pkgs = ['youtube-dl', 'mutagen']
        for pkg in required_pkgs:
            if 'youtube-dl' not in installed_pkgs:
                with self.suppress_stdout():
                    pip.main(['install', pkg])

        # Check ffmpeg. If not installed, install it using `apt` command.
        proc = Popen('apt-get install -y ffmpeg',
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
        parser.add_option('-i', '--index', action='store_true', dest='index',
                          help='specify channel ID')
        parser.add_option('-t', '--title', action='store_true', dest='title',
                          help='match ID3 `Title` tag with filenames')
        parser.add_option('-a', '--album', dest='album',
                          help='set single ID3 `Album` tag for the audios')
        parser.add_option('-A', '--artist', dest='artist',
                          help='set single ID3 `Artist` tag for the audios')
        parser.add_option('-c', '--cover', dest='cover',
                          help='set album jacket for the audios')
        parser.add_option('-m', '--message', dest='message',
                          help='write a single comment for the audios')
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
        if self.opts.dir is None:
            self.opts.dir = './'
        else:
            if not (
                os.path.isdir(self.opts.dir) and
                os.path.exists(self.opts.dir)
            ):
                x = input(
                    "[*] Cannot find `{}`. ".format(self.opts.dir) +
                    "Do you want to create a new dir? [Y/n] ")

                # Abort if the user select `no`
                if x.lower() != 'y':
                    toast_message('Abort.')
                    return False

                # Create new directory, handle exception
                try:
                    os.mkdir(self.opts.dir)
                    toast_message(
                        'Created directory [{}]'.format(self.opts.dir))
                except Exception:
                    toast_message("Unable to create directory. Abort.")
                    return False

            if self.opts.dir != '/':
                self.opts.dir += '/'  # so as to merge paths later on
            toast_message('Directory set to [{}]'.format(self.opts.dir))

        # Count total numbers of files before downloading
        self.prev_items = set(os.listdir(self.opts.dir))

        # Set options for download
        ydl_opts = {
            'outtmpl': self.opts.dir + '%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }],
            'ignoreerrors': True,
            'nooverwrites': True,
        }

        # Start download & extract mp3 files.
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.args)

        # Get list of downloaded files
        self.new_items = set(os.listdir(self.opts.dir)) - self.prev_items
        toast_message(
            'Downloaded {} mp3 file(s) in total.'.
            format(len(self.new_items)))
        return True

    def post_adjustments(self):
        from mutagen.mp3 import MP3
        from mutagen.id3 import TIT2, TALB, TPE1, APIC, COMM
        # If the title option

        for filename in self.new_items:
            audio = MP3(self.opts.dir + filename)
            print('-----------------------------------------')
            if self.opts.title:
                audio['TIT2'] = TIT2(encoding=3, text=filename[:-4])
                toast_message(
                    'ID3 SET: `Title` --> {}'.format(filename[:-4]))
            if self.opts.album is not None:
                audio['TALB'] = TALB(encoding=3, text=self.opts.album)
                toast_message(
                    'ID3 SET: `Album` --> {}'.format(self.opts.album))
            if self.opts.artist is not None:
                audio['TPE1'] = TPE1(encoding=3, text=self.opts.artist)
                toast_message(
                    'ID3 SET: `Artist` --> {}'.format(self.opts.artist))
            if self.opts.message is not None:
                audio['COMM'] = COMM(encoding=3, text=self.opts.message)
                toast_message(
                    'ID3 SET: `COMMENT` --> {}'.format(self.opts.message))
            if self.opts.cover is not None:
                try:
                    img = open(self.opts.cover, 'rb').read()
                    audio['APIC'] = APIC(encoding=3, data=img)
                except Exception:
                    toast_message(
                        '[{}] is not a valid JPEG file / URL. Abort.'.
                        format(self.opts.cover))
                    return False

                toast_message(
                    'ID3 SET: `Album Jacket` --> {}'.format(self.opts.cover))

            audio.save(self.opts.dir + filename)

        toast_message('Operation complete.')


def main():
    downloader = Downloader()
    if downloader.check_compatibility() and downloader.check_options():
        response = downloader.download()
        if response:
            downloader.post_adjustments()


if __name__ == "__main__":
    main()
