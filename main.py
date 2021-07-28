import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI(title="StoryParser", debug=True)

basedir = os.path.abspath(os.path.dirname(__file__))
db_url = "sqlite:///" + os.path.join(basedir, "story.sqlite")
register_tortoise(
    app,
    db_url=db_url,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)