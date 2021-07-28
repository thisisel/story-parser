import logging
import os
from typing import List

from tortoise import Tortoise, run_async

from stories.dict.the_eyes import corpus as the_eyes_corpus
from models import StoryPieceModel, StoryReward

logging.basicConfig(
    level=logging.DEBUG,
    filename="sample.log",
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_url = "sqlite:///" + os.path.join(basedir, "story.sqlite")


def split_tokenizer(corpus: str) -> List[str]:
    return corpus.split()


def make_segments(splitted_corpus: List[str], fixed_segment_size: int = 50):

    total_word_count = len(splitted_corpus)
    segments: List[str] = []
    segments_obj = List[StoryPieceModel]

    for i in range(0, total_word_count, fixed_segment_size):

        segment_words: List[str] = splitted_corpus[i : fixed_segment_size + i]
        current_segment_text: str = " ".join(segment_words)

        segments.append(current_segment_text)
        if len(segment_words) < fixed_segment_size:

            logger.info(f"last segment before merge >>>>> {current_segment_text}")

            n = len(segment_words)
            logger.info(f"has residue => needs {fixed_segment_size - n} more words")

            segments.pop()
            last_segment_merge: str = segments.pop()

            logger.info(
                f"last segment after merge >>>>> {last_segment_merge} {current_segment_text}"
            )

            segments.append(f"{last_segment_merge} {current_segment_text}")


def prep_piece_models(
    splitted_corpus: List[str],
    story_obj: StoryReward = None,
    fixed_segment_size: int = 50,
):

    if story_obj is None:
        logger.info("Story is not inserted")

    total_word_count = len(splitted_corpus)
    pieces: List[StoryPieceModel] = []
    piece_num = 1

    for i in range(0, total_word_count, fixed_segment_size):

        segment_words: List[str] = splitted_corpus[i : fixed_segment_size + i]
        current_segment_text: str = " ".join(segment_words)

        current_piece = StoryPieceModel(
            content=current_segment_text,
            word_count=len(segment_words),
            piece_num=piece_num,
        )
        pieces.append(current_piece)
        piece_num += 1

    # fix last part residue
    last_piece = pieces[-1]
    if last_piece.word_count < fixed_segment_size:
        pieces.pop()
        new_last_piece = pieces.pop()
        new_last_piece.word_count = new_last_piece.word_count + last_piece.word_count
        new_last_piece.content = f"{new_last_piece.content} {last_piece.content}"
        pieces.append(new_last_piece)

    logger.info("END making pieces")
    return pieces


def get_story_tag(word_count: int) -> str:
    FLASH_FICTION = "flash-fiction"
    SHORT_STORY = "short-story"
    NOVELETTE = "novelette"
    NOVELLA = "novella"

    tag: str

    if word_count < 1000:
        tag = FLASH_FICTION
    if word_count in range(1000, 7500):
        tag = SHORT_STORY
    elif word_count in range(7500, 10000):
        tag = NOVELETTE
    else:
        tag = NOVELLA

    logger.info(f"END Tag is {tag}")
    return tag


def prep_story_model(author: str, title: str, splitted_corpus: List[str]):

    story_word_count = len(splitted_corpus)
    tag = get_story_tag(story_word_count)
    story_obj = StoryReward(
        tag=tag, author=author, title=title, word_count=story_word_count
    )

    logger.info("END preping models")

    return story_obj

def read_corpus():
    with open("raw.txt", "r") as f:
        t = f.read()
        return t

async def run():
    await Tortoise.init(db_url=db_url, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

    c = read_corpus()
    splitted_corpus = split_tokenizer(corpus=c)
    
    story_obj = prep_story_model(
        author="philip", title="eyes", splitted_corpus=splitted_corpus
    )

    await story_obj.save()

    pieces_list_obj = prep_piece_models(
        splitted_corpus=splitted_corpus, story_obj=story_obj
    )

    try:
        for piece in pieces_list_obj:
            piece.story = story_obj
            await piece.save()

        logger.info("SUCCESS")

        story_obj.saved_pieces_count = pieces_list_obj[-1].piece_num
        await story_obj.save()

        logger.info("SUCCESS updated saved_pierces_count")

    except Exception as exe:
        logger.error(msg=exe)


if __name__ == "__main__":
    run_async(run())
