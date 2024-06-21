## FunctionDef get_page_title(url)
 **get_page_title**: The function of get_page_title is to fetch and return the title of a web page given its URL.

**parameters**: The parameters of this Function.
· url: The URL of the web page from which to fetch the title. It should be a string representing a valid web address.

**Code Description**: The description of this Function.
The function `get_page_title` takes a single argument, `url`, which is expected to be a string representing the URL of a web page. The function uses the `requests` library to send an HTTP GET request to the provided URL. If the request is successful and the response status code is in the 2xx range, the function proceeds to parse the HTML content of the response using the `BeautifulSoup` library. It specifically looks for the `<title>` tag in the HTML and extracts its text content, which is then returned as the title of the web page.

If there is any issue with the request (such as a network problem or a non-2xx status code), the function catches the `requests.RequestException` and prints an error message indicating the problem. In such cases, the function returns `None`.

**Note**: Points to note about the use of the code
- Ensure that the `requests` and `BeautifulSoup` libraries are installed and imported before using this function.
- The function handles basic network errors and HTTP errors (4xx, 5xx) but may not handle all possible exceptions that could occur during the request or parsing process.
- The function assumes that the web page has a `<title>` tag; if the page does not, an attribute error may occur.

**Output Example**: Mock up a possible appearance of the code's return value.
If the URL "https://www.example.com" is provided, and the web page's title is "Example Domain", the function would return:
```
"Example Domain"
```
If there is an error fetching the URL, the function would return:
```
None
```
