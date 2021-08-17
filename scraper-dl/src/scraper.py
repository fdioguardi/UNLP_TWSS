from src.movie import Movie
from src.metadata import Metadata
from functools import reduce
from json import dump
from os import getcwd
from os.path import join, isdir


class Scraper(object):
    def scrape(self, urls_list):
        """Parse structured data from a list of pages."""

        if isinstance(urls_list, list):
            for urls in urls_list:
                self.scrape_movie(urls)
        else:
            self.scrape_movie(urls_list)

    def scrape_movie(self, urls):
        if isinstance(urls, list) and len(urls) > 1:
            movie = reduce(
                lambda movie, another_movie: movie.merge(another_movie),
                [Movie(Metadata(url).get_json_dl()).normalize(url) for url in urls],
            )
        else:
            movie = Movie(Metadata(urls).get_json_dl())

        movie = movie.remove_data(
            [
                "@id",
                "dateCreated",
                "dateModified",
                "datePublished",
                "url",
            ]
        )

        self.save_movie(movie.data)
        return movie

    def save_movie(self, data):
        with open(
            self.create_file_name(data),
            "w",
            encoding="utf8",
        ) as file:
            dump(data, file, ensure_ascii=False, indent=4, sort_keys=True)

    def create_file_name(self, data):
        name = data["name"] if "name" in data.keys() else "Movie"
        if isinstance(name, list):
            name = name[0]

        return join(getcwd(), "data", name + ".json")
