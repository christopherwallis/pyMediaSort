import os
from pyMediaSort import Sorter

path_old_tv = "E:\\Media\\TV"
path_new_tv = "G:\\Media\\TV"


def get_dir_structure(tv_directories):
    show_list = []
    for show in tv_directories.keys():
        show_list.append(show.capitalize())
    print(show_list)
    return show_list


def make_dirs(list, target, verbose=False):
    total = 0
    for directory in list:
        path = os.path.join(target, directory)
        try:
            os.mkdir(path)
            total += 1
            if verbose:
                print("Created: {}".format(path))
        except OSError:
            print("Creation of the directory %s failed" % path)
    return total


def duplicate_tv_dirs(initial, final):
    directories = Sorter.tv(initial="NA", final=initial, verbose=True)
    directories.make_list()
    print(directories.tv_directories)
    shows = get_dir_structure(directories.tv_directories)
    total_to_create = len(shows)
    total_created = make_dirs(shows, final)
    print("Created {} / {}".format(total_created, total_to_create))


duplicate_tv_dirs(path_old_tv, path_new_tv)
