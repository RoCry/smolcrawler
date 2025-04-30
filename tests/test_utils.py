from smolcrawler.utils import extract_urls, get_default_url_prefix, is_valid_url


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


def test_specific_url_in_html():
    base_url = "https://mailarchive.ietf.org/arch/msg/oauth/XOEXkQVHDG6u_5ChUf6s4LxqA8M/"
    html = """
    <html>
        <body>
            <a href="https://official-name" rel="nofollow">https://official-name</a>
        </body>
    </html>
    """

    urls = extract_urls(html, base_url)
    print(urls)
    assert urls == {"https://official-name"}


def test_get_default_url_prefix():
    # Test case 1: IETF mail archive URL
    url1 = "https://mailarchive.ietf.org/arch/msg/oauth/I5dbO7j8KGbhgNhpJgTPAYdAg1w/"
    assert get_default_url_prefix(url1) == "https://mailarchive.ietf.org"

    # Test case 2: Greptime docs URL
    url2 = "https://docs.greptime.com/enterprise/overview/"
    assert get_default_url_prefix(url2) == "https://docs.greptime.com"

    # Additional test cases for robustness
    # Test case 3: URL with no path
    url3 = "https://example.com"
    assert get_default_url_prefix(url3) == "https://example.com"

    # Test case 4: URL with query parameters
    url4 = "https://example.com/path?query=value"
    assert get_default_url_prefix(url4) == "https://example.com"
