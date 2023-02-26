import re
import asyncio
from bs4 import BeautifulSoup
from contextlib import suppress
from aiohttp import ClientSession
from aiogram_dialog import DialogManager
from typing import Any

from db import add_authors_and_paper, add_or_update_paper, check_paper

base_url = "https://engine.scholarcy.com/api/"
extract_url = "metadata/extract"
highlights_url = "highlights/extract"
summarize_endpoint = "https://summarizer.scholarcy.com/summarize"
extract_endpoint = base_url + extract_url
highlights_endpoint = base_url + highlights_url

params = dict(
    external_metadata="false",
    parse_references="false",
    generate_summary="true",
    summary_engine="v4",
    replace_pronouns="false",
    strip_dialogue="false",
    summary_size="400",
    summary_percent="0",
    structured_summary="false",
    keyword_method="sgrank+acr",
    keyword_limit="25",
    abbreviation_method="schwartz",
    extract_claims="true",
    key_points="5",
    citation_contexts="false",
    inline_citation_links="false",
    extract_pico="false",
    extract_tables="false",
    extract_figures="true",
    require_captions="false",
    extract_sections="false",
    unstructured_content="false",
    include_markdown="true",
    extract_snippets="true",
    engine="v2",
    image_engine="v1+v2"
)

async def get_summary(cross_data: Any, 
                      paper_id: str,
                      paper_url: str,
                      synopsys=False,
                      highlights=True,
                      context_id: str = "qwe"):

    async def fetch_summary(paper_url: str, synopsys=False, highlights=False):
        pdf_url = paper_url.replace("abs", "pdf") + ".pdf"
        if highlights:
            url = highlights_endpoint
        else:
            url = extract_endpoint
        if synopsys:
            url = summarize_endpoint
        params["url"] = pdf_url
        async with ClientSession() as session:
            async with await session.get(url, params=params) as response:
                if response.ok:
                    data = await response.json()
                    if data.get("response"):
                        return data["response"]
                    else:
                        return data
                else:
                    try:
                        data = {"code_error": response.status,
                                "message": (await response.json()).get("message")}
                        return data
                    except Exception as e:
                        data = {"code_error": response.status,
                                "message": e}
                        return data

    if paper := await check_paper(paper_id):
        if paper.highlights:
            data = {
                "id": paper.id_,
                "title": paper.title,
                "abstract": paper.abstract,
                "highlights": paper.highlights,
                "findings": paper.findings,
                "summary": paper.summary,
                "figures_url": paper.figures_url,
                "full_data": paper.full_data,
                # "authors": paper.authors,
            }
        else:
            data = await fetch_summary(paper_url, synopsys, highlights)
            if not data.get("code_error"):
                await add_or_update_paper(paper_id, data)
                data["id"] = paper.id_
                data["title"] = paper.title
                data["abstract"] = paper.abstract
                # data["authors"] = paper.authors
    else:
        data = await fetch_summary(paper_url, synopsys, highlights)
        if data.get("metadata"):
            data["authors"] = data["metadata"].get("author").split(",").strip()
            data["title"] = data["metadata"].get('title')
            data["abstract"] = data["metadata"].get("abstract")
            await add_authors_and_paper(paper_id, data)

    # await asyncio.sleep(1)
    cross_data.intent_queue[context_id] = "done"
    cross_data.context[context_id].dialog_data.update(data)

    return




async def get_paper_desc(id_paper: str) -> dict | None:
    if paper_ := await check_paper(id_paper):
        paper = {
            "id_" : paper_.id_,
            "url" : f"https://arxiv.org/abs/{paper_.id_}",
            "title" : paper_.title,
            "abstract" : paper_.abstract,
            "authors": None
        }
        return paper
    else:
        async with ClientSession() as session:
            async with await session.get(f'https://arxiv.org/abs/{id_paper}') as request:
                if request.ok:
                    soup = BeautifulSoup(await request.text(), features="xml")
                    try:
                        url = soup.find('meta', property='og:url').get('content') # type: ignore
                        paper = {
                        "id_": re.findall(r'arxiv.org\/(?:abs|pdf)\/(\d{4}\.\d{5}[v]?[\d]?)', url)[0], # type: ignore
                        "url" : url,  # type: ignore
                        "title" : soup.find('meta', property='og:title').get('content'), # type: ignore
                        "abstract" : soup.find('meta', property='og:description').get('content').replace('\n', ' '), # type: ignore
                        "authors" : [name.text for name in soup.find("div", class_="authors").find_all("a")] # type: ignore
                        }
                        await add_authors_and_paper(paper["id_"], paper)
                        return paper
                    except TypeError:
                        pass
    return None

