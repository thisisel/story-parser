import datetime

from pydantic import BaseModel, HttpUrl, ValidationError, validator
from requests.models import HTTPError
from requests_html import HTML, AsyncHTMLSession, HTMLSession

known_domains = {"americanliterature.com"}


class SourceUrl(BaseModel):
    url: HttpUrl

    @validator("url", always=True)
    def check_url(cls, v):
        if v.host not in known_domains:
            raise ValidationError("unknown domain")
        return v


def save_page(page_text: str, filename: str) -> None:
    """I/O bound task
        saves web page with html elements to
        .html file

    Args:
        page_text (str): [description]
        filename (str): [description]
    """

    with open(f"{filename}.html", "w") as f:
        f.write(page_text)


def get_html_filename(url: HttpUrl = None, filename: str = None):

    if filename is None:
        filename = f"{datetime.datetime.now()}"
        if url is not None:
            filename = f"{url.host}" + filename

    return filename


def get_text_filename(title: str = None, author: str = None):

    filename = f"({datetime.datetime.now()}"
    if author:
        filename = author + filename
    if title:
        filename = title + filename

    return filename


def get_page(url: str) -> str:
    """Download web page

    Args:
        url ([type]):

    Raises:
        HTTPError:

    Returns:
        str: html page in text form
    """
    session = HTMLSession()
    response = session.get(url)

    if response.status_code == 200:
        return response.text

    raise HTTPError(response)


def get_html(r_text):
    r_html = HTML(html=r_text)


def extract_elements(r_html):

    paragraphs = extract_paragraphs(r_html)
    meta = extract_meta(r_html)

    return paragraphs, meta


def extract_paragraphs(r_html):

    ps = r_html.find("p")
    return ps


def extract_meta(r_html):
    ...


def save_scrape_content(ps, filename: str = "raw") -> None:

    print(f"total ps {len(ps)}")
    for i, el in enumerate(ps):

        with open(f"{filename}.txt", "a") as f:
            if el.attrs or el.find("a"):
                continue
            if el.text:
                print(f"{i}: {el.text}")
                f.write(f"{el.text}")


if __name__ == "__main__":

    url = input("please enter url\n")
    url_obj = SourceUrl(url="https://americanliterature.com/")
    filename = get_html_filename(url=url_obj.url)
    r_text = get_page(
        url=url
    )
    save_page(page_text=r_text)
    r_html = HTML(html=r_text)
    # paragraphs, _ = extract_elements(r_html)
    paragraphs = extract_paragraphs(r_html)
    save_scrape_content(ps=paragraphs)
