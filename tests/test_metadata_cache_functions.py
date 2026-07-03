import unittest

from functions import metadataCacheFunctions as metadata_cache


class MetadataCacheFunctionsTest(unittest.TestCase):
    def test_build_metadata_cache_keeps_current_context_rows(self):
        record = {
            "type": "torrents",
            "item_id": 1,
            "file_id": 2,
            "file_size": 100,
            "file_name": "Example.Movie.mkv",
            "metadata_title": "Example Movie",
            "metadata_filename": "Example Movie.mkv",
            "metadata_cache_context": metadata_cache.metadataCacheContext(),
        }

        cache = metadata_cache.buildMetadataCache([record])
        key = metadata_cache.metadataCacheKeyFromRecord(record)

        self.assertIn(key, cache)
        self.assertEqual(cache[key]["metadata_title"], "Example Movie")
        self.assertEqual(cache[key]["metadata_cache_context"], metadata_cache.metadataCacheContext())

    def test_build_metadata_cache_skips_stale_context_rows(self):
        record = {
            "type": "torrents",
            "item_id": 1,
            "file_id": 2,
            "file_size": 100,
            "file_name": "Example.Movie.mkv",
            "metadata_title": "Example Movie",
            "metadata_cache_context": "metadata:other",
        }

        cache = metadata_cache.buildMetadataCache([record])

        self.assertEqual(cache, {})


if __name__ == "__main__":
    unittest.main()
