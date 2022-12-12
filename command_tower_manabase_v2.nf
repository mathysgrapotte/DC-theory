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
    tuple path("sources.json"), path("deck_s.csv")

  script:
  """
  land_counter_from_parser.py --deck $deck > sources.json
  mv $deck deck_s.csv
  """

}

process compute_castability {

  input:
    tuple path(sources), path(deck)

  output:
    tuple path("castability.json"), path("deck_c.csv")

  script:
  """
  java -jar ${projectDir}/bin/castability.jar --iterations 250000 --max-mana-value 7 $sources > castability.json
  mv $deck deck_c.csv
  """

}

process manabase_analysis {

  input:
    tuple path(castability), path(deck)

  output:
    path("analysis.csv")

  script:
  """
  manabase_analysis.py --dec $deck --karsten $castability > analysis.csv
  """


}


workflow{
  Channel.of(params.url) \
   | parse_url \
   | find_sources \
   | compute_castability \
   | manabase_analysis \
   | collectFile(name: params.outfile, storeDir: params.outdir)

}
