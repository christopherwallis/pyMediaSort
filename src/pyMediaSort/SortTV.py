#!/usr/bin/env python

import os
import shutil
import re
import csv
import argparse
import pathlib
# import subprocess
import sys
import time
try:
    from rich import pretty, print
    from rich.panel import Panel
    from rich.padding import Padding
    pretty.install()
    ENRICHED = True
except ImportError as e:
    ENRICHED = False
    print(e)


extension_list = {
    r"avi",
    r'mkv',
    r'mp4'
}

regex_list = [
    '[Ss][1234567890][1234567890][Ee][1234567890][1234567890]',
    '[[({]?[Ss]?[0123]?[1234567890][EeXx][1234567890][1234567890]',
]

regex_loose = [
    '20[2][1234567890]',
    '[Ss][1234567890][1234567890][Ee][1234567890][1234567890]',
    '[[({]?[Ss]?[0123]?[1234567890][EeXx][1234567890][1234567890]',
    '[Ss]eason'
    '[0-9][0-9][0-9]'
]

regex_remove = '-'


class MediaFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.directory = None
        self.season = None
        self.title = None
        self.source = None


def get_title(file, delim, loose_regex=False):
    """
    Determines title of TV show based on standard file name variations
    :param file: pathlib.Path object of the file
    :param delim: Delimiter used to separate words in title. Usually '.'
    :param loose_regex: If true a wider selection of regex matches are used to determine if the file matches. Can accidentally include movies and other files but useful for capturing daily TV shows.
    :return: Str: title of the show
    """
    if loose_regex:
        regex_list_local = regex_loose
    else:
        regex_list_local = regex_list
    splitted = file.filename.split(delim)
    print(splitted)
    title = ""

    for word in splitted:
        for regex_rem in regex_remove:
            reg = re.compile(regex_rem)
            if re.match(reg, word):
                splitted.remove(word)
    for word in splitted:
        for code in regex_list_local:
            regex = re.compile(code)
            if re.match(regex, word):
                try:
                    word = word.lower()
                    stripped = word.strip('s').split('e')
                    file.season = int(stripped[0])
                except Exception:
                    try:
                        stripped = word.strip('[').strip(']').split('x')
                        file.season = int(stripped[0])
                    except Exception:
                        if ENRICHED:
                            print("[red]Failed to get season")
                        else:
                            print("Failed to get season")
                file.title = title.strip(" ").lower()
                if ENRICHED:
                    print("Title: [magenta]{}".format(file.title))
                else:
                    print("Title: {}".format(file.title))
                return file.title
            elif word in extension_list:
                return False
        title = title + " "
        title = title + word
    file.title = title.strip(" ").lower()
    return file.title


def SortFiles(dir_lookup, input_path, other=False, loose=False):
    """
    Works through files in directory and sorts matching files into the Plex TV directory structure: Base/Show/Season/episode_file
    :param dir_lookup: Dictionary of the recognised shows and their corresponding path
    :param input_path: Directory to sort
    :param other: Option to move other video to a chosen directory if they are not recognised as one of the TV Shows. Currently inactive.
    :param loose: Option to use broader range of Regex filters when determining show title. Helps pick up daily shows.
    :return: files: list of transferred files. count: number of transferred files.
    """
    files = []
    count = 0
    for dirname, dirnames, filenames in os.walk(input_path):
        for filename in filenames:
            file = MediaFile(filename)
            if filename.split('.')[-1] in extension_list:
                file.source = pathlib.Path(dirname, filename)
                file.title = get_title(file, '.', loose_regex=loose)  # Get the title from the filename
                if file.title is False:
                    file.title = get_title(file, ' ')
                # print(file.title)
                if filename is None:
                    # print("Pass")
                    pass
                elif file.title == "" and other:
                    # print("No title  : Moving {} to {}".format(file.filename, path_other))
                    # shutil.move(file.source, fullpath(path_other, filename))
                    pass
                elif file.title in dir_lookup:  # If show is in list:
                    destination = dir_lookup[file.title]
                    destination = destination + "Season {}/".format(file.season)
                    if not os.path.isdir(destination):  # Create new season directory if required
                        print("Directory does not exist: Creating")
                        os.mkdir(destination)
                    if ENRICHED:
                        print("[red]Recognised:[white] Moving {} to {}".format(file.title, destination))
                    else:
                        print("Recognised: Moving {} to {}".format(file.title, destination))

                    shutil.move(file.source, pathlib.Path(destination, filename))
                    count += 1
                    # Caused issues on some file systems and for multiple media files per folder: Removed until fix can be implemented
                    # if dirname != input_path:  # If the file isn't in the base directory, move the directory (and contents) to a trash folder once file is sorted.
                    #     trash_folder = pathlib.Path(input_path) / 'trash' / file.title
                    #     shutil.move(pathlib.Path(file.source).parent, trash_folder)
                else:
                    pass
            files.append(file)
    return files, count


def main(input_dir=None, output_dir=None, loose_regex=None, sys_args=None):
    """ Entry point access """

    if sys_args:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input", help="Input directory")
        parser.add_argument("-o", "--output", help="Output directory")
        parser.add_argument("--loose", action='store_true')
        args = parser.parse_args(sys_args)

    # Get commandline args if no inputs selected:
    if not input_dir:
        input_dir = args.input
    if not output_dir:
        output_dir = args.output
    if not loose_regex:
        loose_regex = args.loose

    # Check outputs exist and return readable error if not.
    if not input_dir or not output_dir:
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        raise IOError("Input directory and Target/output directory required.")
    lockfile = pathlib.Path(input_dir, 'lock.txt')
    if lockfile.is_file():
        print("Directory locked, waiting...")
        time.sleep(5)
        if lockfile.is_file():
            print("Directory locked, skipping")
            return 99
    print("No lock on directory")
    _main(input_dir, output_dir, loose_matches=loose_regex)


def _main(input_location, output_location, loose_matches=False):
    input_location = pathlib.Path(input_location)
    output_location = pathlib.Path(output_location)
    if ENRICHED:
        t = Panel(f"\t[white]Sort From:[bright white]\t\t{input_location}\n"
                  f"\t[white]Sort To:  [bright white]\t\t{output_location}")
        t.title = "[blue]Sort TV"
        t.border_style = "bold blue"
        t.title_align = "center"
        print(t)
    else:
        print("#########################################################################")
        print("##                           Sort TV                                   ##")
        print("#########################################################################")
        print("##  Sort TV from: {}".format(input_location))
        print("##  Sort TV to:   {}".format(output_location))
    dirs = MakeList(output_location)
    if len(dirs) == 0:
        raise IOError("No output folders detected")

    output = SortFiles(dirs, input_location, loose=loose_matches)

    if ENRICHED:
        t = Panel(f"\t [white]Directories: [light-grey]\t\t{len(dirs):>4}\n"
                  f"\t [white]Files Found: [grey]\t\t{len(output[0]):>4}\n"
                  f"[bold white]\t Files Sorted:\t\t[red]{output[1]:>4}")
        t.title = "[blue]Sort Complete"
        t.border_style = "bold blue"
        t.title_align = "center"
        print(t)

        t = Padding("", (0, 0), style="on green", expand=True)
        print(t)
    else:
        print(f"##  Directories:  {len(dirs):>4}")
        print(f"##  Files found:  {len(output[0]):>4}")
        print(f"##  Files sorted: {output[1]:>4}")
        print("#########################################################################")


def StoreNames(directory, location):
    """
    Stores output directory information in a CSV. Useful when creating/moving directory.
    """
    w = csv.writer(open(location, "w"))
    for key, add in directory.items():
        w.writerow([key])


def MakeList(path):
    """
    Creates dictionary describing the folder structure in the Plex TV repo
    :param path: Base location of the directory structure
    :return: dict: filename=path
    """
    dir_lookup = {}
    for dirname, dirnames, filenames in os.walk(path):
        splitted = dirname.split('/')
        lowerc = splitted[-1].lower()
        dir_full = dirname + "/"
        if "season" not in lowerc:
            dir_lookup.update({lowerc: dir_full})
    return dir_lookup


if __name__ == "__main__":
    main(sys_args=sys.argv[1:])
