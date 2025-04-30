from smolcrawler.url_utils import get_url_variations, is_similar_url, normalize_url


def test_normalize_url():
    # Test basic URL normalization
    assert normalize_url("https://example.com/page") == "https://example.com/page"
    assert normalize_url("https://example.com/page/") == "https://example.com/page"
    assert normalize_url("https://example.com/page#section") == "https://example.com/page"
    assert normalize_url("https://example.com/page?param=value") == "https://example.com/page"
    assert normalize_url("https://example.com/page/?param=value#section") == "https://example.com/page"


def test_get_url_variations():
    # Test URL variations generation
    variations = get_url_variations("https://example.com/page")
    assert len(variations) == 2
    assert "https://example.com/page" in variations
    assert "https://example.com/page/" in variations

    # Test with trailing slash
    variations = get_url_variations("https://example.com/page/")
    assert len(variations) == 1
    assert "https://example.com/page" in variations


def test_is_similar_url():
    # Test URL similarity detection
    assert is_similar_url("https://example.com/page", "https://example.com/page/")
    assert is_similar_url("https://example.com/page#section", "https://example.com/page")
    assert is_similar_url("https://example.com/page?param=value", "https://example.com/page")
    assert is_similar_url("https://example.com/page", "https://example.com/page")

    # Test different URLs
    assert not is_similar_url("https://example.com/page1", "https://example.com/page2")
    assert not is_similar_url("https://example1.com/page", "https://example2.com/page")
    assert not is_similar_url("http://example.com/page", "https://example.com/page")
