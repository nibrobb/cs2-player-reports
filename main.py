from enum import StrEnum
from typing import Literal

from bs4 import BeautifulSoup
from dataclasses import dataclass, field

import json
import os
import requests


class ReportReason(StrEnum):
    OTHER_HACKING = "Other Hacking"
    AIM_HACKING = "Aim Hacking"


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
class SteamAPIResponseInner(json.JSONDecoder):
    success: Literal[1, 42] = field()
    steamid: str | None = field(default=None)
    message: str | None = field(default=None)


def get_steamid64(nickname: str) -> SteamAPIResponseInner:
    api_base = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    key = os.environ.get("API_KEY")
    assert key is not None, "Missing API key"

    response = requests.get(api_base, params={"key": key, "vanityurl": nickname})
    if not response.ok:
        raise ValueError("Did not get a 200 OK")

    shiet = json.loads(response.content)
    inner_shiet = shiet["response"]
    return SteamAPIResponseInner(**inner_shiet)


def main():
    with open("data/reports.html", "r") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        personaldata_elements_container = soup.find(
            id="personaldata_elements_container"
        )

        cheaters: set[Profiles] = set()

        if personaldata_elements_container:
            rows = personaldata_elements_container.table.tbody.find_all("tr")  # type: ignore
            for tr in rows:
                for nick in tr.find_all(class_="playerNickname"):
                    for item in tr.find_all("li"):
                        for s in item.stripped_strings:
                            if s in ("Other Hacking", "Aim Hacking"):
                                link_title = nick.find("a", class_="linkTitle")
                                report_reason = s
                                profile_link = str(link_title["href"])  # type: ignore
                                nickname = str(link_title.contents[0]).strip()  # type: ignore

                                vanity_url = profile_link.split(
                                    "https://steamcommunity.com/id/"
                                )
                                profiles_split = profile_link.split(
                                    "https://steamcommunity.com/profiles/"
                                )

                                if len(profiles_split) == 2:
                                    steam_id = profiles_split[-1]
                                elif len(vanity_url) == 2:
                                    steam_id = get_steamid64(vanity_url[-1]).steamid
                                else:
                                    # Should be unreachable (if not rate limited or something)
                                    steam_id = None

                                cheaters.add(
                                    Profiles(
                                        report_reason=ReportReason(report_reason),
                                        nickname=str(nickname),
                                        profile_link=str(profile_link),  # type: ignore
                                        steam_id=steam_id or "Could not get Steam ID",
                                    )
                                )
                                print(f"[DEBUG] {steam_id} {profile_link} {nickname}")

        print(len(cheaters))
        with open("output.json", "w") as fp:
            out = json.dumps(
                list(cheaters),
                default=lambda o: o.__dict__,
                sort_keys=True,
                indent=4,
            )
            fp.write(out)


if __name__ == "__main__":
    main()
