#!/usr/bin/env python

import os
import shutil
import re
import csv
import SortMovies
from pyMediaSort.setup import Directory
# from GetMagnetRSS import create_to_download


class MediaFile(object):
    """
    Object associated with a media file
    """
    def __init__(self, filename):
        self.filename = filename
        self.directory = None
        self.season = None
        self.title = None
        self.source = None


class Sorter:
    """
    Creates sorting object for a particular folder and media type
    """
    def __init__(self, config):
        self.config = config
        self.tv_directories = []

    @classmethod
    def tv(cls, initial=None, final=None):
        call = []
        if initial:
            call.append(''.join(["path_initial=", initial]))
        if final:
            call.append(''.join(["path_final=", final]))
        print("Setup Call: {}".format(call))
        config = Directory.tv_shows(call)
        return cls(config)

    @classmethod
    def movies(cls, initial=None, final=None):
        call = []
        if initial:
            call.append(''.join(["path_initial=", initial]))
        if final:
            call.append(''.join(["path_final=", final]))
        print("Setup Call: {}".format(call))
        config = Directory.movies(call)
        return cls(config)

    # Should be tested but also working
    def get_title(self, file, delim):
        if self.config.tv:
            splitted = file.filename.split(delim)
            # print(splitted)
            title = ""

            for word in splitted:
                for regex_rem in self.config.regex_remove:
                    reg = re.compile(regex_rem)
                    if re.match(reg, word):
                        splitted.remove(word)
            for word in splitted:
                for code in self.config.regex_list:
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
                                # print("Failed to get season")
                                pass
                        file.title = title.strip(" ").lower()
                        # print("Title: {}".format(file.title))
                        return file.title
                    elif word in self.config.extension_list:
                        return False
                title = title + " "
                title = title + word
            file.title = title.strip(" ").lower()
            return file.title
        if self.config.movie:
            split_directory = []
            splitted = self.directory.split(delim)
            for word in splitted:
                split_word = word.split('.')
                for word2 in split_word:
                    split_directory.append(word2)
            if self.config.verbose:
                print(split_directory)
            title = ""

            for word in split_directory:
                for code in self.config.regex_list:
                    regex = re.compile(code)
                    if re.match(regex, word):
                        if self.config.verbose:
                            print("Move: {}".format(title))
                        self.title = title.strip(" ")
                        return True
                title = title + " "
                title = title + word
            if self.config.verbose:
                print("Skip: {}".format(title))
            self.title = title.strip(" ")
            return False

    def sort_files(self):
        if self.config.tv:
            global moved
            files = []
            for dirname, dirnames, filenames in os.walk(self.config.path_initial):
                # print(filenames)
                for filename in filenames:
                    file = MediaFile(filename)
                    # print(filename.split('.')[-1])
                    if filename.split('.')[-1] in self.config.extension_list:
                        file.source = self.config.fullpath(dirname, filename)
                        # print(source)
                        file.title = self.config.get_title(file, '.')
                        # print(filename)
                        if file.title is False:
                            file.title = self.config.get_title(file, ' ')
                        # print(file.title)
                        if filename is None:
                            # print("Pass")
                            pass
                        # elif file.title is "":
                        #     print("No title  : Moving {} to {}".format(file.filename, path_other))
                        #     shutil.move(file.source, self.config.fullpath(path_other, filename))
                        elif file.title in self.config.dir_lookup:
                            destination = self.config.dir_lookup[file.title]
                            destination = destination + "Season {}\\".format(file.season)
                            if not os.path.isdir(destination):
                                # print("Directory does not exist: Creating")
                                os.mkdir(destination)
                            print("Recognised: Moving {} to {}".format(file.title, destination))
                            shutil.move(file.source, self.config.fullpath(destination, filename))
                            moved += 1
                        else:
                            # print("Default   : Moving {} to {}".format(file.title, path_other))
                            # shutil.move(file.source, self.config.fullpath(path_other, filename))
                            pass
                    files.append(file)
        if self.config.movie:
            global moved
            folders = []
            for dirname, dirnames, filenames in os.walk(self.config.path_initial):
                if self.config.verbose:
                    print("dirnames: {}".format(dirnames))
                for folder in dirnames:
                    folders.append(MovieFolder(folder, self.config))
                for movie in folders:
                    movie.source = self.config.fullpath(dirname, movie.directory)
                    if self.config.verbose:
                        print("Source: {}".format(movie.source))
                    if movie.get_title(verbose=self.config.verbose):
                        print("Recognised: Moving {} to {}".format(movie.source, self.config.path_final))
                        try:
                            shutil.move(movie.source, self.config.path_final)
                            moved += 1
                        except shutil.Error as e:
                            print(e)
            print("Total folders: {}".format(len(folders)))
            print("Folders moved: {}".format(moved))
    #
    # def store_names(directory, location):
    #     w = csv.writer(open(location, "w"))
    #     for key, add in directory.items():
    #         w.writerow([key])

    def make_list(self):
        dir_lookup = {}
        for dirname, dirnames, filenames in os.walk(self.config.path_final):
            splitted = dirname.split('\\')
            lowerc = splitted[-1].lower()
            dir_full = dirname + "\\"
            if "season" not in lowerc:
                # print("Adding: " + lowerc)
                dir_lookup.update({lowerc: dir_full})
        # print(dir_lookup)
        self.tv_directories = dir_lookup

    def sort_media(self):
        self.make_list()
        self.sort_files()


class MovieFolder(MediaFile):
    def __init__(self, directory, config):
        super().__init__(None)
        self.config = config
        self.directory = directory

    # Should be tested but also working
    def get_title(self, verbose=False):
        split_directory = []
        splitted = self.directory.split(self.config.delim)
        for word in splitted:
            split_word = word.split('.')
            for word2 in split_word:
                split_directory.append(word2)
        if verbose:
            print(split_directory)
        title = ""

        for word in split_directory:
            for code in config.regex_list:
                regex = re.compile(code)
                if re.match(regex, word):
                    if verbose:
                        print("Move: {}".format(title))
                    self.title = title.strip(" ")
                    return True
            title = title + " "
            title = title + word
        if verbose:
            print("Skip: {}".format(title))
        self.title = title.strip(" ")
        return False


tv_sorter = Sorter.tv()
tv_sorter.sort_tv()

