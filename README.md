[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/imnotripper/passport-page-imaginary-country/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/imnotripper/passport-page-imaginary-country/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

An open passport spread for the **Republic of Velmora** — a small Adriatic
coastal republic whose capital is Port Alver — built for the
[make.fun bounty](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

`main.py` writes one image to `/output/entry.png`: the data page of Mara
Ileana Selvane (born 12 Mar 1994 in Port Alver; passport VM 0418827, issued
14 Jun 2021, valid to 14 Jun 2031) beside the visas page of her travels —
Dravostan in September 2022, Kessar in May 2023, and the Isles of Tarn by
ferry in November 2024. Every stamp falls after the passport's issue date,
and the red visa-condition stamp tells you what kind of place Velmora is:
entry is valid for the coastal districts only, and the mountainous interior
needs a Ministry permit. The ferry tax was paid: 12 vel.

The spread is drawn in code (`build_spread.py`, PIL) around a generated ID
portrait, so every date, name and MRZ check digit agrees with the others.
