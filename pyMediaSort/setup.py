# Configuration classes for directories for pyMediaSort
# cwallis
# March 2019

import os

# Default directories:
default_initial = os.getcwd()
default_tv = os.path.join(os.getcwd(), "tv")
default_movies = os.path.join(os.getcwd(), "Movies")


# Configuration settings for a directory of media files
class Directory:
    def __init__(self, path_final, path_initial, path_output, extension_list, regex_list, delim, regex_remove, verbose=False, tv=False, movie=False, progresscbf=print):
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
        self.movie = movie
        self.progresscbf = progresscbf

    @classmethod
    def tv_shows(cls, path_destination=default_tv, path_initial=default_initial, verbose=False, progresscbf=print):
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
        return cls(path_final=path_tv, path_initial=path_initial, path_output=names_out, extension_list=extension_list,
                   regex_list=regex_list, delim=delim, regex_remove=regex_remove, verbose=verbose, tv=True,
                   progresscbf=progresscbf)

    @classmethod
    def movies(cls, path_initial=default_initial, path_final=default_movies, verbose=False, progresscbf=print):
        print("Verbose: {}".format(verbose))
        # path_initial = path_initial
        # movie_destination = path_final
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
        return cls(path_initial=path_initial, path_final=path_final, path_output=names_out,
                   extension_list=extension_list, regex_list=regex_list, delim=delim, regex_remove=regex_remove,
                   verbose=verbose, movie=True, progresscbf=progresscbf)


class SetupError(Exception):
    pass
