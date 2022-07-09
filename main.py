import os, questionary, requests, re
from bs4 import BeautifulSoup, NavigableString
from plumbum import cli

def clear_screen():
    """
    Clears the screen
    """
    os.system('cls' if os.name == 'nt' else 'clear')

class MALHelper(cli.Application):
    VERSION = '1.0'
    search = cli.SwitchAttr(['s', 'search'], help='Searches MyAnimeList for the provided query and displays a list of top 50 search results')
    trending =  cli.Flag(['t', 'trending'], help='Displays a list of top 50 trending anime from MyAnimeList')
    airing =  cli.Flag(['a', 'airing'], help='Displays a list of top 50 currently airing anime from MyAnimeList')
    upcoming =  cli.Flag(['u', 'upcoming'], help='Displays a list of top 50 upcoming anime from MyAnimeList')

    def show_anime_info(self, anime_list, anime_index):
        """
        Shows info about an anime scraped from MyAnimeList
        """
        selected_anime = anime_list[int(anime_index)]
        anime_page_url = selected_anime.select('td:nth-of-type(2) a')[0]['href']
        response = requests.get(anime_page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        name = soup.select('h1.title-name strong')[0].text

        info = '\n'.join(
            info_piece.span.text + ' ' + ' '.join(
                tag.text.strip() 
                for tag in info_piece.contents[2:] 
                if isinstance(tag, NavigableString) or (not tag.has_attr('style') or not 'display: none' in tag['style'])
            ) 
            for info_piece in soup.find('h2', text='Information').find_next_siblings('div', class_='spaceit_pad')[:14]
        ).replace('  ', ' ').replace(' , ', ', ')

        stats = '\n'.join(
            (
                stat_piece.span.text +  ' '.join(
                    tag.text.strip() 
                    for tag in stat_piece.contents
                    if (tag.name == 'span' and tag.has_attr('class') and 'score-label' in tag['class']) or isinstance(tag, NavigableString)
                )
            ).replace('  ', ' ')
            for stat_piece in soup.find('h2', text='Statistics').find_next_siblings('div', class_='spaceit_pad')[:5]
        )

        synopsis = soup.find('p', attrs={ 'itemprop': 'description' }).text
        while True:
            clear_screen()
            questionary.print(f'Page URL: {anime_page_url}\nName: {name}\n{info}\n{stats}\nSynopsis:\n{synopsis}\n', style='fg:blue')
            choice = questionary.select(
                'Select an option:',
                choices=[
                    'See recommedations based on this anime',
                    'Go back to the previous page',
                    'Show main menu',
                    'Quit'
                ]
            ).ask()
            if choice == 'Quit':
                clear_screen()
                exit()
            elif choice == 'Show main menu':
                clear_screen()
                return True
            elif choice == 'Go back to the previous page':
                clear_screen()
                return False
            else:
                show_main_menu = self.recommend_anime(anime_list, anime_index)
                if show_main_menu:
                    return True

    def recommend_anime(self, anime_list, anime_index):
        """
        Shows reccomendations based on an anime scraped from MyAnimeList
        """
        selected_anime = anime_list[int(anime_index)]
        anime_page_url = selected_anime.select('td:nth-of-type(2) a')[0]['href']
        response = requests.get(anime_page_url+r'/userrecs')
        soup = BeautifulSoup(response.content, 'html.parser')
        
        name = soup.select('h1.title-name strong')[0].text

        recommendations = soup.select('div.borderClass td:nth-of-type(2)')
        if len(recommendations) == 0:
            questionary.print(f'No recommendations could be found based on {name} ☹.', style='bold fg:red')
            choice = questionary.select(
                'Select an option:',
                choices=[
                    'Go back to previous page',
                    'Show main menu',
                    'Quit'
                ]
            ).ask()
            if choice == 'Quit':
                clear_screen()
                exit()
            elif choice == 'Show main menu':
                clear_screen()
                return True
            elif choice == 'Go back to previous page':
                clear_screen()
                return False
        else:
            iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
            while True:
                clear_screen()
                questionary.print(f'Anime recommendations based on {name}:\n\n', style='bold fg:darkgreen')
                for index, recommendation in enumerate(recommendations):
                    recommendation_name = recommendation.select('div:nth-of-type(2) a')[0].text.strip()

                    recommendation_text = ' '.join(
                        content_piece.text.strip()
                        for content_piece in recommendation.find(class_='spaceit_pad detail-user-recs-text').contents
                        if content_piece.name != 'a'
                    ) 
                    
                    recommender_name = ' '.join(
                        content_piece.text.strip() 
                        for content_piece in recommendation.find(class_='spaceit_pad detail-user-recs-text').next_sibling.next_sibling.contents[2:]
                    )
                    questionary.print(f'Index: {index+1}\nName: {recommendation_name}\n{recommendation_text}\n{recommender_name}\n', style='fg:blue')
                    
                    if index == len(recommendations)-1:
                        questionary.print(f'\nThose were the top {index+1} recommendations based on {name}!', style='bold fg:darkgreen')
                        choice = questionary.select(
                            'Select an option:',
                            choices=[
                                'Show more info about an anime',
                                'Go to previous page',
                                'Show main menu',
                                'Quit'
                            ]
                        ).ask()
                        if choice == 'Quit':
                            clear_screen()
                            exit()
                        elif choice == 'Show main menu':
                            clear_screen()
                            return True
                        elif choice == 'Go to previous page':
                            clear_screen()
                            return False
                        elif choice == 'Show more info about an anime':
                            recommendation_index = int(
                                questionary.text(
                                'Enter the index of the anime recommendation: ', 
                                validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= int(index)+1 else 'Please enter a valid index.'
                                ).ask()
                            )
                            clear_screen()
                            show_main_menu = self.show_anime_info(recommendations, recommendation_index-1) # We've put recommendation_index-1 instead of recommendation_index because this function accepts the index of the anime which is one less than the anime's rank  
                            if show_main_menu:
                                return True
                            else:
                                clear_screen()
                                iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                                break
                        iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                        break
                    if iteration_options['constant_iteration'] and iteration_options['constant_iteration_till_index'] == index:
                        iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
                    if not iteration_options['constant_iteration'] and index > 0 and (index+1)%5 == 0:
                        choice = questionary.select(
                            'Select an option:',
                            choices=[
                                'Display more anime recommendations',
                                'Show more info about an anime',
                                'Go back to previous page',
                                'Show main menu',
                                'Quit'
                            ]
                        ).ask()
                        if choice == 'Quit':
                            clear_screen()
                            exit()
                        elif choice == 'Show main menu':
                            clear_screen()
                            return True
                        elif choice == 'Go back to previous page':
                            clear_screen()
                            return False
                        elif choice == 'Show more info about an anime':
                            recommendation_index = int(
                                questionary.text(
                                'Enter the index of the anime recommendation: ', 
                                validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= int(index)+1 else 'Please enter a valid index.'
                                ).ask()
                            )
                            clear_screen()
                            self.show_anime_info(recommendations, recommendation_index-1) # We've put recommendation_index-1 instead of recommendation_index because this function accepts the index of the anime which is one less than the anime's rank  
                            clear_screen()
                            iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                            break

    def search_anime(self, query):
        """
        Shows a list of anime scraped from MyAnimeList based on a search query
        """
        url = f'https://myanimelist.net/anime.php?q={requests.utils.quote(query)}&cat=anime'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        all_anime_container = soup.find(class_='js-categories-seasonal js-block-list list')
        all_anime = all_anime_container.find_all('tr')
        iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
        while True:
            for index, anime in enumerate(all_anime):
                if index > 0:
                    name = anime.select('div.title strong')[0].text
                    score = anime.select('td:nth-of-type(5)')[0].text.strip()
                    info = f"{anime.select('td:nth-of-type(3)')[0].text.strip()}, {anime.select('td:nth-of-type(4)')[0].text.strip()} episode(s)"
                    questionary.print(f'Index: {index}\nName: {name}\nScore: {score}\nMore information: {info}\n', style='fg:blue')
                    if index == len(all_anime)-1:
                        questionary.print(f'\nThose were the top {index} search results for your query!', style='bold fg:darkgreen')
                        choice = questionary.select(
                            'Select an option:',
                            choices=[
                                'Show more info about an anime',
                                'Go to previous page',
                                'Show main menu',
                                'Quit'
                            ]
                        ).ask()
                        if choice == 'Quit':
                            clear_screen()
                            exit()
                        elif choice == 'Show main menu':
                            clear_screen()
                            return True
                        elif choice == 'Go to previous page':
                            clear_screen()
                            return False
                        elif choice == 'Show more info about an anime':
                            anime_index = int(
                                questionary.text(
                                'Enter the index of the anime: ', 
                                validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= index else 'Please enter a valid index.'
                                ).ask()
                            )
                            clear_screen()
                            self.show_anime_info(all_anime, anime_index)
                            clear_screen()
                            iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                            break
                    if iteration_options['constant_iteration'] and iteration_options['constant_iteration_till_index'] == index:
                        iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
                    if not iteration_options['constant_iteration'] and (index)%5 == 0:
                        choice = questionary.select(
                            'Select an option:',
                            choices=[
                                'Display more anime',
                                'Show more info about an anime',
                                'Go to previous page',
                                'Show main menu',
                                'Quit'
                            ]
                        ).ask()
                        if choice == 'Quit':
                            clear_screen()
                            exit()
                        elif choice == 'Show main menu':
                            clear_screen()
                            return True
                        elif choice == 'Go to previous page':
                            clear_screen()
                            return False
                        elif choice == 'Show more info about an anime':
                            anime_index = int(
                                questionary.text(
                                'Enter the index of the anime: ', 
                                validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= index else 'Please enter a valid index.'
                                ).ask()
                            )
                            clear_screen()
                            show_main_menu = self.show_anime_info(all_anime, anime_index)
                            if show_main_menu:
                                clear_screen()
                                return True
                            else:
                                clear_screen()
                                iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                                break

    def top_anime(self, page_url, top_anime_type):
        """
        Shows a list of top anime depending on the type specified (trending, airing, or upcoming) scraped from MyAnimeList.
        """
        response = requests.get(page_url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        all_anime = soup.find_all(class_='ranking-list')
        iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
        while True:
            clear_screen()
            questionary.print(f'Top 50 {top_anime_type} anime on MyAnimeList:\n\n', style='bold fg:darkgreen')
            for index, anime in enumerate(all_anime):
                ranking = anime.find(class_='rank').find('span').text
                name = anime.find(class_='clearfix').text.strip()
                score = anime.find('span', class_='score-label').text
                info = re.sub(' +', ' ', ', '.join(anime.find(class_='information').text.strip().split('\n')[:2]))
                questionary.print(f'Rank: {ranking}\nName: {name}\nScore: {score}\nMore info: {info}\n', style='fg:blue')
                if int(ranking) == 50:
                    questionary.print(f'\nThose were the top 50 {top_anime_type} anime on MyAnimeList!', style='bold fg:darkgreen')
                    choice = questionary.select(
                        'Select an option:',
                        choices=[
                            'Show more info about an anime',
                            'Show main menu',
                            'Quit'
                        ]
                    ).ask()
                    if choice == 'Quit':
                        clear_screen()
                        exit()
                    elif choice == 'Show main menu':
                        clear_screen()
                        return True
                    elif choice == 'Show more info about an anime':
                        anime_rank = int(
                            questionary.text(
                            'Enter the rank of the anime: ', 
                            validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= int(ranking) else 'Please enter a valid index.'
                            ).ask()
                        )
                        clear_screen()
                        show_main_menu = self.show_anime_info(all_anime, anime_rank-1) # We've put anime_rank-1 instead of anime_rank because this function accepts the index of the anime which is one less than the anime's rank  
                        if show_main_menu:
                            clear_screen()
                            return True
                        else:
                            clear_screen()
                            iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                            break
                if iteration_options['constant_iteration'] and iteration_options['constant_iteration_till_index'] == index:
                    iteration_options = { 'constant_iteration': False, 'constant_iteration_till_index': 0 }
                if not iteration_options['constant_iteration'] and index > 0 and (index+1)%5 == 0:
                    choice = questionary.select(
                        'Select an option:',
                        choices=[
                            'Display more anime',
                            'Show more info about an anime',
                            'Show main menu',
                            'Quit'
                        ]
                    ).ask()
                    if choice == 'Quit':
                        clear_screen()
                        exit()
                    elif choice == 'Show main menu':
                        clear_screen()
                        return True
                    elif choice == 'Show more info about an anime':
                        anime_rank = int(
                            questionary.text(
                            'Enter the rank of the anime: ', 
                            validate=lambda user_input: True if user_input.isnumeric() and 0 < int(user_input) <= int(ranking) else 'Please enter a valid index.'
                            ).ask()
                        )
                        clear_screen()
                        show_main_menu = self.show_anime_info(all_anime, anime_rank-1) # We've put anime_rank-1 instead of anime_rank because this function accepts the index of the anime which is one less than the anime's rank  
                        if show_main_menu:
                            clear_screen()
                            return True
                        else:
                            clear_screen()
                            iteration_options = { 'constant_iteration': True, 'constant_iteration_till_index': index }
                            break

    def top_trending_anime(self):
        """
        Shows a list of top trending anime scraped from MyAnimeList.
        """
        self.top_anime('https://myanimelist.net/topanime.php', 'trending')

    def top_upcoming_anime(self):
        """
        Shows a list of top upcoming anime scraped from MyAnimeList.
        """
        self.top_anime('https://myanimelist.net/topanime.php?type=upcoming', 'upcoming')

    def top_airing_anime(self):
        """
        Shows a list of top airing anime scraped from MyAnimeList.
        """
        self.top_anime('https://myanimelist.net/topanime.php?type=airing', 'airing')

    def main(self):
        if self.search:
            self.search_anime(self.search)
        elif self.trending:
            self.top_trending_anime()
        elif self.airing:
            self.top_airing_anime()
        elif self.upcoming:
            self.top_upcoming_anime()
        else:
            while True:
                choice = questionary.select(
                    'Select an option:',
                    choices=[
                        'Search for anime',
                        'Show top 50 trending anime',
                        'Show top 50 airing anime',
                        'Show top 50 upcoming anime',
                        'Quit'
                    ]
                ).ask()
                if choice == 'Search for anime':
                    query = questionary.text('Enter a search query: ').ask()
                    self.search_anime(query)
                elif choice == 'Show top 50 trending anime':
                    self.top_trending_anime()
                elif choice == 'Show top 50 airing anime':
                    self.top_airing_anime()
                elif choice == 'Show top 50 upcoming anime':
                    self.top_upcoming_anime()
                else:
                    return
    
if __name__ == '__main__':
    MALHelper()