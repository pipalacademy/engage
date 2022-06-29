import cProfile
import pstats
from pstats import SortKey

from engage.engage.doctype.problem_repository.problem_repository import update_problems


def run_profile():
    with cProfile.Profile() as pr:
        count = update_problems("generated-problems")
        print(f"{count} problems added/updated")

    ps = pstats.Stats(pr)
    ps.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(topn)

    return pr
