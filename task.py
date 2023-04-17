from bs4 import BeautifulSoup
import requests


def get_html_source(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_source = response.content
        return html_source
    else:
        print(f'Request failed with status code {response.status_code}')
        return None


def extract_data_from_row(tr):
    data = {}
    number_elem = tr.find('td', {'class': 'number'})
    
    if number_elem is not None:
        data['number'] = number_elem.find('a').text.strip()
    else:
        data['number'] = None

    logo_elem = tr.find('td', {'class': 'trademark image'})
    if logo_elem is not None and logo_elem.find('img') is not None:
        data['logo_url'] = logo_elem.find('img')['src']
    else:
        data['logo_url'] = None

    name_elem = tr.find('td', {'class': 'trademark words'})
    if name_elem is not None:
        data['name'] = name_elem.text.strip()
    else:
        data['name'] = None

    classes_elem = tr.find('td', {'class': 'classes'})
    if classes_elem is not None:
        data['classes'] = classes_elem.text.strip()
    else:
        data['classes'] = None

    status_elem = tr.find('td', {'class': 'status'})
    if status_elem is not None:       
        status = status_elem.text.strip()
        status = status.replace('●', '')
        status = status.replace('\n', '')

        if len(status.split(' - ')) > 1:
            data['status1'] = status.split(' - ')[0]
            data['status2'] = status.split(' - ')[1]
        else:
            data['status1'] = status
            data['status2'] = None
    else:
        data['status1'] = None
        data['status2'] = None

    details_elem = tr.find('td', {'class': 'number'})
    if details_elem is not None and details_elem.find('a') is not None:
        data['details_page_url'] = base_url + details_elem.find('a')['href']
    else:
        data['details_page_url'] = None

    return data


def extract_data_from_html(soup):    
    results = []

    for tr in soup.select('tr[class*="mark-line result"]'):
        data = extract_data_from_row(tr)
        results.append(data)

    return results


def check_no_results(soup):
    no_results_elem = soup.find('div', {'class': 'no-content'})
    if no_results_elem is not None and 'You have no results.' in no_results_elem.text:
        return True
    else:
        return False
    

def write_results_to_file(all_pages_results):
    with open('my_file.txt', 'w') as f:
        for item in all_pages_results:
            f.write("%s\n" % item)    
    

def get_all_results(url):
    all_pages_results = []
    page_number = 0

    while True:
        html_source = get_html_source(f'{url}&p={page_number}')

        if html_source is None:
            break

        soup = BeautifulSoup(html_source, 'html.parser')

        print(page_number)

        # detects end of pagination
        if check_no_results(soup):
            break

        current_page_results = extract_data_from_html(soup)
        all_pages_results.extend(current_page_results)

        page_number += 1

    return all_pages_results



base_url = 'https://search.ipaustralia.gov.au'
url = base_url + '/trademarks/search/result?s=914df9d3-8cbe-4665-888b-81680d516277'
all_pages_results = get_all_results(url)
write_results_to_file(all_pages_results)
