from abc import ABC, abstractmethod
from functools import reduce


class CinemaScrapy(ABC):
    """Abstract scraper for cinema pages

    _cinema_page (str): Link to fetch for movies
    """

    def __init__(self, _cinema_page):
        """This method performs a generic initialization of a Scrapy

        Args:
            _cinema_page (str): Link to the main website to scrap.
        """
        self._cinema_page = _cinema_page

    @abstractmethod
    def _scrape_movie_title(self, movie_container):
        """This method scraps the title of a movie

        Args:
            movie_container (any): Web container of the movie

        Returns:
            str: title of a movie
        """
        return

    @abstractmethod
    def _scrape_movie_synopsis(self, movie_container):
        """This method scraps the synopsis of a movie

        Args:
            movie_container (any): Web container of the movie

        Returns:
            dict:  Dictionary with "Sinopsis" as key and a movie's synopsis as
                value
        """
        return

    @abstractmethod
    def _separate_movie_traits(self, traits):
        """This methods splits every list-like string in 'traits' that's
            considered fitting

        Args:
            traits (dict): Traits of a movie

        Returns:
            dict: Traits of a movie with reformatted keys
        """
        return

    def _split_string_trait(self, traits, trait, separator):
        """This method splits a string in 'traits' with key 'trait' by
            'separator', replacing the original string with a list.

        Args:
            traits (dict): Traits of a movie
            trait (str): Movie trait representing a list
            separator (str): Separator of the trait's list

        Returns:
            dict: Traits of a movie
        """
        if trait in traits.keys():
            traits[trait] = traits[trait].split(separator)
        return traits

    @abstractmethod
    def _collect_movie_traits(self, movie_container):
        """This method fetches the traits of a movie from the movie
            container

        Args:
            movie_container (any): Web container of the movie

        Returns:
            dict: Collected traits of a movie
        """
        return

    def _scrape_movie_traits(self, movie_container):
        """This method obtains the traits of a movie

        Args:
            movie_container (any): Web container of the movie

        Returns:
            dict: Traits of a movie
        """
        return self._separate_movie_traits(
            self._collect_movie_traits(movie_container)
        )

    @abstractmethod
    def _scrape_movie_schedule(self, movie_container):
        """This method obtains a movie's schedule

        Args:
            movie_container (any): Web container of the movie

        Returns:
            dict: Movie with schedule data
        """
        return

    def scrape_movie(self, movie_container):
        """This method scrapes a movie page

        Args:
            movie_container (any): movie information container

        Returns:
            dict: Data of movie
        """
        return {
            self._scrape_movie_title(movie_container): self._normalize_movie(
                reduce(
                    lambda a, b: {**a, **b},
                    [
                        self._scrape_movie_synopsis(movie_container),
                        self._scrape_movie_traits(movie_container),
                        self._scrape_movie_schedule(movie_container),
                    ],
                )
            )
        }

    @abstractmethod
    def _normalize_movie(self, movie):
        """This method normalizes a movie's data

        Args:
            movie (dict): A movie data

        Returns:
            dict: Normalized movie data
        """
        return

    @abstractmethod
    def scrape(self):
        """This method starts the scrapping of a cinema's billboard page

        Returns:
            dict: Data of movies
            str: Source of data
        """
        return
