<!-- ABOUT THE PROJECT -->
## О проекте

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Проект представляет собой сайт с дашбордами, на которых находится визуализация информации о крупных электоральных процессах в России начиная с 2003 года, полученная путем парсинга данных с сайтов ЦИК и Избиркома.

Сайт расположен по адресу:

Репозиторий содержит следующие файлы:
* **data_parsing.ipynb** Ноутбук с парсингом данных выборов с 2003 года с сайтов http://cikrf.ru/ и http://www.izbirkom.ru/
* Файлы .csv с необработанными данными, только что спарсенными с указанных выше сайтов.
* **database_making.ipynb** Ноутбук с созданием полноценной базы данных из спарсенных таблиц а также подготовкой geojson для создания карты России.
* **elections.db** Получившаяся база данных с информацией о президентских и депутатских выборов с 2003 года.
* **russia.geojson** geojson с обработанными названиями регионов России, при помощи которого можно строить карту.
* **app.py** Файл с самим приложением и функциями обработки callback'ов.
* **home.py** Домашняя страница, с которой осуществляется переход на страницы с дашбордами.
* **president.py** Дашборд с информацией о президентских выборах с 2004 года.
* **parliament.py** Дашборд с информацией о выборах в Госдуму с 2003 года.


<p align="right">(<a href="#readme-top">Наверх</a>)</p>



## Инструменты

При создании проекта использовались следующие библиотеки:

* **Pandas**
* **Plotly**
* **Dash**
* **SQLite3**
* **BeautifulSoup4**
* **requests**



## Ход работы
Работу над проектом можно разделить на три этапа: парсинг данных, создание базы данных и создание дашбордов
1. **Парсинг данных.**
2. **Создание базы данных.** Спарсенные таблички предстояло перевести в реляционный формат. Для этого получившиеся после парсинга таблички для каждых из выборов, в которых столбцами были название региона, различные данные о явке и столбцы с количеством голосов за каждого из кандидатов, а строками регионы, я перевел в две другие таблицы: таблица с информацией о ходе выборов в каждом из регионов (столбцы: регион; общее число избирателей; число избирателей, пришедших на участки (считается как число бюллетеней, выданных досрочно + число бюллетеней, выданных в день голосования + число бюллетеней, выданных вне помещения); число проголосовавших избирателей (считается как число действительных бюллетеней + число недействительных бюллетеней), год выборов) и таблица с результатами каждого из кандидатов в каждом из регионов (столбцы: кандидат; регион; количество голосов за кандидата; год выборов). После этого я объединил все таблицы, получившиеся для каждых из выборов и сформировал базу данных из следующих таблиц: таблица с названиями регионов и присвоенными им id, две аналогичные таблицы для всех кандидатов в президенты и партий-кандидатов в Госдуму соответственно за весь рассматриваемый период, две таблицы с информацией о ходе президентских и депутатских выборов соответственно в регионах за все годы и две таблицы с информацией о результатах кандидатов в президенты и партий-кандидатов в Госдуму соответственно в регионах за все рассматриваемые годы.
3. **Создание дашбордов.** После создания базы данных настало время подсчитывания интересной статистики и ее визуализации. Процесс работы заключался в придумывании как можно более интересных SQL-запросов, способных предоставить нам наиболее интересные и неочевидные инсайты на основе имеющихся данных. Запросы писались на SQLite3 прямо в Python и визуализировались при помощи plotly. После построения всех графиков, началась долгая и упорная борьба с языком html, в результате которой была сделана красивая верстка сайта.

<!-- USAGE EXAMPLES -->
## Использование

Сайт: 

Проект представляет собой сайт с двумя страницами, на которых расположены два дашборда с визуализацией статистики по президентским и депутатским выборам с 2003 года соответственно. Оба дашборда аналогичны по своей структуре: на странице расположена кликабельная карта России, по клику на которую можно выбрать интересующий регион, настроить отображение регионов в виде тепловой карты явки или голосов за одного из кандидатов, выпадающие списки с годом выборов, рассматриваемым регионом (можно выбрать всю Россию) и способом отображения регионов на карте, круговые диаграммы с информацией о результатах выборов и явке в выбранном регионе в выбранный год, межрегиональные показатели явки в выбранный год, региональные предпочтения, статистику по кандитатам.





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
