from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import argparse

def crawler(firsturl):
    #url filter function
    def filter(url):
        #video file
        if (url.endswith('flv') or url.endswith('mp4') or url.endswith('wmv') or url.endswith('avi')):
            return 0
        #image file
        elif (url.endswith('jpg') or url.endswith('JPG') or url.endswith('png') or url.endswith('gif')):
            return 0
        #other file
        elif (url.endswith('pdf') or url.endswith('doc') or url.endswith('docx') or url.endswith('ppt') or url.endswith('zip') or url.endswith('rar')):
            return 0
        else:
            return 1

    # default url in queue
    new_urls = deque([firsturl])

    # all of urls that I have already crawled
    processed_urls = set()

    while len(new_urls):

        # move next url from the queue to the set of processed urls
        url = new_urls.popleft()
        # url filter
        analyze = filter(url)
        if(analyze == 1):
            processed_urls.add(url)

            # extract base url to resolve relative links
            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url
            print("crawling %s" % url)

            try:
                #put the web info into response(dont redirect when occur redirect)
                response = requests.get(url, allow_redirects=False)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                # ignore errors pages
                continue
            # find out all email addresses with regular expression and add them into the new_emails
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            # write e-mail log into log.txt
            f = open("maillist.txt","a+")

            for value in new_emails:
                print(value)
                f.write(repr(value))
                f.write("\n")

            # BeautifulSoup the html document
            soup = BeautifulSoup(response.text,"lxml")

            # find all anchors in the html document
            for anchor in soup.find_all("a"):
                # extract the link in href attribute's value
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                # resolve relative links
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                # dont't crawl repeated url
                if not link in new_urls and not link in processed_urls:
                    new_urls.append(link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='It is a e-mail crawler.')
    parser.add_argument('url', help='the url you want to crawl.')
    arg = parser.parse_args()
    crawler(arg.url)