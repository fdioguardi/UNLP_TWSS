from src.abstract_cinema import CinemaScrapy
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CinepolisScrapy(CinemaScrapy):
    """Scrapper of Cinepolis's billboard"""

    def __init__(self, driver_executable, browser_executable):
        """This method initialize the scrapy

        Args:
            driver_executable (str): Driver for navigation. Defaults to
                "chromedriver".
            browser_executable (str): Path to browser executable.
                Defaults to "/usr/bin/brave".
        """

        super().__init__(_cinema_page="http://www.villagecines.com/")
        self.browser_executable = browser_executable
        self.driver_executable = driver_executable

    def driver(self):
        """This method creates an instance of WebDriver

        Returns:
            WebDriver: Driver to navigate throw internet like a person
        """
        options = webdriver.ChromeOptions()
        options.binary_location = self.browser_executable
        return webdriver.Chrome(
            executable_path=self.driver_executable, options=options
        )

    def _scrape_movie_title(self, driver):
        """This method scraps the title of a movie

        Args:
            driver (WebDriver): Web container of the movie

        Returns:
            str: title of a movie
        """
        return (
            driver.find_element_by_class_name("title-text")
            .text.strip()
            .upper()
        )

    def _scrape_cinema_name(self, cinema):
        """ This method obtains the cinema's name

        Args:
            cinema (WebElement): Web element with a cinema's name

        Returns:
            str: cinema's name
        """
        return cinema.find_element_by_class_name("btn-link").text.strip()

    def _scrape_movie_auditorium_and_schedule(self, cinema):
        """
        This method creates a dictionary with a cinema's name and
        it's showtime schedule

        Args:
            cinema (WebbElement): Web element with a cinema's schedule

        Returns:
            dict: auditorium as key and schedule as value
        """
        return {
            combination.find_element_by_class_name(
                "text-uppercase"
            ).text.strip(): [
                anchor.text for anchor in combination.find_elements_by_tag_name("a")
            ]
            for combination in cinema.find_elements_by_class_name(
                "movie-showtimes-component-combination"
            )
        }

    def _scrape_movie_schedule(self, driver):
        """This method obtains a movie's schedule

        Args:
            movie_container (WebDriver): Web container of the movie

        Returns:
            dict: Movie with schedule data
        """
        schedule_tab = driver.find_element_by_class_name(
            "movie-detail-showtimes-component"
        )

        schedule_data = {}
        for cinema in schedule_tab.find_elements_by_class_name(
            "panel-primary"
        ):
            cinema.click()
            schedule_data[
                self._scrape_cinema_name(cinema)
            ] = self._scrape_movie_auditorium_and_schedule(cinema)
        return {"Horarios": schedule_data}

    def _scrape_movie_synopsis(self, movie_driver):
        """This method scraps the synopsis of a movie

        Args:
            movie_container (WebDriver): Web container of the movie

        Returns:
            dict:  Dictionary with "Sinopsis" as key and a movie's
                synopsis as value
        """
        return {
            "Sinopsis": movie_driver.find_element_by_id(
                "sinopsis"
            ).text.strip()
        }

    def _wait_for_traits(self, movie_driver, timeout=10):
        """Wait for traits to load.

        Args:
            movie_driver (WebDriver): Movie's data container
            timeout (int, optional): time in second, to wait for tha
                page to do something. Defaults to 10.

        Raises:
            TimeoutException: When the trait didn't load after 'timeout'
            seconds

        """

        WebDriverWait(movie_driver, timeout).until(
            EC.text_to_be_present_in_element((By.ID, "tecnicos"), "Título")
        )

    def _collect_movie_traits(self, movie_driver):
        """This method fetches the traits of a movie from the movie
            container

        Args:
            movie_container (WebDriver): Web container of the movie

        Returns:
            dict: Collected traits of a movie
        """
        movie_driver.find_element_by_id("tecnicos-tab").click()
        self._wait_for_traits(movie_driver)

        traits = {}
        try:
            for trait in movie_driver.find_element_by_id("tecnicos").text.split(
                "\n"
            ):
                key, value = trait.split(": ", 1)
                traits[key] = value
        except ValueError:
            pass

        return traits

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

    def _separate_movie_traits(self, traits):
        """This methods splits every list-like string in 'traits' that's
            considered fitting

        Args:
            traits (dict): Traits of a movie

        Returns:
            dict: Traits of a movie with reformatted keys
        """
        for trait in ["Actores", "Género"]:
            traits = self._split_string_trait(traits, trait, ", ")
        return traits

    def _normalize_movie(self, movie):
        """This method normalizes a movie's data

        Args:
            movie (dict): A movie data

        Returns:
            dict: Normalized movie data
        """
        if "Duración" in movie.keys():
            movie["Duración"] = movie["Duración"][:-1] + "utos"
        return movie

    def scrape(self):
        """
        This method starts the scrapping of a cinepolis's billboard page

        Returns:
            dict: Data of movies
            str: Source of data
        """
        movies = {}
        driver = self.driver()
        driver.get(self._cinema_page)
        movie_container = driver.find_element_by_class_name("movie-grid")
        for movie in [
            anchor.get_attribute("href")
            for anchor in movie_container.find_elements_by_tag_name("a")
        ]:
            try:
                driver.get(movie)
                movies.update(self.scrape_movie(driver))
            except TimeoutException:
                pass

        driver.quit()
        return movies, "Cinepolis"
