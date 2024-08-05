const codelist = [
  {
    value: "00",
    description: "Undefined",
  },
  {
    value: "AA",
    description: "Audio",
  },
  {
    value: "AB",
    description: "Audio cassette",
  },
  {
    value: "AC",
    description: "CD-Audio",
  },
  {
    value: "AD",
    description: "DAT",
  },
  {
    value: "AE",
    description: "Audio disc",
  },
  {
    value: "AF",
    description: "Audio tape",
  },
  {
    value: "AG",
    description: "MiniDisc",
  },
  {
    value: "AH",
    description: "CD-Extra",
  },
  {
    value: "AI",
    description: "DVD Audio",
  },
  {
    value: "AJ",
    description: "Downloadable audio file",
  },
  {
    value: "AK",
    description: "Pre-recorded digital audio player",
  },
  {
    value: "AL",
    description: "Pre-recorded SD card",
  },
  {
    value: "AM",
    description: "LP",
  },
  {
    value: "AN",
    description: "Downloadable and online audio file",
  },
  {
    value: "AO",
    description: "Online audio file",
  },
  {
    value: "AZ",
    description: "Other audio format",
  },
  {
    value: "BA",
    description: "Book",
  },
  {
    value: "BB",
    description: "Hardback",
  },
  {
    value: "BC",
    description: "Paperback / softback",
  },
  {
    value: "BD",
    description: "Loose-leaf",
  },
  {
    value: "BE",
    description: "Spiral bound",
  },
  {
    value: "BF",
    description: "Pamphlet",
  },
  {
    value: "BG",
    description: "Leather / fine binding",
  },
  {
    value: "BH",
    description: "Board book",
  },
  {
    value: "BI",
    description: "Rag book",
  },
  {
    value: "BJ",
    description: "Bath book",
  },
  {
    value: "BK",
    description: "Novelty book",
  },
  {
    value: "BL",
    description: "Slide bound",
  },
  {
    value: "BM",
    description: "Big book",
  },
  {
    value: "BN",
    description: "Part-work (fascículo)",
  },
  {
    value: "BO",
    description: "Fold-out book or chart",
  },
  {
    value: "BP",
    description: "Foam book",
  },
  {
    value: "BZ",
    description: "Other book format",
  },
  {
    value: "CA",
    description: "Sheet map",
  },
  {
    value: "CB",
    description: "Sheet map, folded",
  },
  {
    value: "CC",
    description: "Sheet map, flat",
  },
  {
    value: "CD",
    description: "Sheet map, rolled",
  },
  {
    value: "CE",
    description: "Globe",
  },
  {
    value: "CZ",
    description: "Other cartographic",
  },
  {
    value: "DA",
    description: "Digital (on physical carrier)",
  },
  {
    value: "DB",
    description: "CD-ROM",
  },
  {
    value: "DC",
    description: "CD-I",
  },
  {
    value: "DE",
    description: "Game cartridge",
  },
  {
    value: "DF",
    description: "Diskette",
  },
  {
    value: "DI",
    description: "DVD-ROM",
  },
  {
    value: "DJ",
    description: "Secure Digital (SD) Memory Card",
  },
  {
    value: "DK",
    description: "Compact Flash Memory Card",
  },
  {
    value: "DL",
    description: "Memory Stick Memory Card",
  },
  {
    value: "DM",
    description: "USB Flash Drive",
  },
  {
    value: "DN",
    description: "Double-sided CD/DVD",
  },
  {
    value: "DO",
    description: "BR-ROM",
  },
  {
    value: "DZ",
    description: "Other digital carrier",
  },
  {
    value: "EA",
    description: "Digital (delivered electronically)",
  },
  {
    value: "EB",
    description: "Digital download and online",
  },
  {
    value: "EC",
    description: "Digital online",
  },
  {
    value: "ED",
    description: "Digital download",
  },
  {
    value: "FA",
    description: "Film or transparency",
  },
  {
    value: "FC",
    description: "Slides",
  },
  {
    value: "FD",
    description: "OHP transparencies",
  },
  {
    value: "FE",
    description: "Filmstrip",
  },
  {
    value: "FF",
    description: "Film",
  },
  {
    value: "FZ",
    description: "Other film or transparency format",
  },
  {
    value: "LA",
    description: "Digital product license",
  },
  {
    value: "LB",
    description: "Digital product license key",
  },
  {
    value: "LC",
    description: "Digital product license code",
  },
  {
    value: "MA",
    description: "Microform",
  },
  {
    value: "MB",
    description: "Microfiche",
  },
  {
    value: "MC",
    description: "Microfilm",
  },
  {
    value: "MZ",
    description: "Other microform",
  },
  {
    value: "PA",
    description: "Miscellaneous print",
  },
  {
    value: "PB",
    description: "Address book",
  },
  {
    value: "PC",
    description: "Calendar",
  },
  {
    value: "PD",
    description: "Cards",
  },
  {
    value: "PE",
    description: "Copymasters",
  },
  {
    value: "PF",
    description: "Diary or journal",
  },
  {
    value: "PG",
    description: "Frieze",
  },
  {
    value: "PH",
    description: "Kit",
  },
  {
    value: "PI",
    description: "Sheet music",
  },
  {
    value: "PJ",
    description: "Postcard book or pack",
  },
  {
    value: "PK",
    description: "Poster",
  },
  {
    value: "PL",
    description: "Record book",
  },
  {
    value: "PM",
    description: "Wallet or folder",
  },
  {
    value: "PN",
    description: "Pictures or photographs",
  },
  {
    value: "PO",
    description: "Wallchart",
  },
  {
    value: "PP",
    description: "Stickers",
  },
  {
    value: "PQ",
    description: "Plate (lámina)",
  },
  {
    value: "PR",
    description: "Notebook / blank book",
  },
  {
    value: "PS",
    description: "Organizer",
  },
  {
    value: "PT",
    description: "Bookmark",
  },
  {
    value: "PU",
    description: "Leaflet",
  },
  {
    value: "PV",
    description: "Book plates",
  },
  {
    value: "PZ",
    description: "Other printed item",
  },
  {
    value: "SA",
    description: "Multiple-component retail product",
  },
  {
    value: "SB",
    description: "Multiple-component retail product, boxed",
  },
  {
    value: "SC",
    description: "Multiple-component retail product, slip-cased",
  },
  {
    value: "SD",
    description: "Multiple-component retail product, shrink-wrapped",
  },
  {
    value: "SE",
    description: "Multiple-component retail product, loose",
  },
  {
    value: "SF",
    description: "Multiple-component retail product, part(s) enclosed",
  },
  {
    value: "VA",
    description: "Video",
  },
  {
    value: "VF",
    description: "Videodisc",
  },
  {
    value: "VI",
    description: "DVD video",
  },
  {
    value: "VJ",
    description: "VHS video",
  },
  {
    value: "VK",
    description: "Betamax video",
  },
  {
    value: "VL",
    description: "VCD",
  },
  {
    value: "VM",
    description: "SVCD",
  },
  {
    value: "VN",
    description: "HD DVD",
  },
  {
    value: "VO",
    description: "Blu-ray",
  },
  {
    value: "VP",
    description: "UMD Video",
  },
  {
    value: "VQ",
    description: "CBHD",
  },
  {
    value: "VZ",
    description: "Other video format",
  },
  {
    value: "WW",
    description: "Mixed media product"
  },
  {
    value: "WX",
    description: "Multiple copy pack"
  },
  {
    value: "XA",
    description: "Trade-only material",
  },
  {
    value: "XB",
    description: "Dumpbin – empty",
  },
  {
    value: "XC",
    description: "Dumpbin – filled",
  },
  {
    value: "XD",
    description: "Counterpack – empty",
  },
  {
    value: "XE",
    description: "Counterpack – filled",
  },
  {
    value: "XF",
    description: "Poster, promotional",
  },
  {
    value: "XG",
    description: "Shelf strip",
  },
  {
    value: "XH",
    description: "Window piece",
  },
  {
    value: "XI",
    description: "Streamer",
  },
  {
    value: "XJ",
    description: "Spinner – empty",
  },
  {
    value: "XK",
    description: "Large book display",
  },
  {
    value: "XL",
    description: "Shrink-wrapped pack",
  },
  {
    value: "XM",
    description: "Boxed pack",
  },
  {
    value: "XN",
    description: "Pack (outer packaging unspecified)",
  },
  {
    value: "XO",
    description: "Spinner – filled",
  },
  {
    value: "XY",
    description: "Other point of sale – including retail product",
  },
  {
    value: "XZ",
    description: "Other point of sale",
  },
  {
    value: "ZA",
    description: "General merchandise",
  },
  {
    value: "ZB",
    description: "Doll or figure",
  },
  {
    value: "ZC",
    description: "Soft toy",
  },
  {
    value: "ZD",
    description: "Toy",
  },
  {
    value: "ZE",
    description: "Game",
  },
  {
    value: "ZF",
    description: "T-shirt",
  },
  {
    value: "ZG",
    description: "E-book reader",
  },
  {
    value: "ZH",
    description: "Tablet computer",
  },
  {
    value: "ZI",
    description: "Audiobook player",
  },
  {
    value: "ZJ",
    description: "Jigsaw",
  },
  {
    value: "ZK",
    description: "Mug",
  },
  {
    value: "ZL",
    description: "Tote bag",
  },
  {
    value: "ZM",
    description: "Tableware",
  },
  {
    value: "ZN",
    description: "Umbrella",
  },
  {
    value: "ZO",
    description: "Paints, crayons, pencils",
  },
  {
    value: "ZX",
    description: "Other toy/game accessories",
  },
  {
    value: "ZY",
    description: "Other apparel",
  },
  {
    value: "ZZ",
    description: "Other merchandise",
  }
]

function getCandidateFormat(code) {
  for (let c of codelist) {
    if (c.value == code) return c.description
  }
  return code
}

export { getCandidateFormat }
