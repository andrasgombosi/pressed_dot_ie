"""
MOOD.IE news site front page extractor
phase 1
"""
import os
import urllib
import re
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def log(entry):
    '''
    This is a function to write into the log file
    '''
    log_file.write("\n")
    log_file.write('%s ' % datetime.datetime.now())
    log_file.write(entry)
    log_file.flush()

def generate_wordcloud_image(inbound_text,filename):
    '''
    generates a WordCloud image
    '''
    #WORDCLOUD = WordCloud(max_font_size=50).generate(inbound_text)
    WORDCLOUD = WordCloud(max_font_size=50).generate(inbound_text)
    plt.imshow(WORDCLOUD)
    plt.axis("off")
    plt.savefig(filename)
    log("Wordcloud image %s generated " % filename)

def remove_stopwords(text):
    ret_val = ''
    word_tokens = word_tokenize(text)

    for w in word_tokens:
        if w not in STOPWORDS:
            ret_val = ret_val + ' ' + w

    log('remove_stopwords returned %s ' % ret_val)
    return ret_val


def dissect_article(child_soup, top_domain):
    '''
    separated out the handling of the contents of the main article tag, so
    it is not as cluttered. Every top domain has a different webpage structure
    '''

    #log('In dissect_article, top_domain : %s ' % top_domain)

    ret_val =''
    '''
    Irish Times specific processing logic
    '''
    if top_domain == TOP_DOMAINS['IRT']:

    #main article seems to be in an <ARTICLE> tag
        article = child_soup.find('article')

        if article is not None and article.hgroup is not None:
        #    log('2')
            # extracting header 1 from the article
            if article.hgroup.h1 is not None :
            #    log('3')
                TEXT_UNICODE = UnicodeDammit(article.hgroup.h1.string)
                TEXT = TEXT_UNICODE.unicode_markup
                ret_val = ret_val + TEXT
            if article.hgroup.h2 is not None :
            #    log('4')
                TEXT_UNICODE = UnicodeDammit(article.hgroup.h2.string)
            #    log('5')
                TEXT = TEXT_UNICODE.unicode_markup
                #log('6')
                ret_val = ret_val + TEXT

        # log("%s" % ret_val)

    '''
    Independent specific processing logic
    '''

    if top_domain == TOP_DOMAINS['IND']:

    #main article seems to be in an <ARTICLE> tag
        article = child_soup.find('article')

        if article is not None and article is not None:
            # extracting header 1 from the article
            if article.h1 is not None and article.h1.string is not None :
                TEXT_UNICODE = UnicodeDammit(article.h1.string)
                TEXT = TEXT_UNICODE.unicode_markup
                ret_val = ret_val + TEXT
                # extracting header 2 from the article
            if article.h2 is not None  and article.h2.string is not None:
                TEXT_UNICODE = UnicodeDammit(article.h2.string)
                TEXT = TEXT_UNICODE.unicode_markup
                ret_val = ret_val + TEXT

    '''
    Irish Examiner specific processing logic
    '''

    if top_domain == TOP_DOMAINS['IEX']:

    #main article seems to be in an <ARTICLE> tag
        article = child_soup.find("title")
        ret_val = article.string
        ret_val = re.sub('| Irish Examiner$', '', ret_val)

    ret_val = ret_val.lower()
    # Eliminating common keywords
    for key, replacement in STR_REPLACEMENT_DICT:
        ret_val = ret_val.replace( key, replacement )

        #log("Returning %s" % ret_val)

    return ret_val

def has_class_but_no_id(tag):
    '''
    this function is to be passed to the find_all()
    BeautifulSoup function to only retrieve P tags
    '''
    return tag.has_attr('class') and not tag.has_attr('id')

def cleanse_href(href_str, top_domain):
    """
    Function to sort out the different href parsing methods
    and generate a meaningful URL's to follow
    """
    ret_val = True

    try:
        # getting rid of empties and white spaces
        href_str = href_str.strip()
    except AttributeError:
        ret_val = False

# getting rid of single digit , typically # hrefs
    if ret_val and len(href_str) > 1:
        ret_val = href_str
    else:
        ret_val = False

# converting to unicode
    if ret_val:
        href_str_unicode = UnicodeDammit(href_str)
        href_str = (href_str_unicode.unicode_markup)

# domain specific
    if ret_val and top_domain == TOP_DOMAINS['IRT']:
        # irish times puts a counter or a version number at the end
        # of their article pages, like 1.255698, so quick regexp
        # also, putting back the top domain to deliver full URL for irish times

        if re.search(r'\.[0-9]{3,5}', href_str):
            ret_val = TOP_DOMAIN + href_str
        else:
            ret_val = False

    if ret_val and top_domain == TOP_DOMAINS['IND']:
        # irish times puts a counter or a version number at the end
        # of their article pages, like 1.255698, so quick regexp
        # also, putting back the top domain to deliver full URL for irish times

        if re.search('.[0-9]{5,6}', href_str) and 'independent.ie' in href_str and 'sponsored-features' not in href_str:
            ret_val = href_str
        else:
            ret_val = False

    if ret_val and top_domain == TOP_DOMAINS['IEX']:
        # irish times puts a counter or a version number at the end
        # of their article pages, like 1.255698, so quick regexp
        # also, putting back the top domain to deliver full URL for irish times

        if re.search(r'[0-9]{3,7}\.html', href_str) and 'sponsored-content' not in href_str:
            ret_val = TOP_DOMAIN + href_str
        else:
            ret_val = False


    return ret_val

################

log_file_name = "pressed.log"
log_file = open(log_file_name,'w')

TOP_DOMAINS = {'IRT': "http://www.irishtimes.com",
               'IND': "http://www.independent.ie",
               'IEX': "http://www.irishexaminer.com"
               }

STOPWORDS = set(stopwords.words('english'))

STR_REPLACEMENT_DICT =     [('irish', ''),
                            ('ireland', ''),
                            ('dublin', ''),
                            ('examiner', ''),
                            ("n't",''),
                            ("watch",''),
                            ("video",''),
                            ("'s",'')
                            ]

os.system('cls')

FULLTEXT = ' '

for short,url in TOP_DOMAINS.items():
    TOP_DOMAIN_TEXT = ''
    log('TOP_DOMAIN_TEXT length: %d' % len(TOP_DOMAIN_TEXT))
    # get one top domain
    TOP_DOMAIN = TOP_DOMAINS[short]
    log("Working on %s" % TOP_DOMAIN)
    #scan front page
    try:
        HTML_DOC = urllib.request.urlopen(TOP_DOMAIN)
    except urllib.error.URLError:
        log("top domain %s is inaccessible" % TOP_DOMAIN )

    SOUP = BeautifulSoup(HTML_DOC, 'lxml')

    #get the URLs
    URL_LIST = []

    for link in SOUP.find_all('a'):

        # extract the hyperlink target
        href_content = link.get('href')
        # cleanse it
        href_content_clean = cleanse_href(href_content, TOP_DOMAIN)
        # and put it in a list
        if href_content_clean is not False:
            #, but only append it once
            if href_content_clean not in URL_LIST:
                URL_LIST.append(href_content_clean)

# so, at this stage I have a full list of URL's which point to actual articles

    HEADER_CONTENT = ' '

    for i in range(0, len(URL_LIST)-1):
        log("Working on %s" % URL_LIST[i])
        CHILD_DOC = urllib.request.urlopen(URL_LIST[i])
        CHILD_SOUP = BeautifulSoup(CHILD_DOC, 'lxml')

        HEADER_CONTENT = dissect_article(child_soup=CHILD_SOUP, top_domain=TOP_DOMAIN)

        TOP_DOMAIN_TEXT = TOP_DOMAIN_TEXT + remove_stopwords(HEADER_CONTENT)

    '''generate a standalone image for each of
        the major papers too beside the overall'''

    generate_wordcloud_image(inbound_text=TOP_DOMAIN_TEXT,filename= short +'.png' )
    # save it into the overall text
    FULLTEXT = FULLTEXT + TOP_DOMAIN_TEXT

        #log( "URL: %s " % URL_LIST[i])
        #log( "Header content: %s " % HEADER_CONTENT)

generate_wordcloud_image(inbound_text=FULLTEXT,filename= 'overall.png' )

#plt.show()

##########
log_file.close()
