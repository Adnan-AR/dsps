defmodule Dsps.MixProject do
  use Mix.Project

  def project do
    [
      app: :dsps,
      version: "0.1.0",
      elixir: "~> 1.9",
      elixirc_paths: elixirc_paths(Mix.env),
      build_embedded: Mix.env == :prod,
      start_permanent: Mix.env == :prod,
      deps: deps(),
      escript: escript(), # to build executable application (REMOVE)

      # Release 
      releases: [
	dsps: [
	  applications: [runtime_tools: :permanent],
	  # Add runtime configuration (provide path to YAML file)
	  config_providers: [
	    {ConfigHandler, System.get_env("NODE_CONFIG_PATH")}
	  ]
	]
      ]
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      mod: {Node.Starter, []},
      extra_applications: [:logger]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:csv, "~> 2.3"},
      {:uuid, "~> 1.1"},
      {:fast_ngram, "~> 1.0"},
      {:erlport, "~> 0.10.1"},
      {:cowboy, "~> 1.0.0"},
      {:poison, "~> 3.1"},
      {:yaml_elixir, "~> 2.4.0"}
    ]
  end

  # Launch DSPS command line
  defp escript, do: [main_module: DSPS.CLI]
  
  # Add dependecies paths depending on build env
  defp elixirc_paths(:test), do: ["lib","test/fake"]
  defp elixirc_paths(_), do: ["lib"]

end
