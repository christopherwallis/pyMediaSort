from pyMediaSort import Sorter


initial = "E:\\Media\\Shared"
tv = "E:\\Media\\TV"
movies = "M:\\Media\\Movies"


tv_sorter = Sorter.tv(initial=initial, final=tv, verbose=True)
tv_sorter.sort_media()
movie_sorter = Sorter.movies(initial=initial, final=movies, verbose=True)
movie_sorter.sort_media()
