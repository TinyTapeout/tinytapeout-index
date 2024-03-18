# Tiny Tapeout Index

This repo contains the index of all the Tiny Tapeouts shuttles since TT02. The main index file is [index/index.json](index/index.json). There is also a per-shuttle index file that contains the list of all the projects that have been taped out on that shuttle:

| Shuttle          | Index File                            |
|------------------|---------------------------------------|
| Tiny Tapeout 2   | [index/tt02.json](index/tt02.json)    |
| Tiny Tapeout 3   | [index/tt03.json](index/tt03.json)    |
| Tiny Tapeout 3.5 | [index/tt03p5json](index/tt03p5.json) |
| Tiny Tapeout 4   | [index/tt04.json](index/tt04.json)    |
| Tiny Tapeout 5   | [index/tt05.json](index/tt05.json)    |

You can also find the [JSON schema](schemas/shuttle.schema.json) for the shuttle index files.

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
