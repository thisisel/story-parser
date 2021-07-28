import logging
from models import StoryPieceModel, StoryReward
import os
from tortoise.query_utils import Q
from tortoise import Tortoise, run_async

logging.basicConfig(
    level=logging.DEBUG,
    filename="sample.log",
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_url = "sqlite:///" + os.path.join(basedir, "fake-story.sqlite")


class StoryManager:

    PIECE_SIZE: int = 50
    
    # rm
    words_per_page = [i for i in range(300, 99, -50)]
    fetch_window = [(i, int(i / 50)) for i in words_per_page]

    default_durations = {i * 10 for i in range(1, 10)}
    find_words_per_page = {
        10: 300,
        20: 300,
        30: 250,
        40: 200,
        50: 200,
        60: 150,
        70: 100,
        80: 100,
        90: 100,
    }
    pieces_to_get = lambda words, piece_size: int(words / piece_size)

    piece_boundary_filters = {
        10: {Q(saved_pieces_count__gte=60), Q(saved_pieces_count__lt=150)},
        20: {Q(saved_pieces_count__gte=60), Q(saved_pieces_count__lt=150)},
        30: {Q(saved_pieces_count__gte=150), Q(saved_pieces_count__lt=160)},
        40: {Q(saved_pieces_count__gte=160), Q(saved_pieces_count__lt=200)},
        50: {Q(saved_pieces_count__gte=200)},
        60: {Q(saved_pieces_count__gte=180), Q(saved_pieces_count__lt=200)},
        70: {Q(saved_pieces_count__gte=140), Q(saved_pieces_count__lt=160)},
        80: {Q(saved_pieces_count__gte=160), Q(saved_pieces_count__lt=180)},
        90: {Q(saved_pieces_count__gte=180), Q(saved_pieces_count__lt=200)},
    }

    @classmethod
    def dispatch_story(cls, duration: int):
        filters = cls.piece_boundary_filters.get(duration, None)

        if duration not in cls.default_durations:
            raise Exception(
                f"Invalid Duration {duration}\nValid duration Must be in : {cls.default_durations}"
            )

        if filters is None:
            raise Exception("Filter Not Found")

        story_qset = StoryReward.filter(*filters, join_type="AND").first()
        return story_qset

    # assumption : story never runs out of page words
    @classmethod
    def arrange_story(cls, story_id: int, page_num: int, duration: int):

        if (words := cls.find_words_per_page.get(duration, None)) is None:
            raise Exception(
                f"Invalid duration. Duration must be in {cls.default_durations}"
            )

        challenge_over = False

        if page_num > duration:
            raise Exception(f"Over insert")

        if page_num == duration:
            challenge_over = True

        window = cls.pieces_to_get(words=words, piece_size=50)
        
        finish_piece_num = page_num * window
        start_piece_num = finish_piece_num - window + 1
        idx_filters = [Q(piece_num__gte=start_piece_num), Q(piece_num__lte=finish_piece_num)]
        
        if challenge_over:
            del idx_filters [-1]
        
        return idx_filters


async def dispatch(duration: int):
    await Tortoise.init(db_url=db_url, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

    q_set = StoryManager.dispatch_story(duration=d)
    story = await q_set

    if story is None:
        print(f"No story found for the given duration={duration}")
        return

    print(story.__str__())


async def arrange(story_id: int, page_num: int, duration: int):
    await Tortoise.init(db_url=db_url, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

    idx_filters = StoryManager.arrange_story(
        story_id=story_id, page_num=page_num, duration=duration
    )   
    s = await StoryReward.filter(Q(id=story_id)).first()
    ps = await StoryPieceModel.filter(Q(story_id=story_id), *idx_filters).all()
    
    print("---story---")
    print(s.__str__())
    print("---pieces---")
    for p in ps:
        print(p.__str__())
        print(p.content)

    print(f"total pieces = {len(ps)}")

if __name__ == "__main__":

    exit = False
    while not exit:
        option = int(input(f"1. Dispatch Story\n2. Arrange Story Pieces\n3. exit\n"))

        if option == 1:
            d = int(input("enter duration\n"))
            run_async(dispatch(duration=d))

        elif option == 2:
            s_id = int(input("enter story id\n"))
            d = int(input("enter duration\n"))
            p = int(input("enter page num\n"))
            run_async(arrange(story_id=s_id, page_num=p, duration=d))

        elif option == 3:
            exit = True

        else:
            print("Invalid option entered")
