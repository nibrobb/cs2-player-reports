from enum import StrEnum
from typing import Literal
import argparse
import bs4
from bs4 import BeautifulSoup
from dataclasses import dataclass, field

import json
import os
import requests
import logging

logger = logging.getLogger("main")


class ReportReason(StrEnum):
    OTHER_HACKING = "Other Hacking"
    AIM_HACKING = "Aim Hacking"
    WALL_HACKING = "Wall Hacking"


@dataclass
class Profiles:
    report_reason: ReportReason
    nickname: str
    profile_link: str
    steam_id: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Profiles):
            return self.steam_id == other.steam_id
        return False

    def __hash__(self) -> int:
        return hash(self.steam_id)


@dataclass
class SteamAPIResponseInner:
    success: Literal[1, 42] = field()
    steamid: str = field()
    message: str | None = field(default=None)


def get_steamid64(vanity_url: str) -> str:
    api_base = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    key = os.environ.get("API_KEY")
    assert key is not None, "Missing API key"

    response = requests.get(api_base, params={"key": key, "vanityurl": vanity_url})
    if not response.ok:
        raise ValueError("Did not get a 200 OK")

    content = json.loads(response.content)
    content_response = content["response"]
    steam_api_response = SteamAPIResponseInner(**content_response)
    if steam_api_response.steamid is None:
        raise ValueError("Error getting steam id")
    return steam_api_response.steamid


def parse_dump(soup_tag: bs4.element.Tag, use_api: bool = False) -> set[Profiles]:
    cheaters: set[Profiles] = set()
    checked_profiles = set()

    rows = soup_tag.table.tbody.find_all("tr")  # type: ignore[attribute]
    for tr in rows:
        for nick in tr.find_all(class_="playerNickname"):
            for item in tr.find_all("li"):
                for s in item.stripped_strings:
                    if s in (ReportReason.OTHER_HACKING, ReportReason.AIM_HACKING):
                        link_title = nick.find("a", class_="linkTitle")
                        report_reason = s
                        profile_link = str(link_title["href"])
                        if profile_link in checked_profiles:
                            continue
                        nickname = str(link_title.contents[0]).strip()  # type: ignore

                        if profile_link.startswith("https://steamcommunity.com/id/"):
                            vanity_url = profile_link.split(
                                "https://steamcommunity.com/id/"
                            )[-1]
                            steam_id = (
                                get_steamid64(vanity_url) if use_api else "NOT_FETCHED"
                            )
                        elif profile_link.startswith(
                            "https://steamcommunity.com/profiles/"
                        ):
                            steam_id = profile_link.split(
                                "https://steamcommunity.com/profiles/"
                            )[-1]
                        else:
                            steam_id = "Could not find or get Steam ID"

                        cheaters.add(
                            Profiles(
                                report_reason=ReportReason(report_reason),
                                nickname=str(nickname),
                                profile_link=str(profile_link),  # type: ignore
                                steam_id=steam_id,
                            )
                        )
                        logger.debug(f"{steam_id:>17} {profile_link:<64} {nickname}")
    return cheaters


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="verbose mode, show more info",
    )
    parser.add_argument(
        "--input",
        default="data/reports.html",
        required=False,
        help="the input file `path/to/reports.html` [DEFAULT=data/reports.html]",
    )
    parser.add_argument(
        "--output",
        default="output/output.json",
        required=False,
        help="the output file `path/to/output.json` [DEFAULT=output/output.json]",
    )
    parser.add_argument(
        "--no-api",
        default=False,
        action="store_true",
        required=False,
        help="set this flag if you DO NOT wish to use the Steam API to lookup accounts Steam IDs",
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "text"],
        required=False,
        help="the output format [DEFAULT=json]",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    verbose: bool = args.verbose
    if verbose:
        logger.setLevel(logging.DEBUG)
    infile: str = args.input
    outfile: str = args.output
    use_api: bool = not args.no_api
    output_format: Literal["json", "text"] = args.format

    with open(infile, "r") as reports:
        soup = BeautifulSoup(reports, "html.parser")
        personaldata_elements_container = soup.find(
            id="personaldata_elements_container"
        )

        if not personaldata_elements_container:
            raise RuntimeError(
                "Could not find element `personaldata_elements_container`"
            )

        cheaters = parse_dump(personaldata_elements_container, use_api)

        if output_format == "json":
            # Create the parent directories if neccecary
            os.makedirs(os.path.dirname(outfile), exist_ok=True)
            with open(outfile, "w") as out_fp:
                out_json = json.dumps(
                    list(cheaters),
                    default=lambda o: o.__dict__,
                    sort_keys=True,
                    indent=4,
                )
                out_fp.write(out_json)
        elif output_format == "text":
            with open(outfile, "w") as out_fp:
                for cheater in cheaters:
                    out_fp.write(cheater.profile_link + "\n")

        logger.info(f"Found {len(cheaters)} reported cheaters")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
