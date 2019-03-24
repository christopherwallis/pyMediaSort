from pyMediaSort import Sorter


initial = "/home/pi/Downloads/"
tv = "/media/pi/CLEARSSD120/tv"
movies = "/media/pi/CLEARSSD120/movies"


tv_sorter = Sorter.tv(initial=initial, final=tv, verbose=True, windows=False)
tv_sorter.sort_media()
movie_sorter = Sorter.movies(initial=initial, final=movies, verbose=True, windows=False)
movie_sorter.sort_media()
