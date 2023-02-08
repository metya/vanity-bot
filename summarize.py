from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from contextlib import suppress
from requests import get

def get_paper_desc(id_paper: str) -> tuple | None:
    request = get(f'https://arxiv.org/abs/{id_paper}')
    if request.ok:
        soup = BeautifulSoup(request.content, features="lxml")
        with suppress(TypeError): 
            url = soup.find('meta', property='og:url').get('content')
            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content').replace('\n', ' ')
            return url, title, description
    return None

async def get_summary(url: str = "https://arxiv.org/abs/2102.12092v2") -> str:
    url = url.replace("abs", "pdf")
    async_session = AsyncHTMLSession()
    async_response = await async_session.get(f"https://labs.kagi.com/ai/sum?url={url}.pdf")
    await async_response.html.arender(sleep=5)
    if res := async_response.html.find("p.description", first = True).text:
        await async_session.close()
        return res
    else:
        await async_response.html.arender(sleep=10)
        if  res := async_response.html.find("p.description", first = True).text:
            await async_session.close() 
            return res
        else:
            await async_session.close()
            return "Nothing to retrieve :("

async def get_key_moments(url: str = "https://arxiv.org/abs/2102.12092v2") -> str:
    url = url.replace("abs", "pdf")
    async_session = AsyncHTMLSession()
    async_response = await async_session.get(f"https://labs.kagi.com/ai/sum?url={url}.pdf&expand=1")
    await async_response.html.arender(sleep=5)
    if res := async_response.html.find("p.description", first = True).text:
        await async_session.close() 
        return res
    else:
        await async_response.html.arender(sleep=10)
        if  res := async_response.html.find("p.description", first = True).text:
            await async_session.close()
            return res
        else:
            await async_session.close()
            return "Nothing to retrieve :("