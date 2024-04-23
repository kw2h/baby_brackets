import polars as pl
from zipfile import ZipFile

def doc_iter(zip_name: str):
    """ Creating a generator to loop through zip file and
        read in data files one state at a time
    """
    for f in filter(lambda x: x.endswith("TXT"), ZipFile(zip_name).namelist()):
        yield  ZipFile(zip_name).read(f)


def load_names(zip_name: str):
    df_lst = []
    for f in doc_iter(zip_name):
        df = pl.read_csv(
            source=f,
            has_header=False,
            new_columns=["state","sex","year","name","count"]
        )
        df_lst.append(df)
    df_all = pl.concat(df_lst, how="vertical")
    df_all = df_all.group_by(["sex","name"]).agg(pl.col("count").sum()).sort("count", descending=True)
    return df_all


def prefix_search(df_all: pl.DataFrame, query: str, sex: str):
    """ Prefix search based on query + sex and return
        top 10 sorted by descending frequency
    """
    df_q = df_all.filter(pl.col("sex").eq(sex)) if sex else df_all
    df_q = df_q.filter(pl.col("name").str.contains(f"(?i){query}"))
    return df_q.slice(0, 10).to_dicts()


def random_name(df_all: pl.DataFrame, n: int, sex: str):
    """ Return n randome names with a 100,000 minimum count
    """
    df_min = df_all.filter(pl.col("count").gt(100000))
    df_min = df_min.filter(pl.col("sex").eq("M")) if sex else df_min
    return df_min.sample(n).to_dicts()
