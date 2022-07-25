// Define parameters
params.url = null
params.karsten = "data/karsten_tables.csv"
params.outdir = "results"
params.outfile = "analysis.csv"

// Channels from files
karsten = file(params.karsten)

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

process analysis_karsten {

  input:
    path(deck)

  output:
    path("karsten_analysis.csv")

  script:
  """
  manabase_karsten_analysis.py --dec $deck --karsten $karsten > karsten_analysis.csv
  """
}

/*
 *   Workflow definition
 */

 workflow{
  Channel.of(params.url) \
    | parse_url \
    | analysis_karsten \
    | collectFile(name: params.outfile, storeDir: params.outdir)
}
