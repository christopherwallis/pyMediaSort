#!/usr/bin/env python

import os
import shutil
import re
import csv
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input directory")
parser.add_argument("-o", "--output", help="Output directory")
parser.add_argument("--loose", action='store_true')
args = parser.parse_args()

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
                        print("Failed to get season")
                file.title = title.strip(" ").lower()
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
                print(file.title)
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
                    print("Recognised: Moving {} to {}".format(file.title, destination))
                    shutil.move(file.source, pathlib.Path(destination, filename))
                    count += 1
                    if dirname != input_path:  # If the file isn't in the base directory, move the directory (and contents) to a trash folder once file is sorted.
                        trash_folder = pathlib.Path(input_path) / 'trash' / file.title
                        shutil.move(pathlib.Path(file.source).parent, trash_folder)
                else:
                    pass
            files.append(file)
    return files, count


def main(input_location, output_location, loose_matches=False):
    print("#########################################################################")
    print("##                           Sort TV                                   ##")
    print("#########################################################################")
    print("##  Sort TV from: {}".format(input_location))
    print("##  Sort TV to:   {}".format(output_location))
    dirs = MakeList(out)
    print(f"##  Directories:  {len(dirs):>4}")
    # shutil.move(names_out, names_out + ".backup")
    # StoreNames(dir, names_out)
    # create_to_download(names_out)
    output = SortFiles(dirs, input_location, loose=loose_matches)
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
    inp = args.input
    out = args.output
    main(inp, out, loose_matches=args.loose)
