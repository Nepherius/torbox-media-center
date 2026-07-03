import unittest

from functions.fileFilterFunctions import isSampleFile


class FileFilterFunctionsTest(unittest.TestCase):
    def test_skips_exact_sample_name(self):
        file = {
            "short_name": "sample.mkv",
            "name": "Movie.Release/sample.mkv",
            "size": 50 * 1024 * 1024,
        }

        self.assertTrue(isSampleFile(file))

    def test_skips_numbered_sample_name(self):
        file = {
            "short_name": "Sample2.mp4",
            "name": "Movie.Release/Sample2.mp4",
            "size": 50 * 1024 * 1024,
        }

        self.assertTrue(isSampleFile(file))

    def test_skips_sample_folder(self):
        file = {
            "short_name": "Movie.Release.mkv",
            "name": "Movie.Release/Sample/Movie.Release.mkv",
            "size": 50 * 1024 * 1024,
        }

        self.assertTrue(isSampleFile(file))

    def test_keeps_real_title_containing_sample_when_large(self):
        file = {
            "short_name": "Sample.People.2000.mkv",
            "name": "Sample.People.2000/Sample.People.2000.mkv",
            "size": 2 * 1024 * 1024 * 1024,
        }

        self.assertFalse(isSampleFile(file))

    def test_can_include_sample_files(self):
        file = {
            "short_name": "sample.mkv",
            "name": "Movie.Release/sample.mkv",
            "size": 50 * 1024 * 1024,
        }

        self.assertFalse(isSampleFile(file, include_sample_files=True))


if __name__ == "__main__":
    unittest.main()
