from datetime import datetime

from prisma_automator.collector import Collector
from prisma_automator.splitter import Splitter


def main():
    """ Time report: program start """
    start = datetime.now()
    time = start.strftime("%H:%M:%S")
    print(f"[$] Program start at {time}.")

    """ Split string generation """
    # Create key word groups
    reality = ["Augmented Reality", "Virtual Reality",
               "Extended Reality || Mixed Reality"]
    goal = ["BCI", "Gaming"]
    other = ["Digital Twin", ""]
    kw_groups = [reality, goal, other]

    # Create a Splitter and add the key word groups
    splitter = Splitter()
    splitter.add_kwgroups(kw_groups)

    # Generate the splits. Results are saved to "./out".
    splits = splitter.split()

    """ Search results collection """
    # Create a Collector
    collector = Collector()

    # Search Scopus using the generated splits. Results are saved to "./out".
    collector.run(splits)

    """ Time report: program end """
    end = datetime.now()
    time = end.strftime("%H:%M:%S")
    difference = end - start
    seconds_in_day = 24 * 60 * 60
    elapsed_time = divmod(
        difference.days * seconds_in_day + difference.seconds, 60)
    print(
        f"[$] Success. Program end at {time}. Elapsed time: {elapsed_time[0]}min and {elapsed_time[1]}s.")


if __name__ == "__main__":
    main()
