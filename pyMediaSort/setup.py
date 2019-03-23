# Configuration classes for firectories for pyMediaSort
# cwallis
# March 2019

import os
# Default directories:
default_initial = "E:\\Media\\Shared"
default_tv = "E:\\Media\\TV"
default_movies = "M:\\Media\\Movies"


# Configuration settings for a directory of media files
class Directory:
    def __init__(self, path_final, path_initial, path_output, extension_list, regex_list, delim, regex_remove, verbose=False, tv=False, movies=False):
        self.fullpath = os.path.join
        self.path_final = path_final
        self.path_initial = path_initial
        self.path_output = path_output
        self.extension_list = extension_list
        self.regex_list = regex_list
        self.delim = delim
        self.regex_remove = regex_remove
        self.moved = 0
        self.verbose = verbose
        self.tv = tv
        self.movies = movies

    @classmethod
    def tv_shows(cls, path_destination=default_tv, path_initial=default_initial, verbose=False):
        path_tv = path_destination
        path_initial = path_initial
        names_out = os.path.join(path_initial, "TV_output.csv")
        extension_list = [
            r"avi",
            r'mkv'
            ]
        regex_list = [
            '[Ss][1234567890][1234567890][Ee][1234567890][1234567890]',
            '20[12][1234567890]',
            '[[({]?[Ss]?[0123]?[1234567890][EeXx][1234567890][1234567890]',
            # '[Ss]eason'
            # '[0-9][0-9][0-9]'
        ]
        delim = ' '
        regex_remove = '-'
        return cls(path_final=path_tv, path_initial=path_initial, path_output=names_out, extension_list=extension_list, regex_list=regex_list, delim=delim, regex_remove=regex_remove, tv=True)


    @classmethod
    def movies(cls, path_initial=default_initial, path_destination=default_movies, verbose=False):
        path_initial = path_initial
        movie_destination = path_destination
        names_out = os.path.join(path_initial, "Movies_output.csv")
        extension_list = {
            r"avi",
            r'mkv'
        }
        regex_list = [
            '\([12][1234567890][1234567890][1234567890]\)'
        ]
        delim = ' '
        regex_remove = '-'
        return cls(path_initial=path_initial, path_final=movie_destination, path_output=names_out, extension_list=extension_list, regex_list=regex_list, delim=delim, regex_remove=regex_remove, verbose=verbose, movies=True)