import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import base64
import os


class CpuData:

    def __attr_init__(self):
        #Source
        self.url = ''
        self.plain_html = ''
        self.soup_html = None

        #Properties
        self.cpu_properties = {
            'cpu_name': '',
            'cpu_logo': '',
            'socket': '',
            'foundry': '',
            'process_size': '',
            'transistors': '',
            'die_size': '',
            'package': '',
            'tcasemax': '',
            'frequency': '',
            'turbo_clock': '',
            'base_clock': '',
            'multiplier': '',
            'multiplier_unlocked': '',
            'voltage': '',
            'tdp': '',
            'fp32': '',
            'market': '',
            'production_status': '',
            'release_date': '',
            'codename': '',
            'generation': '',
            'part_number': '',
            'memory_support': '',
            'ecc_memory': '',
            'pci_express': '',
            'cores_num': '',
            'threads_num': '',
            'smp_cpus_num': '',
            'integrated_graphics': '',
            'cache_l1': '',
            'cache_l2': '',
            'cache_l3': '',
            'features_list': [],
            'imgs': {},
            'notes': ''
        }

        self.standard_tables = ['Physical', 'Performance', 'Architecture', 'Cores', 'Cache']

        self.enum_properties = {
            'Socket:': 'socket',
            'Foundry:': 'foundry',
            'Process Size: ': 'process_size',
            'Transistors:': 'transistors',
            'Die Size:': 'die_size',
            'Package:': 'package',
            'tCaseMax:': 'tcasemax',
            'Frequency:': 'frequency',
            'Turbo Clock:': 'turbo_clock',
            'Base Clock:': 'base_clock',
            'Multiplier:': 'multiplier',
            'Multiplier Unlocked:': 'multiplier_unlocked',
            'Voltage:': 'voltage',
            'TDP:': 'tdp',
            'FP32:': 'fp32',
            'Market:': 'market',
            'Production Status:': 'production_status',
            'Release Date:': 'release_date',
            'Codename:': 'codename',
            'Generation:': 'generation',
            'Part#:': 'part_number',
            'Memory Support:': 'memory_support',
            'ECC Memory:': 'ecc_memory',
            'PCI-Express:': 'pci_express',
            '# of Cores:': 'cores_num',
            '# of Threads:': 'threads_num',
            'SMP # CPUs: ': 'smp_cpus_num',
            'Integrated Graphics:': 'integrated_graphics',
            'Cache L1: ': 'cache_l1',
            'Cache L2: ': 'cache_l2',
            'Cache L3: ': 'cache_l3'
        }

    def __init__(self, url):
        self.__attr_init__()
        self.url = urlparse(url)
        self.plain_html = self.__download_url(url)
        self.soup_html = BeautifulSoup(self.plain_html, 'html.parser')
        self.__collect_data()

    def store_data(self, path, include_headers, create_images, img_as_path):
        if include_headers and not os.path.isfile(path):
            headers = ",".join(self.cpu_properties.keys())
            with open(path, 'w') as f:
                f.write(headers + "\n")
        data = ''
        for key in self.cpu_properties:
            writed_data = False
            if key == 'cpu_logo' and img_as_path:
                data = data + '"' + 'img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' + \
                       self.cpu_properties['cpu_name'].replace(' ', '_') + '_logo.png' + '"' + ','
                writed_data = True
            if key == 'cpu_logo' and create_images:
                    if not os.path.isdir('img'):
                        os.mkdir('img')
                    if not os.path.isdir('img/'+self.cpu_properties['cpu_name'].replace(' ', '_')):
                        os.mkdir('img/'+self.cpu_properties['cpu_name'].replace(' ', '_'))
                    with open('img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' +
                              self.cpu_properties['cpu_name'].replace(' ', '_') + '_logo.png', "wb") as f:
                        f.write(base64.decodebytes(self.cpu_properties['cpu_logo']))
            if key == 'imgs' and img_as_path:
                imgs_paths = {}
                for img in self.cpu_properties[key]:
                    imgs_paths[img] = 'img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' + \
                                      self.cpu_properties['cpu_name'].replace(' ', '_') + '_' + \
                                      img.replace(' ', '_') + '.png'
                data = data + '"' + str(imgs_paths) + '"' + ','
                writed_data = True
            if key == 'imgs' and create_images:
                for img in self.cpu_properties[key]:
                    if not os.path.isdir('img'):
                        os.mkdir('img')
                    if not os.path.isdir('img/' + self.cpu_properties['cpu_name'].replace(' ', '_')):
                        os.mkdir('img/' + self.cpu_properties['cpu_name'].replace(' ', '_'))
                    with open('img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' +
                              self.cpu_properties['cpu_name'].replace(' ', '_') + '_' +
                              img.replace(' ', '_') + '.png', "wb") as f:
                        f.write(base64.decodebytes(self.cpu_properties[key][img]))
            if not writed_data:
                data = data + '"' + str(self.cpu_properties[key]) + '"' + ','
        data = data[0:-1]
        with open(path, 'a') as f:
            f.write(data + "\n")

    @staticmethod
    def __get_b64_img(url):
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'UOC Test Bot. Img downloader. lgarciatar@uoc.edu.'
            }
        )

        img = urllib.request.urlopen(req, timeout=10).read()

        b64_img = base64.b64encode(img)

        return b64_img

    def __collect_data(self):
        article = self.soup_html.find('article')
        article_div_list = article.find_all('div')
        for div in article_div_list:
            if 'class' in div.attrs:
                if 'clearfix' in div.attrs['class'] and 'images' not in div.attrs['class']:
                    for h1 in div.find_all('h1'):
                        if 'cpuname' in h1.attrs['class']:
                            self.cpu_properties['cpu_name'] = str(h1.string)
                    for img in div.find_all('img'):
                        if 'cpulogo' in img.attrs['class']:
                            self.cpu_properties['cpu_logo'] = self.__get_b64_img('{uri.scheme}://{uri.netloc}'.
                                                                                 format(uri=self.url) +
                                                                                 img.attrs['src'])
                if 'clearfix' in div.attrs['class'] and 'images' in div.attrs['class']:
                    for inner_div in div.findAll('div'):
                        if 'chip-image' in inner_div.attrs['class']:
                            src = inner_div.find('img', {"class": "chip-image--img"}).attrs['src']
                            if 'http' not in src:
                                img = self.__get_b64_img('{uri.scheme}://{uri.netloc}'.format(uri=self.url) + src)
                            else:
                                img = self.__get_b64_img(src)
                            name = str(inner_div.find('div', {"class": "chip-image--type"}).string)
                            self.cpu_properties['imgs'][name] = img
                if 'sectioncontainer' in div.attrs['class']:
                    for section in div.find_all('section'):
                        if str(section.find('h1').string) in self.standard_tables:
                            table = section.find('table')
                            for row in table.findAll('tr'):
                                th = str(row.find('th').string)
                                td = str(row.find('td').text)
                                self.cpu_properties[self.enum_properties[th]] = td.strip().replace("\n", "")\
                                    .replace("\r", "")
                        if str(section.find('h1').string) == 'Features':
                            for item in section.findAll('li'):
                                self.cpu_properties['features_list'].append(str(item.string).strip().replace("\n", ""))
                        if str(section.find('h1').string) == 'Notes':
                            text_container = section.find('td', {"class": "p"})
                            self.cpu_properties['notes'] = str(text_container.string).strip().replace("\n", "")

    @staticmethod
    def __download_url(url):
        # Descargamos contenido de la url
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'UOC Test Bot. lgarciatar@uoc.edu.'
            }
        )

        html_doc = urllib.request.urlopen(req, timeout=10).read()

        return html_doc


test = CpuData('https://www.techpowerup.com/cpu-specs/ryzen-5-3600.c2132')
test.store_data('dataset.csv', True, True, True)

test2 = CpuData('https://www.techpowerup.com/cpu-specs/a8-7680.c2120')
test2.store_data('dataset.csv', True, True, True)