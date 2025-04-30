from smolcrawler.utils import get_default_url_prefix


def test_get_default_url_prefix():
    assert (
        get_default_url_prefix("https://swiftpackageindex.com/grpc/grpc-swift-protobuf")
        == "https://swiftpackageindex.com"
    )
    assert get_default_url_prefix("https://docs.scylladb.com/manual/stable/") == "https://docs.scylladb.com"
    assert get_default_url_prefix("https://docs.scylladb.com/manual/stable") == "https://docs.scylladb.com"
    # special case for deepwiki
    assert get_default_url_prefix("https://deepwiki.com/groue/GRDB.swift") == "https://deepwiki.com/groue/GRDB.swift"
    assert get_default_url_prefix("https://deepwiki.com/groue/GRDB.swift/") == "https://deepwiki.com/groue/GRDB.swift"
