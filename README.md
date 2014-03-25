kalpana-export
==============

Export files to different formats. The result is placed in the clipboard.

*Command syntax:* `e<format>[:<chapter>]`

`format` is specified in the config. A format is a list of pairs of strings, with a regex and the replacements. The regex is parsed with the MULTILINE flag, which means that ^ and $ represents the beginning and end of a line.

If the kalpana-chapters plugin is active as well, you can export a single chapter using the `:<chapter>` suffix to the command. `chapter` must be a number of an existing chapter.

All output is stripped of whitespace.

###Example config###

    {
      "format": {
        "test": [
          ["/(.+?)", "<em>\\1</em>"],
          ["^(.+?)$", "<p>\\1</p>"]
        ]
      }
    }