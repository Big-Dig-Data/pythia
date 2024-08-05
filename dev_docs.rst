Marc fields of interest
-----------------------

008 - fixed length general info
      char 35-37 - language code e.g. "060401d19511975ja ur p       0    |eng||"


080 - universal decimal classification number
      a - the number itself
      2 - edition of the numbering system

      e.g.::
        <marc:subfield code="a">621.38/.39</marc:subfield>
        <marc:subfield code="2">MRF</marc:subfield>

100 - author
      a - personal name
      4 - relationship https://www.loc.gov/marc/relators/relaterm.html
          'aut' == author
          'dis' == dissertant
          'ths' == thesis advisor
          'edt' == editor
          'com' == compiler
          'trl' == translator
          'aui' == author of introduction
          'ill' == illustrator
          'oth' == other
          'pht' == photographer
          'art' == artist
          'cwt' == commentator for written text

245 - title
      a - main title
      b - remainder of title
      c - statement of responsibility

650 - categorization
      a - category
      2 - source of heading or term

653, 655 - podobný 650

700 - related person names
      a - name
      4 - relationship
      d - dates associated with name

710 - related corporate names
      a - corporate name
      b - unit
      4 - relationship - similar to author, but some extra values there:

          pbl = publisher
          spn = sponsor
          orm = organizer
          prt = printer
