def parse_csv(csv_file):
    import csv

    with open(csv_file, "rt") as f:
        try:
            sniffer = csv.Sniffer()
            if not sniffer.has_header(f.read(4096)):
                raise RuntimeError("could not find CSV header in {}".format(csv_file))
        except csv.Error:
            raise
        else:
            f.seek(0)

        # automatically make a dict using the header row
        reader = csv.DictReader(f)
        yield from reader
