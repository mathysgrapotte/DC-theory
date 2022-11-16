// define parameters
params.url = null
params.outdir = "results"
params.outfile = "analysis.csv"

process parse_url {

  input:
    val(url)

  output:
    path("parsed.csv")

  script:
  """
  parser.py --mox $url > parsed.csv
  """

}

process find_sources {

  input:
    path(deck)

  output:
    path("sources.json")

  script:
  """
  land_counter_from_parser.py --deck $deck > sources.json
  """

}

process compute_castability {

  input:
    path(sources)

  output:
    path("castability.json")

  script:
  """
  castability.sh $sources > castability.json
  """

}



workflow{
  Channel.of(params.url) \
   | parse_url \
   | find_sources \
   | compute_castability \
   | collectFile(name: params.outfile, storeDir: params.outdir)

}
