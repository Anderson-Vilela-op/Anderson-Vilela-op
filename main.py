from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from xml.dom import minidom
import os

HEADERS = {'authorization': 'token '+ os.environ['ACCESS_TOKEN']}


def my_year_diff(my_year):
    diff_year = relativedelta(datetime.today(), my_year)
    return "{} {}, {} {}, {} {}{}".format(
        diff_year.years,
        format_plural(diff_year.years, "ano", "anos"),
        diff_year.months,
        format_plural(diff_year.months, "mês", "meses"),
        diff_year.days,
        format_plural(diff_year.days, "dia", "dias"),
        " 🎂" if (diff_year.months == 0 and diff_year.days == 0) else "",
    )

def format_plural(unit, single, plural):
    if unit == 1:
        return f"{single}"
    else:
        return f"{plural}"

def count_repositories(username):
    try:
        res = requests.get(f"https://api.github.com/users/{username}/repos")
        if res.status_code == 200:
            repositories = res.json()
            return len(repositories)
        else:
            return f"Erro: {res.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

def count_starts(username):
    res = requests.get(f'https://api.github.com/users/{username}/starred')
    if res.status_code == 200:
        data = res.json()
        return len(data)
    else:
        return None

def count_commits(username, token):
    headers = {"Authorization": f"token {token}"}
    try:
        repositories_response = requests.get(
            f"https://api.github.com/users/{username}/repos", headers=headers
        )
        if repositories_response.status_code != 200:
            return f"Erro ao obter a lista de respositorios: {repositories_response.status_code}"
        total_commits = 0

        for repo in repositories_response.json():
            repo_name = repo["name"]
            commits_response = requests.get(
                f"https://api.github.com/repos/{username}/{repo_name}/commits",
                headers=headers,
            )
            if commits_response.status_code != 200:
                return f"Erro ao obter os commits do repositorio  {repo_name}: {commits_response.status_code}"
            total_commits += len(commits_response.json())
        return total_commits
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

def svg_overwrite(filename, age_data, repo_data, commit_data, contrib_data, starts_data):
  
    svg = minidom.parse(filename)
    f = open(filename, mode='w', encoding='utf-8')
    tspan = svg.getElementsByTagName('tspan')
    tspan[30].firstChild.data = age_data
    tspan[59].firstChild.data = repo_data
    tspan[61].firstChild.data = contrib_data
    tspan[63].firstChild.data = commit_data
    tspan[65].firstChild.data = starts_data

    # for index, elm in enumerate(tspan):
    #     print(f'O indice: {index}')
    #     print("Conteúdo da tag <tspan> no índice", elm.firstChild.data)
    
    #tspan[73].firstChild.data = loc_data[2]
    #tspan[74].firstChild.data = loc_data[0] + '++'
    #tspan[75].firstChild.data = loc_data[1] + '--'
    f.write(svg.toxml('utf-8').decode('utf-8'))
    f.close()


def count_contributions(username, token):
        headers = {'Authorization': f'token {token}'}
        try:
            commits_response = requests.get(f'https://api.github.com/users/{username}/events', headers=headers)
            if commits_response.status_code != 200:
                return f"Erro ao obter os eventos do usuário: {commits_response.status_code}"

            total_commits = 0
            for event in commits_response.json():
                if event['type'] == "PushEvent":
                    total_commits += len(event['payload']['commits'])

            pull_requests_response = requests.get(f'https://api.github.com/search/issues?q=author:{username}+is:pr', headers=headers)
            if pull_requests_response.status_code != 200:
                return f"Erro ao obter os pull requests do usuário: {pull_requests_response.status_code}"

            total_pull_requests = pull_requests_response.json()['total_count']

            reviews_response = requests.get(f'https://api.github.com/search/issues?q=review-requested:{username}', headers=headers)
            if reviews_response.status_code != 200:
                return f"Erro ao obter as revisões de código do usuário: {reviews_response.status_code}"

            total_reviews = reviews_response.json()['total_count']

            total_contributions = total_commits + total_pull_requests + total_reviews
            return total_contributions

        except requests.exceptions.RequestException as e:
            return f"Erro de conexão: {e}"


if __name__ == '__main__':
    age = my_year_diff(datetime(2002, 6, 4))
    commits = count_commits("AndersonVilela", HEADERS)
    repositories = count_repositories("AndersonVilela") 
    contrib = count_contributions("AndersonVilela", HEADERS)
    stars = count_starts('AndersonVilela')

    svg_overwrite('assets/dark_mode.svg', age, repositories, commits, contrib, stars)


