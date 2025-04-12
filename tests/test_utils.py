from urllib.parse import urljoin

from smolcrawler.utils import extract_urls, is_valid_url


def test_extract_urls_with_relative_paths():
    base_url = "https://example.com/docs"
    html = """
    <html>
        <body>
            <a href="/swift-protobuf">Link 1</a>
            <a href="swift-protobuf">Link 2</a>
            <a href="./swift-protobuf">Link 3</a>
            <a href="../swift-protobuf">Link 4</a>
            <a href="//example.com/swift-protobuf">Link 5</a>
        </body>
    </html>
    """
    
    urls = extract_urls(html, base_url)
    expected = {
        "https://example.com/swift-protobuf",  # from /swift-protobuf
        "https://example.com/docs/swift-protobuf",  # from swift-protobuf
        "https://example.com/docs/swift-protobuf",  # from ./swift-protobuf
        "https://example.com/swift-protobuf",  # from ../swift-protobuf
        "https://example.com/swift-protobuf",  # from //example.com/swift-protobuf
    }
    
    assert urls == expected


def test_is_valid_url():
    # Test valid URLs
    assert is_valid_url("https://example.com/page")
    assert is_valid_url("https://example.com/page.html")
    assert is_valid_url("https://example.com/page.php")
    
    # Test invalid URLs
    assert not is_valid_url("https://example.com/style.css")
    assert not is_valid_url("https://example.com/script.js")
    assert not is_valid_url("https://example.com/image.jpg")
    
    # Test with prefix
    assert is_valid_url(
        "https://example.com/page",
        url_prefix="https://example.com"
    )
    assert not is_valid_url(
        "https://other.com/page",
        url_prefix="https://example.com"
    ) 