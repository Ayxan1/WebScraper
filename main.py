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
    data['number'] = number_elem.find('a').text.strip() if number_elem else None

    logo_elem = tr.find('td', {'class': 'trademark image'})
    data['logo_url'] = logo_elem.find('img')['src'] if logo_elem and logo_elem.find('img') else None

    name_elem = tr.find('td', {'class': 'trademark words'})
    data['name'] = name_elem.text.strip() if name_elem else None

    classes_elem = tr.find('td', {'class': 'classes'})
    data['classes'] = classes_elem.text.strip() if classes_elem else None

    status_elem = tr.find('td', {'class': 'status'})
    if status_elem:
        status = status_elem.text.strip().replace('●', '').replace('\n', '')
        data['status1'], data['status2'] = status.split(' - ') if len(status.split(' - ')) > 1 else (status, None)
    else:
        data['status1'], data['status2'] = None, None

    details_elem = tr.find('td', {'class': 'number'})
    data['details_page_url'] = base_url + details_elem.find('a')['href'] if details_elem and details_elem.find('a') else None

    return data


def extract_data_from_html(soup):    
    results = []

    for tr in soup.select('tr[class*="mark-line result"]'):
        data = extract_data_from_row(tr)
        results.append(data)

    return results


def check_no_results(soup):
    no_results_elem = soup.find('div', {'class': 'no-content'})
    return True if no_results_elem and 'You have no results.' in no_results_elem.text else False
    

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

        # Detect end of pagination
        if check_no_results(soup):
            break

        current_page_results = extract_data_from_html(soup)
        all_pages_results.extend(current_page_results)

        page_number += 1

    return all_pages_results


base_url = 'https://search.ipaustralia.gov.au'
url = f'{base_url}/trademarks/search/result?s=914df9d3-8cbe-4665-888b-81680d516277'
all_pages_results = get_all_results(url)
write_results_to_file(all_pages_results)
