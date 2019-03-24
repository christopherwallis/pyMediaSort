#!/usr/bin/env python

import os
import shutil
import re
# import csv
# import SortMovies
from setup import Directory, SetupError
# from GetMagnetRSS import create_to_download


# Default directories:
default_initial = os.getcwd()
default_tv = os.path.join(os.getcwd(), "tv")
default_movies = os.path.join(os.getcwd(), "Movies")


class MediaFile(object):
    """
    Object associated with a media file
    """
    def __init__(self, filename, progresscbf=print):
        self.filename = filename
        self.directory = None
        self.season = None
        self.title = None
        self.source = None
        self.progresscbf = progresscbf


class Sorter:
    """
    Creates sorting object for a particular folder and media type
    """
    def __init__(self, config, progresscbf):
        self.config = config
        self.progresscbf = progresscbf
        self.tv_directories = []

    @classmethod
    def tv(cls, initial=None, final=None, verbose=False, progresscbf=print, windows=True):
        if not initial:
            raise SetupError("Initial file location missing")
        if not final:
            raise SetupError("Final file location missing")
        config = Directory.tv_shows(path_initial=initial, path_destination=final, verbose=verbose, progresscbf=progresscbf, windows=windows)
        return cls(config, progresscbf)

    @classmethod
    def movies(cls, initial=None, final=None, verbose=False, progresscbf=print, windows=True):
        call = ""
        if not initial:
            raise SetupError("Initial file location missing")
        if not final:
            raise SetupError("Final file location missing")
        config = Directory.movies(path_initial=initial, path_final=final, verbose=verbose, progresscbf=progresscbf, windows=windows)
        return cls(config, progresscbf)

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
                        except Exception as e:
                            if self.config.verbose:
                                self.progresscbf(e)
                            try:
                                stripped = word.strip('[').strip(']').split('x')
                                file.season = int(stripped[0])
                            except Exception as e:
                                if self.config.verbose:
                                    self.progresscbf(e)
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
                self.progresscbf(split_directory)
            title = ""

            for word in split_directory:
                for code in self.config.regex_list:
                    regex = re.compile(code)
                    if re.match(regex, word):
                        if self.config.verbose:
                            self.progresscbf("Move: {}".format(title))
                        self.title = title.strip(" ")
                        return True
                title = title + " "
                title = title + word
            if self.config.verbose:
                self.progresscbf("Skip: {}".format(title))
            self.title = title.strip(" ")
            return False

    def sort_files(self):
        if self.config.tv:
            files = []
            for dirname, dirnames, filenames in os.walk(self.config.path_initial):
                # print(filenames)
                for filename in filenames:
                    file = MediaFile(filename)
                    # print(filename.split('.')[-1])
                    if filename.split('.')[-1] in self.config.extension_list:
                        file.source = self.config.fullpath(dirname, filename)
                        # print(source)
                        file.title = self.get_title(file, '.')
                        # print(filename)
                        if file.title is False:
                            file.title = self.get_title(file, ' ')
                        print(file.title)
                        if filename is None:
                            # print("Pass")
                            pass
                        # elif file.title is "":
                        #     print("No title  : Moving {} to {}".format(file.filename, path_other))
                        #     shutil.move(file.source, self.config.fullpath(path_other, filename))
                        elif file.title in self.tv_directories:
                            destination = self.tv_directories[file.title]
                            destination = destination + "Season {}\\".format(file.season)
                            if not os.path.isdir(destination):
                                # print("Directory does not exist: Creating")
                                os.mkdir(destination)
                            self.progresscbf("Recognised: Moving {} to {}".format(file.title, destination))
                            shutil.move(file.source, self.config.fullpath(destination, filename))
                            self.config.moved += 1
                        else:
                            # print("Default   : Moving {} to {}".format(file.title, path_other))
                            # shutil.move(file.source, self.config.fullpath(path_other, filename))
                            pass
                    files.append(file)
            self.progresscbf("Total files: {}".format(len(files)))
        if self.config.movie:
            if self.config.verbose:
                self.progresscbf("Sorting movie files:")
                self.progresscbf(self.config.path_initial)
            folders = []
            for dirname, dirnames, filenames in os.walk(self.config.path_initial):
                if self.config.verbose:
                    self.progresscbf("dirnames: {}".format(dirnames))
                for folder in dirnames:
                    folders.append(MovieFolder(folder, self.config))
                for movie in folders:
                    movie.source = self.config.fullpath(dirname, movie.directory)
                    if self.config.verbose:
                        self.progresscbf("Source: {}".format(movie.source))
                    if movie.get_title(verbose=self.config.verbose):
                        self.progresscbf("Recognised: Moving {} to {}".format(movie.source, self.config.path_final))
                        try:
                            shutil.move(movie.source, self.config.path_final)
                            self.config.moved += 1
                        except shutil.Error as e:
                            self.progresscbf(e)
            self.progresscbf("Total folders: {}".format(len(folders)))
        self.progresscbf("Folders moved: {}".format(self.config.moved))
    #
    # def store_names(directory, location):
    #     w = csv.writer(open(location, "w"))
    #     for key, add in directory.items():
    #         w.writerow([key])

    def make_list(self):
        dir_lookup = {}
        print("Directory split: {}".format(self.config.dirsplit))
        for dirname, dirnames, filenames in os.walk(self.config.path_final):
            splitted = dirname.split(self.config.dirsplit)
            lowerc = splitted[-1].lower()
            dir_full = dirname + self.config.dirsplit
            if "season" not in lowerc:
                # print("Adding: " + lowerc)
                dir_lookup.update({lowerc: dir_full})
        # print(dir_lookup)
        self.tv_directories = dir_lookup

    def sort_media(self):
        if self.config.tv:
            self.progresscbf("Sorting TV files:")
            if self.config.verbose:
                self.progresscbf("Current Directory: {}".format(self.config.path_initial))
                self.progresscbf("Target Directory:  {}".format(self.config.path_final))
        if self.config.movie:
            self.progresscbf("Sorting Movie files:")
            if self.config.verbose:
                self.progresscbf("Current Directory: {}".format(self.config.path_initial))
                self.progresscbf("Target Directory:  {}".format(self.config.path_final))
        self.make_list()
        # print(self.tv_directories)
        self.sort_files()


class MovieFolder(MediaFile):
    def __init__(self, directory, config, progresscbf=print):
        super().__init__(None, progresscbf=progresscbf)
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
            self.progresscbf(split_directory)
        title = ""

        for word in split_directory:
            for code in self.config.regex_list:
                regex = re.compile(code)
                if re.match(regex, word):
                    if verbose:
                        self.progresscbf("Move: {}".format(title))
                    self.title = title.strip(" ")
                    return True
            title = title + " "
            title = title + word
        if verbose:
            self.progresscbf("Skip: {}".format(title))
        self.title = title.strip(" ")
        return False


