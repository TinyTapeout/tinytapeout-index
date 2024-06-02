# Tiny Tapeout Index

This repo contains the index of all the Tiny Tapeouts shuttles since TT02. The main index file is [index/index.json](index/index.json). There is also a per-shuttle index file that contains the list of all the projects that have been taped out on that shuttle:

| Shuttle          | Index File                             |
|------------------|----------------------------------------|
| Tiny Tapeout 2   | [index/tt02.json](index/tt02.json)     |
| Tiny Tapeout 3   | [index/tt03.json](index/tt03.json)     |
| Tiny Tapeout 3.5 | [index/tt03p5.json](index/tt03p5.json) |
| Tiny Tapeout 4   | [index/tt04.json](index/tt04.json)     |
| Tiny Tapeout 5   | [index/tt05.json](index/tt05.json)     |
| Tiny Tapeout 6   | [index/tt06.json](index/tt06.json)     |
| Tiny Tapeout 7   | [index/tt07.json](index/tt07.json)     |

You can also find the [JSON schema](schemas/shuttle.schema.json) for the shuttle index files.

## API Server

You can access the index files through the API server available at [https://index.tinytapeout.com](https://index.tinytapeout.com).

To access a specific shuttle, just append the shuttle identifier to the URL, followed by `.json`. For example, to access the index file for Tiny Tapeout 4, you can use the following URL: [https://index.tinytapeout.com/tt04.json](https://index.tinytapeout.com/tt04.json).

You can also query specific fields in the index files by using the `fields` query parameter. For example, to get just the repo and address fields for all the projects on Tiny Tapeout 4, you can use the following URL: [https://index.tinytapeout.com/tt04.json?fields=repo,address](https://index.tinytapeout.com/tt04.json?fields=repo,address). The fields should be comma-separated. The "macro" fields is always included in the response.

## Regenerating the Index

To regenerate the index files, run the following commands:

```bash
cd scripts
pip install -r requirements.txt
python update_index <shuttle>
```

Where `<shuttle>` is the identifier of the shuttle (e.g. tt04).

# License

The shuttle index files are licensed under the [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) license.
