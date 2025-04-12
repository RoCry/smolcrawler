
from smolcrawler.utils import extract_urls, is_valid_url


def test_extract_urls_with_relative_paths():
    base_url = "https://example.com/docs"
    html = """
    <html>
        <body>
            <a href="/swift-protobuf">Link 1</a>  <!-- root-relative -->
            <a href="swift-protobuf">Link 2</a>   <!-- relative to current path -->
            <a href="./swift-protobuf">Link 3</a> <!-- same as above -->
            <a href="../swift-protobuf">Link 4</a> <!-- parent path -->
        </body>
    </html>
    """

    urls = extract_urls(html, base_url)

    # Expected behavior:
    # 1. /swift-protobuf -> https://example.com/swift-protobuf
    # 2. swift-protobuf -> https://example.com/docs/swift-protobuf
    # 3. ./swift-protobuf -> https://example.com/docs/swift-protobuf
    # 4. ../swift-protobuf -> https://example.com/swift-protobuf
    expected = {
        "https://example.com/swift-protobuf",
        "https://example.com/docs/swift-protobuf",
    }

    assert urls == expected, f"Expected {expected}, got {urls}"


def test_is_valid_url():
    # Test valid URLs
    assert is_valid_url("https://example.com/page")
    assert is_valid_url("https://example.com/page/")
    assert is_valid_url("https://example.com/page.html")
    assert is_valid_url("https://example.com/page.php")

    # Test invalid URLs
    assert not is_valid_url("https://example.com/style.css")
    assert not is_valid_url("https://example.com/script.js")
    assert not is_valid_url("https://example.com/image.jpg")

    # Test with prefix
    assert is_valid_url("https://example.com/page", url_prefix="https://example.com")
    assert not is_valid_url("https://other.com/page", url_prefix="https://example.com")
