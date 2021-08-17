from os import getcwd
from os.path import join, isdir
from functools import reduce
from datetime import datetime
from json import dump
from src.cinema import CinemaLaPlataScrapy
from src.cinepolis import CinepolisScrapy


class Scraper:
    """A class to merge scraped data

    driver_executable (str): path to the executable for the browser's
        driver
    browser_executable (str): path to the user's browser.exe
    """

    def __init__(
        self,
        driver_executable="chromedriver",
        browser_executable="/usr/bin/brave",
    ):
        """Initialize the scraper with two scrapies

        Args:
            driver_executable (str, optional): Driver for navigation.
                Defaults to "chromedriver".
            browser_executable (str, optional): Path to browser
                executable. Defaults to "/usr/bin/brave".
        """
        self.scrapies = [
            CinemaLaPlataScrapy(),
            CinepolisScrapy(
                driver_executable=driver_executable,
                browser_executable=browser_executable,
            ),
        ]

    def _difference(self, dictionary, intersection):
        """This method returns a dictionary without the intersected keys

        Args:
            dictionary (dict): A movie
            intersection (set): Shared keys

        Returns:
            dict: dictionary without the intersected keys
        """
        return {
            key: dictionary[key]
            for key in set(dictionary.keys()).difference(intersection)
        }

    def _merge_keys(self, movie, shared_keys, a_movie, b_movie):
        """This method merges information from specific keys

        Args:
            movie (dict): Movie's not shared data
            shared_keys (list): Keys shared by a_movie and b_movie
            a_movie (dict): A movie's data
            b_movie (dict): Another movie's data

        Returns:
            tuple(dict, list): contains the movie with the merged data
                and the new list of shared keys
        """
        for key in ["Actores", "Género"]:
            if key in shared_keys:
                movie[key] = list(set(a_movie[key] + b_movie[key]))
                shared_keys.remove(key)

        if "Horarios" in shared_keys:
            movie["Horarios"] = {**a_movie["Horarios"], **b_movie["Horarios"]}
            shared_keys.remove("Horarios")

        return movie, shared_keys

    def _merge_movies(self, a_movie, a_source, b_movie, b_source):
        """This method merges the information of two movies

        Args:
            a_movie (dict): A movie's data
            a_source (str): A movie's source of data
            b_movie (dict): Another movie's data
            b_source (str): Another movie's source of data

        Returns:
            dict: Merged movie's data
        """

        shared_keys = set(a_movie.keys()).intersection(set(b_movie.keys()))

        movie, shared_keys = self._merge_keys(
            dict(
                self._difference(a_movie, shared_keys),
                **self._difference(b_movie, shared_keys)
            ),
            shared_keys,
            a_movie,
            b_movie,
        )

        a_data = {}
        b_data = {}

        for key in shared_keys:
            if a_movie[key] == b_movie[key]:
                movie[key] = a_movie[key]
            else:
                a_data[key] = a_movie[key]
                b_data[key] = b_movie[key]

        if a_data:
            movie[a_source] = a_data
            movie[b_source] = b_data

        return movie

    def _merge(self, a, b):
        """This method recieves two tuples and merges the information
            within their dictionaries respecting their source when
            appropriate

        Args:
            a (tuple(dict, str)): First dict of movies and its source
            b (tuple(dict, str)): Second dict of movies and its source

        Returns:
            dict: Merged movies
        """

        a_movies, a_source = a
        b_movies, b_source = b

        shared_movies = set(a_movies.keys()).intersection(set(b_movies.keys()))

        movies = dict(
            self._difference(a_movies, shared_movies),
            **self._difference(b_movies, shared_movies)
        )

        for movie in shared_movies:
            movies.update(
                {
                    movie: self._merge_movies(
                        a_movies[movie], a_source, b_movies[movie], b_source
                    )
                }
            )

        return movies

    def scrape(self):
        """This method starts the scraping of both pages and saves the
            gathered data into the recieved path

        Args:
            path (optional[str]): path to save the information in.
                Defaults to "../data/".
        """
        with open(
            join(
                getcwd(),
                "data",
                "movies_"
                + datetime.today().strftime("%Y-%m-%d-%H_%M_%S")
                + ".json",
            ),
            "w",
            encoding="utf8",
        ) as file:
            dump(
                self._merge(
                    *map(lambda scrapy: scrapy.scrape(), self.scrapies)
                ),
                file,
                ensure_ascii=False,
                indent=4,
                sort_keys=True,
            )
