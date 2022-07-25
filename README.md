# CRIPixiv

Simple command-line tool to help with getting RAWs from comic.pixiv.net.

## Dependencies

Using pip:
```sh
$ pip install numpy xmltodict
```

## Running

Provide a `./config.json` file of the following format:
```json
{
    "first_page_link": URL as string from first request (one that returns XML),
    "first_page_index": first page number also present in the first_page_link,
    "last_page_index": last page number,
    "cookie": long encrypted-looking cookie starting with `dist-`
}
```

Then just run
```sh
$ python main.py
```

The script will take a while to finish due to rate limitations.
