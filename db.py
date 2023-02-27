import asyncio
from sqlmodel import Field, SQLModel, create_engine, Relationship, select, Session, JSON, Column
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as _AsyncSession
from sqlalchemy.orm import selectinload


async_sqlite_url = "sqlite+aiosqlite:///papers.db"
echo = False

async_engine = create_async_engine(async_sqlite_url, echo=echo)
engine = create_engine("sqlite:///papers.db", echo=echo)


# models
class Papers2Authors(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    paper_id: int | None = Field(default=None, primary_key=True, foreign_key="papers.id_")
    author_id: int | None = Field(default=None, primary_key=True, foreign_key="authors.id_")


class Authors(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id_: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    papers: list["Papers"] = Relationship(back_populates="authors", link_model=Papers2Authors)


class Papers(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id_: str = Field(primary_key=True)
    title: str
    abstract: str
    highlights: list[str] | None = Field(default=None, sa_column=Column(JSON))
    findings: list[str] | None = Field(default=None, sa_column=Column(JSON))
    summary: list[str] | None = Field(default=None, sa_column=Column(JSON))
    figures_url: list[str] | None = Field(default=None, sa_column=Column(JSON))
    full_data: dict | None = Field(default=None, sa_column=Column(JSON))
    authors: list["Authors"] | None = Relationship(back_populates="papers", link_model=Papers2Authors)
    class Config:
        arbitrary_types_allowed = True


def create_db():
    engine = create_engine("sqlite:///papers.db", echo=True)
    SQLModel.metadata.create_all(engine, checkfirst=True)


# CRUD
def add_authors_to_paper(id_, paper: dict, authors):
    authors = [Authors(name=name) for name in authors]
    with Session(engine) as session:
        paper_ = session.get(Papers, id_)
        if paper_:
            if paper_.authors:
                paper_.authors.extend(authors)
                session.add(paper_)
                session.commit()
            else:
                print("OOOOPS")
        else:
            print('OOOPS')


async def add_authors_and_paper(id_: str, paper: dict):
    if await check_paper(id_):
        return

    if authors := paper.get("authors"):
        paper_ = Papers(
            id_ = id_,
            title = paper["title"],
            abstract = paper["abstract"],
            highlights = paper.get("highlights"),
            summary = paper.get("summary"),
            figures_url = paper.get("figures_url"),
            findings = paper.get("findings"),
            full_data = paper.get("full_data") if paper.get("full_data") else paper
        )
        async with AsyncSession(async_engine, expire_on_commit=False) as session:
            queries = [select(Authors).where(Authors.name==name).
                       options(selectinload(Authors.papers))
                       for name in authors]
            results = await asyncio.gather(*[session.exec(query) for query in queries]) # type: ignore
            exist_authors = [author for res in results if (author:=res.first())]
            exist_names = [author.name for author in exist_authors if author]
            [author.papers.append(paper_) for author in exist_authors]
            session.add_all(exist_authors)
            new_authors = [author for author in authors if author not in exist_names]
            new_authors = [Authors(name=name, papers=[paper_]) for name in new_authors]
            session.add_all(new_authors)
            await session.commit()
    else:
        await add_or_update_paper(id_, paper)


def add_paper_to_authors(id_, paper, authors): 
    paper_ = Papers(
            id_ = id_,
            title = paper["title"],
            abstract = paper["abstract"],
            highlights = paper.get("highlights"),
            summary = paper.get("summary"),
            figures_url = paper.get("figures_url"),
            findings = paper.get("findings"),
            full_data = paper.get("full_data") if paper.get("full_data") else paper
    )
    with Session(engine, expire_on_commit=False) as session:
        queries = [select(Authors).where(Authors.name==name) for name in authors]
        results = [session.exec(query) for query in queries]
        exist_authors = [author for author in [author.first() for author in results] if author]
        [author.papers.append(paper_) for author in exist_authors]
        session.add_all(exist_authors)
        session.commit()


async def check_paper(id_: str, async_engine=async_engine):
    async with AsyncSession(async_engine) as session:
        return await session.get(Papers, id_)


async def add_or_update_paper(id_:str, paper: dict, async_engine = async_engine):
    if exists_paper := await check_paper(id_):
        paper_ = exists_paper
        paper_.highlights = paper.get("highlights")
        paper_.summary = paper.get("summary")
        paper_.findings = paper.get("findings")
        paper_.figures_url = paper.get("figures_url")
        paper_.full_data = paper.get("full_data") if paper.get("full_data") else paper
    else:
        paper_ = Papers(
            id_ = id_,
            title = paper["title"],
            abstract = paper["abstract"],
            highlights = paper.get("highlights"),
            summary = paper.get("summary"),
            figures_url = paper.get("figures_url"),
            findings = paper.get("findings"),
            full_data = paper.get("full_data") if paper.get("full_data") else paper
            )
    async with AsyncSession(async_engine) as session:
        session.add(paper_)
        await session.commit()




if __name__ == "__main__":
    import json
    with open("paper.json", 'r') as file:
        paper = json.load(file)
    paper["title"] = paper["metadata"]["title"]
    paper["authors"] = paper["metadata"]["author"].split(",").strip()
    paper["abstract"] = paper["metadata"]["abstract"]
    create_db()

    async def main():
        await add_authors_and_paper("2203.02155v1", paper)
    asyncio.run(main())
