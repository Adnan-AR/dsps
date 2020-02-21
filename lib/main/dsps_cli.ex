defmodule DSPS.CLI do
  @moduledoc"""
  Main function of the dsps system
  """

  @doc """
  Implementation of Main function
  """
  def main(args \\ []) do
    # Read arguments
    args
    |> parse_args
    |> response
    |> IO.puts()
    # Parse the config yaml file
    {:ok, config_params} = Path.join(
      File.cwd!(), "config/node_config.yml") |> YamlElixir.read_from_file
    # Get name
    node_name = Map.get(config_params, "node.name") |> String.to_atom
    # Rename node
    :net_kernel.start([node_name, :longnames])
    # Set cookie (Cluster name in our case)
    Map.get(config_params, "cookie.name")
    |> String.to_atom
    |> Node.set_cookie
    run(:help)
    
  end

  # Parse Command line arguments
  defp parse_args(args) do
    {opts, word, _} =
      args
      |> OptionParser.parse(switches: [upcase: :boolean])

    {opts, List.to_string(word)}
  end

  # Responce to the command line
  defp response({opts, word}) do
    if opts[:upcase], do: String.upcase(word), else: word
  end

  # Parse configuration file
  def parse_config(path), do: YamlElixir.read_from_file(path)
  
  # Run the application
  defp run(:help) do
    Bunt.puts [:steelblue, """
      Run the Elixir Linter engine from the command line by typing elixir_linter --lint 
      where the repo name is formatted like this: 'owner/repo_name`.
    """]
  end

end
