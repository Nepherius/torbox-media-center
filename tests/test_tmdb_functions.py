import unittest

from functions.organizationFunctions import buildParsedMetadata
from functions import tmdbFunctions
from functions.tmdbFunctions import buildTmdbMetadata


class TmdbFunctionsTest(unittest.TestCase):
    def test_build_movie_metadata_from_tmdb_result(self):
        fallback = buildParsedMetadata(
            "Example Movie",
            {"title": "Example Movie", "year": "2024"},
            "Example.Movie.2024.mkv",
            "Example.Movie.2024.1080p",
        )
        result = {
            "id": 123,
            "title": "Example Movie",
            "release_date": "2024-05-01",
            "poster_path": "/poster.jpg",
            "backdrop_path": "/backdrop.jpg",
        }

        metadata = buildTmdbMetadata(result, "movie", {"year": "2024"}, "Example.Movie.2024.mkv", fallback)

        self.assertEqual(metadata["metadata_provider"], "tmdb")
        self.assertEqual(metadata["metadata_mediatype"], "movie")
        self.assertEqual(metadata["metadata_rootfoldername"], "Example Movie (2024)")
        self.assertEqual(metadata["metadata_filename"], "Example Movie (2024).mkv")
        self.assertEqual(metadata["metadata_link"], "https://www.themoviedb.org/movie/123")
        self.assertEqual(metadata["metadata_image"], "https://image.tmdb.org/t/p/original/poster.jpg")

    def test_build_series_metadata_from_tmdb_result(self):
        fallback = buildParsedMetadata(
            "Example Show",
            {"title": "Example Show", "season": "2", "episode": "3"},
            "Example.Show.S02E03.mkv",
            "Example.Show.S02.1080p",
        )
        result = {
            "id": 456,
            "name": "Example Show",
            "first_air_date": "2022-09-10",
            "poster_path": None,
            "backdrop_path": "/show-backdrop.jpg",
        }

        metadata = buildTmdbMetadata(
            result,
            "series",
            {"season": "2", "episode": "3"},
            "Example.Show.S02E03.mkv",
            fallback,
        )

        self.assertEqual(metadata["metadata_provider"], "tmdb")
        self.assertEqual(metadata["metadata_mediatype"], "series")
        self.assertEqual(metadata["metadata_rootfoldername"], "Example Show (2022)")
        self.assertEqual(metadata["metadata_foldername"], "Season 2")
        self.assertEqual(metadata["metadata_filename"], "Example Show S02E03.mkv")
        self.assertEqual(metadata["metadata_link"], "https://www.themoviedb.org/tv/456")
        self.assertIsNone(metadata["metadata_image"])

    def test_search_tmdb_metadata_without_credentials_uses_fallback(self):
        original_key = tmdbFunctions.TMDB_API_KEY
        original_token = tmdbFunctions.TMDB_ACCESS_TOKEN
        tmdbFunctions.TMDB_API_KEY = None
        tmdbFunctions.TMDB_ACCESS_TOKEN = None

        try:
            metadata, success, detail = tmdbFunctions.searchTmdbMetadata(
                "Example Movie",
                {"title": "Example Movie", "year": "2024"},
                "Example.Movie.2024.mkv",
                "Example.Movie.2024.1080p",
            )
        finally:
            tmdbFunctions.TMDB_API_KEY = original_key
            tmdbFunctions.TMDB_ACCESS_TOKEN = original_token

        self.assertFalse(success)
        self.assertIn("not configured", detail)
        self.assertEqual(metadata["metadata_rootfoldername"], "Example Movie (2024)")


if __name__ == "__main__":
    unittest.main()
