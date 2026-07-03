import unittest

from functions import organizationFunctions as organization


class OrganizationFunctionsTest(unittest.TestCase):
    def setUp(self):
        self.original_mode = organization.ORGANIZATION_MODE

    def tearDown(self):
        organization.ORGANIZATION_MODE = self.original_mode

    def test_parsed_series_metadata_uses_show_and_season(self):
        metadata = organization.buildParsedMetadata(
            "Example Show",
            {"title": "Example Show", "season": 2, "episode": 3},
            "Example.Show.S02E03.mkv",
            "Example.Show.S02.1080p",
        )

        self.assertEqual(metadata["metadata_mediatype"], "series")
        self.assertEqual(metadata["metadata_rootfoldername"], "Example Show")
        self.assertEqual(metadata["metadata_foldername"], "Season 2")

    def test_parsed_movie_metadata_uses_title_and_year(self):
        metadata = organization.buildParsedMetadata(
            "Example Movie",
            {"title": "Example Movie", "year": "2024"},
            "Example.Movie.2024.mkv",
            "Example.Movie.2024.1080p",
        )

        self.assertEqual(metadata["metadata_mediatype"], "movie")
        self.assertEqual(metadata["metadata_rootfoldername"], "Example Movie (2024)")

    def test_organized_path_routes_series_under_series(self):
        organization.ORGANIZATION_MODE = organization.OrganizationModes.parsed.value
        data = {
            "metadata_mediatype": "series",
            "metadata_rootfoldername": "Example Show",
            "metadata_foldername": "Season 2",
            "metadata_filename": "Example.Show.S02E03.mkv",
        }

        self.assertEqual(
            organization.organizedPathParts(data),
            ["series", "Example Show", "Season 2", "Example.Show.S02E03.mkv"],
        )

    def test_raw_path_preserves_original_tree_safely(self):
        organization.ORGANIZATION_MODE = organization.OrganizationModes.raw.value
        data = {"path": "Folder/Season 1/Episode 01.mkv"}

        self.assertEqual(
            organization.organizedPathParts(data),
            ["Folder", "Season 1", "Episode 01.mkv"],
        )

    def test_parsed_series_metadata_handles_string_numbers(self):
        metadata = organization.buildParsedMetadata(
            "Example Show",
            {"title": "Example Show", "season": "2", "episode": "3"},
            "Example.Show.S02E03.mkv",
            "Example.Show.S02.1080p",
        )

        self.assertEqual(metadata["metadata_foldername"], "Season 2")


if __name__ == "__main__":
    unittest.main()
