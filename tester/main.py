import asyncio
import argparse
import crawler


from crawler import VulnerabilitiesCrawler


def main():
    """
    Tester entry point
    """
    crawler = VulnerabilitiesCrawler('http://web/')
    # Show the obtained information
    print("\n \n >>>>>>>" + crawler.run())


if __name__ == "__main__":
    main()